"""Simulate running commands like a user would in a terminal

@Dane, This code is completley independent of "atuin"
"""
import logging
from pathlib import Path
import subprocess
import sys
import time
import pexpect
from liminal.logging import LOGGER


TEST_COMMAND_PREFIX = 'logger "liminal_test'
_SHELL_STARTUP_TIMEOUT_SECONDS = 5

class PS1ParseException(Exception):
	pass


def _wait_for_shell_startup(process: pexpect.spawn, timeout_seconds=_SHELL_STARTUP_TIMEOUT_SECONDS):
	LOGGER.debug(f'waiting {timeout_seconds}s for output to stabilize/finish')
	last_content = None
	iter_time = 0.1
	max_iterations = timeout_seconds / iter_time
	i = 0

	while i < max_iterations:
		i += 1
		time.sleep(iter_time)
		try:
			content = process.read_nonblocking(size=1024, timeout=1)
		except pexpect.TIMEOUT:
			# this seems to be ok, it fails to read a new character, so output is done
			break
		if content == last_content:
			break
		last_content = content
	LOGGER.debug(f'waited for {i}/{max_iterations}')



def run_test_login_command(shell_exec_path: str | Path, key: str) -> str:
	"""Run a test command in a login shell with a unique key for tracking

	This simulates what a real user would experience
	"""
	full_cmd = f'{TEST_COMMAND_PREFIX} {key}"'
	output = run_login_command(str(shell_exec_path), full_cmd, log_message_prefix='Running test command\n\t$ ')
	LOGGER.debug(f'{output=}')	
	return full_cmd

def debug_shell_startup(shell_exec_path: str,) -> str | None:
	try:
		child = pexpect.spawn(
			f'{shell_exec_path} -x -l', encoding='utf-8', dimensions=(111, 444), 
			# env={'PS4': '+lmdebug+'},
			timeout=6,
		)
		time.sleep(3)
		output = child.read_nonblocking(size=1024, timeout=2)
		LOGGER.debug(f'shell startup output:\n{output}')
		return output
	except Exception as e:
		LOGGER.debug('failed to get shell startup output', exc_info=True)


def run_login_command(shell_exec_path: str, cmd: str, timeout_seconds=3, log_message_prefix=''):
	"""Simulate a real user spawned process (pexpect) and a login shell (`shell_command`)

	this seems to be the only way to run a command from python and have atuin record it

	since a login shell can do anything on startup for the first time, along with a user's custom PS1, it is hard to confirm
	we have actually ran a command and gotten its correct output. For example, oakland's HPC will give a message 
	about billing that contains lots of text and special chars, and takes 5-10 seconds to finish outputing, so you can't
	just run a command right after spawning the login shell
	
	subprocess.run(['bash', '-ic', 'mycommand; exit']) doesnt work
		# resp = subprocess.run(['bash', '-ic', f'logger "liminal installed {datetime_utcnow()} {uuid4()}"'])
		resp = subprocess.run(['bash', '-ic', f'eval "$(atuin init bash)"; echo pleaseeee; true; exit 0'], cwd=Path(__file__).parent.parent, env=None)

	other potential strategies: 
		- send noop, diff before and after content to determine PS1
		- check if there is a way to do it with `-c` and still get atuin to work, maybe just needs proper env vars
	"""

	shell_command = f"{shell_exec_path} -l"
	LOGGER.info(f"{log_message_prefix}{shell_exec_path} -l '{cmd}'", stacklevel=2)
	
	shell_exit_timeout_seconds = 2
	command_timeout_in_seconds = timeout_seconds
	max_process_duration_seconds =  (
		2 # some extra padding for the overhead of code
		+ _SHELL_STARTUP_TIMEOUT_SECONDS + command_timeout_in_seconds + shell_exit_timeout_seconds
	)

	child = pexpect.spawn(
		shell_command,
		encoding='utf-8', timeout=max_process_duration_seconds,
		# maxread=1,
		echo=False,
		dimensions=(111, 444) # WARNING: this is important, if not large enough, text will be truncated, causing matches to fail
	)
	# child.delaybeforesend = 0.1 # maybe this will help with unexpected timeouts/matches
	# child.logfile = sys.stdout # use sys.stdout to more easily debug (see output as it is occuring)

	try:
		_wait_for_shell_startup(child)
	except pexpect.TIMEOUT:
		LOGGER.error('Shell startup exceeded timeout')
		raise

	# now the shell should be ready to run a command (and not outputing various startup/welcome message stuff)
	try:
		child.sendline(cmd)
		try:
			_ = child.read_nonblocking(size=1024, timeout=command_timeout_in_seconds)
		except pexpect.TIMEOUT:
			# this exception seems to be ok/benign. it fails to read a new character, so no more output is occuring
			pass
		else:
			time.sleep(command_timeout_in_seconds) 
			# TODO: child.read_nonblocking doesn't do anything with echo=False
		raw_cmd_output = child.before
		return raw_cmd_output
	finally: 
		# handle exiting the shell and child process
		LOGGER.debug(f'{child.exitstatus=} {child.signalstatus=}')
		time.sleep(0.5)  # TODO: more robust sleep (use loop)
		child.sendline('exit 0')  # try to close the login shell we created before closing the child process
		try:
			child.expect(pexpect.EOF, timeout=shell_exit_timeout_seconds)
		except pexpect.TIMEOUT:
			child.terminate(force=True)
		child.close(force=True)
		LOGGER.debug(f'{child.exitstatus=} {child.signalstatus=}')


def run_command(cmd: list, cmd_output_log_level=logging.DEBUG, logger=LOGGER, check=True, **kwargs) -> subprocess.CompletedProcess[str]:
	logger.debug(f'Running command: {cmd}', stacklevel=2)
	try:
		task = subprocess.run(cmd, capture_output=True, text=True, check=check, **kwargs)
	except subprocess.CalledProcessError as e:
		logger.error(f'Error running command: {cmd}')
		logger.info(e.stdout)
		logger.info(e.stderr)
		raise e

	logger.log(cmd_output_log_level, task.stdout)
	logger.log(cmd_output_log_level, task.stderr)


	if task.returncode != 0:
		msg = f'Error running command: {task.returncode}: {cmd}'
		log_level = logging.WARNING
		if not check:
			log_level = logging.DEBUG
		logger.log(log_level, msg)
		logger.debug(task.stdout)
		logger.debug(task.stderr)
	else:
		logger.debug(f'Finished command: {cmd}')

	return task


if __name__ == '__main__':
	import sys
	from liminal.shell import Shell
	try:
		timeout = int(sys.argv[2])
	except (IndexError, TypeError, ValueError):
		timeout=3
	# TODO: we need to set a different LOGGER here
	output = run_login_command(Shell().exec_path.as_posix(), sys.argv[1], timeout_seconds=timeout)
	print(output)

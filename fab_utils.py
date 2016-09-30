import getpass
from fabric.api import *
from fabric.operations import _prefix_env_vars, _prefix_commands, subprocess, win32, os, error, _AttributeString


class return_codes:
    def __init__(self, ok_ret_codes):
        self.previous_value = env.ok_ret_codes
        env.ok_ret_codes = ok_ret_codes

    def __enter__(self):
        return 0

    def __exit__(self, exc_type, exc_value, traceback):
        env.ok_ret_codes = self.previous_value


def lsudo(command, capture=False, shell=None):
    with return_codes([0, 1]):
        with hide('output', 'running'), settings(warn_only=True):
            while local('sudo -n true', capture=True).return_code == 1:
                whoami = local('whoami', capture=True)
                env.sudo_password = getpass.getpass('[sudo] password for {user}: '.format(user=whoami))
                local('echo %s|sudo -S true' % env.sudo_password, capture=True)

    given_command = command
    # Apply cd(), path() etc
    with_env = _prefix_env_vars(command, local=True)
    wrapped_command = _prefix_commands(with_env, 'local')
    if output.debug:
        print("[localhost] local: %s" % (wrapped_command))
    elif output.running:
        print("[localhost] local: " + given_command)
    # Adding sudo wrap
    if env.get('sudo_password') is not None:
        wrapped_command = 'echo %s|sudo -S %s' % (env.sudo_password, wrapped_command)
    else:
        wrapped_command = 'sudo %s' % wrapped_command

    # Tie in to global output controls as best we can; our capture argument
    # takes precedence over the output settings.
    dev_null = None
    if capture:
        out_stream = subprocess.PIPE
        err_stream = subprocess.PIPE
    else:
        dev_null = open(os.devnull, 'w+')
        # Non-captured, hidden streams are discarded.
        out_stream = None if output.stdout else dev_null
        err_stream = None if output.stderr else dev_null
    try:
        cmd_arg = wrapped_command if win32 else [wrapped_command]
        p = subprocess.Popen(cmd_arg, shell=True, stdout=out_stream,
                             stderr=err_stream, executable=shell,
                             close_fds=(not win32))
        (stdout, stderr) = p.communicate()
    finally:
        if dev_null is not None:
            dev_null.close()
    # Handle error condition (deal with stdout being None, too)
    out = _AttributeString(stdout.strip() if stdout else "")
    err = _AttributeString(stderr.strip() if stderr else "")
    out.command = given_command
    out.real_command = wrapped_command
    out.failed = False
    out.return_code = p.returncode
    out.stderr = err
    if p.returncode not in env.ok_ret_codes:
        out.failed = True
        msg = "local() encountered an error (return code %s) while executing '%s'" % (p.returncode, command)
        error(message=msg, stdout=out, stderr=err)
    out.succeeded = not out.failed
    # If we were capturing, this will be a string; otherwise it will be None.
    return out

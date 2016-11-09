from collections import namedtuple
from contextlib import contextmanager
from invoke import task

import re
from pip.req import parse_requirements
import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
HOME_DIR = os.path.expanduser('~')


@task
def setup_host(ctx, docker_machine='radioco'):
    IP_ADDRESS_PATTERN = r'(?P<ip>\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})'
    IP_ADDRESS = re.compile(IP_ADDRESS_PATTERN, flags=re.MULTILINE)
    HOST_LINE_PATTERN = re.compile(r'^\s*{IP_ADDRESS_PATTERN}\s+(?P<hostname>[\w\.\-_]+)'.format(IP_ADDRESS_PATTERN=IP_ADDRESS_PATTERN))
    HOST_LINE_FORMAT = '{ip}    {hostname}    # GENERATED AUTOMATICALLY'
    HOSTNAME = 'radioco'
    HostEntry = namedtuple('HostEntry', ['ip', 'hostname'])

    if docker_machine:
        machines = ctx.run('docker-machine ls | grep {machine}'.format(machine=docker_machine), capture=True)
    else:
        machines = ctx.run('docker-machine ls', capture=True)
    docker_machine_ips = tuple(match.group(1) for match in IP_ADDRESS.finditer(machines))
    if len(docker_machine_ips) != 1:
        if docker_machine:
            msg = 'You have {0} machines running with the same name'.format(len(docker_machine_ips)) if len(docker_machine_ips) else 'The machine "{0}" is not running'.format(docker_machine)
        else:
            msg = 'You have {0} machines running. Please specify a name'.format(len(docker_machine_ips)) if len(docker_machine_ips) else 'There are no machines running'
        raise RuntimeError(msg)
    docker_machine_ip = docker_machine_ips[0]

    with open('/etc/hosts', 'r') as hosts_filehandle:
        hosts_lines = hosts_filehandle.read().split('\n')

    host_line_exist = False
    new_host_lines = []
    for host_line in hosts_lines:
        try:
            host_entry = HostEntry(**HOST_LINE_PATTERN.match(host_line).groupdict())
        except AttributeError:
            new_host_lines.append(host_line)
        else:
            if host_entry.hostname == HOSTNAME:
                host_line_exist = True
                new_host_lines.append(HOST_LINE_FORMAT.format(ip=docker_machine_ip, hostname=HOSTNAME))
            else:
                new_host_lines.append(host_line)
    if not host_line_exist:
        new_host_lines.append(HOST_LINE_FORMAT.format(ip=docker_machine_ip, hostname=HOSTNAME))
        new_host_lines.append('')

    with open('/tmp/hosts', 'w') as hosts_filehandle:
        hosts_filehandle.write('\n'.join(new_host_lines))
    lsudo("sh -c 'cat /tmp/hosts > /etc/hosts'".format('\n'.join(new_host_lines)))
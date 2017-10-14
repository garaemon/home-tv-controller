#!/usr/bin/env python
# script to deploy codes

import os
import subprocess

import fire

PYENV_INSTALLER_URL = 'https://raw.githubusercontent.com/' + \
    'pyenv/pyenv-installer/master/bin/pyenv-installer'

PYENV_SETUP_COMMANDS = ['export PATH="$HOME/.pyenv/bin:$PATH"',
                        'eval "$(pyenv init -)"',
                        'eval "$(pyenv virtualenv-init -)"']


def install_pyenv(hostname):
    print('> Installing pyenv')
    subprocess.check_call(['ssh', hostname,
                           'curl -L %s | bash' % PYENV_INSTALLER_URL])


def concatenate_shell_commands(commands):
    return ''.join([c + ';' for c in commands])


def install_python(hostname, version='3.5.2'):
    commands = PYENV_SETUP_COMMANDS + ['pyenv install %s -s' % version,
                                       'pyenv global %s' % version,
                                       'pip install -U virtualenv']
    subprocess.check_call(['ssh', hostname,
                           concatenate_shell_commands(commands)])


def deploy_source_code(hostname, target_directory):
    exclude_directories = ['.venv', '.idea', '.git', '__pycache__', '*.pyc']
    from_directory = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                  '..'))
    exclude_options = ['--exclude=%s' % d for d in exclude_directories]
    subprocess.check_call(['rsync', '-avz'] + exclude_options +
                          [from_directory + '/', '%s:%s/'
                           % (hostname, target_directory)])


def build_code(hostname, target_directory):
    commands = PYENV_SETUP_COMMANDS + ['cd %s' % target_directory,
                                       'make',
                                       'source .venv/bin/activate',
                                       'python setup.py develop']
    subprocess.check_call(['ssh', hostname,
                           concatenate_shell_commands(commands)])


def main(hostname, target_directory):
    print('> Start deploying to %s' % hostname)
    install_pyenv(hostname)
    install_python(hostname)
    deploy_source_code(hostname, target_directory)
    build_code(hostname, target_directory)


if __name__ == '__main__':
    fire.Fire(main)

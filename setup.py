#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Allow trove classifiers in previous python versions
from sys import version
if version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

from home_tv_controller import __version__ as version

def requireModules(moduleNames=None):
    import re
    if moduleNames is None:
        moduleNames = []
    else:
        moduleNames = moduleNames

    commentPattern = re.compile(r'^\w*?#')
    moduleNames.extend(
        filter(lambda line: not commentPattern.match(line), 
            open('requirements.txt').readlines()))

    return moduleNames

setup(
    name='home_tv_controller',
    version=version,

    author='garaemon',
    author_email='garaemon@gmail.com',

    description='TV Controller for home use',
    long_description=open('README.txt').read(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers'
    ],

    install_requires=requireModules([

    ]),

    test_suite='home_tv_controller'
)

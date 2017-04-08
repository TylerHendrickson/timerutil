from setuptools import setup
import sys


test_requirements = []
if sys.version_info < (3, 3):
    test_requirements = ['mock']

setup(
    name='Timerutil',
    version='1.0.0',
    url='https://github.com/TySkby/timerutil',
    author='Tyler Hendrickson',
    author_email='hendrickson.tsh@gmail.com',
    description='Collection of timer-related utilities for Python',
    long_description=__doc__,
    packages=['timerutil'],
    zip_safe=True,
    tests_require=test_requirements,
    test_suite='tests',
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux'
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)

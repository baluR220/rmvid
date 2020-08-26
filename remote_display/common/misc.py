'''
Classes and fuctions common for widgets and control app
'''
import sys


def check_python_version():
    '''
    Checks the version of python that called this script.
    '''
    PYTHON_VERSION = sys.version.split(' ')[0]
    WRONG_PYTHON_VERSION = "Python version should be 3.8 \
or newer. Yours is %s" % PYTHON_VERSION
    assert sys.version_info >= (3, 8), WRONG_PYTHON_VERSION

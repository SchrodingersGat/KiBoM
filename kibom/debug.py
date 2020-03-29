# -*- coding: utf-8 -*-

from __future__ import print_function

import sys

# Various msg levels
MSG_MESSAGE = -1   # Display generic message (always displayed)
MSG_ERROR = 0      # Display error messages
MSG_WARN = 1       # Display warning messages
MSG_INFO = 2       # Display information messages
MSG_DEBUG = 3      # Display debug messages

MSG_CODES = {
    MSG_ERROR: "ERROR",
    MSG_WARN: "WARNING",
    MSG_INFO: "INFO",
    MSG_DEBUG: "DEBUG",
}

# By default, only display error messages
MSG_LEVEL = MSG_ERROR

# Keep track of accumulated errorsh
ERR_COUNT = 0


def setDebugLevel(level):
    global MSG_LEVEL
    MSG_LEVEL = int(level)


def getErrorCount():
    global ERR_COUNT
    return ERR_COUNT


def _msg(prefix, *arg):
    """
    Display a message with the given color.
    """

    msg = ""
    
    if prefix:
        msg += prefix

    print(msg, *arg)


def message(*arg):
    """
    Display a message
    """

    _msg("", *arg)


def debug(*arg):
    """
    Display a debug message.
    """

    global MSG_LEVEL
    if MSG_LEVEL < MSG_DEBUG:
        return

    _msg(MSG_CODES[MSG_DEBUG], *arg)


def info(*arg):
    """
    Display an info message.
    """

    global MSG_LEVEL
    if MSG_LEVEL < MSG_INFO:
        return

    _msg(MSG_CODES[MSG_INFO], *arg)


def warning(*arg):
    """
    Display a warning message
    """

    global MSG_LEVEL
    if MSG_LEVEL < MSG_WARN:
        return

    _msg(MSG_CODES[MSG_WARN], *arg)


def error(*arg, **kwargs):
    """
    Display an error message
    """

    global MSG_LEVEL
    global ERR_COUNT

    if MSG_LEVEL < MSG_ERROR:
        return

    _msg(MSG_CODES[MSG_ERROR], *arg)

    ERR_COUNT += 1

    fail = kwargs.get('fail', False)

    if fail:
        sys.exit(ERR_COUNT)

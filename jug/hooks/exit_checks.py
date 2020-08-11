# -*- coding: utf-8 -*-
# Copyright (C) 2014-2020, Luis Pedro Coelho <luis@luispedro.org>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

from sys import exit
import typing

Number = typing.Union[int, float]

def exit_if_file_exists(fname):
    '''Before each task execute, check if file exists. If so, exit.

    Note that a check is only performed before a Task is execute. Thus, jug
    will not exit immediately if it is executing another long-running task.

    Parameters
    ----------
    fname : str
        path to check
    '''
    from jug import hooks
    def check_file(_t):
        from os import path
        if path.exists(fname):
            exit(0)
    hooks.register_hook('execute.task-pre-execute', check_file)

def exit_when_true(f : typing.Callable, function_takes_Task: bool = False):
    '''Generic exit check.
    
    After each task, call function ``f`` and exit if it return true.

    Parameters
    ----------
    f : function
        Function to call
    function_takes_Task : boolean, optional
        Whether to call the function with the task just executed (default: False)
    '''

    from jug import hooks
    if not function_takes_Task:
        f = lambda t : f()
    def exit_when(t):
        if f(t):
            exit(0)
    hooks.register_hook('execute.task-executed1', exit_when)


def exit_after_n_tasks(n : int):
    '''Exit after a specific number of tasks have been executed

    Parameters
    ----------
    n : int
        Number of tasks to execute
    '''
    from jug import hooks
    # In newer Python, we could use nonlocal, but this is a work around
    # (http://stackoverflow.com/questions/9603278/is-there-something-like-nonlocal-in-python-3/9603491#9603491)
    executed = [0]

    def exit_after(_t):
        executed[0] += 1
        if executed[0] >= n:
            exit(0)
    hooks.register_hook('execute.task-executed1', exit_after)


def exit_after_time(hours: Number = 0, minutes: Number = 0, seconds: Number = 0):
    '''Exit after a specific number of tasks have been executed

    Note that this only checks the time **after each task has finished
    executing**. Thus if you are using this to limit the amount of time each
    process takes, make sure to specify a lower limit than what is needed.

    Parameters
    ----------
    hours : number, optional
    minutes : number, optional
    seconds : number, optional
    '''
    from jug import hooks
    from time import time
    deadline = time()
    deadline += seconds
    deadline += 60*minutes
    deadline += 60*60*hours

    def check_time(_t):
        if time() >= deadline:
            exit(0)
    hooks.register_hook('execute.task-executed1', check_time)


def exit_env_vars(environ=None):
    '''
    exit_env_vars(environ={os.environ})

    Set exit markers based on the environment.

    The following variables are used if they are set (if they are not set, they
    are ignored).

    ``JUG_MAX_TASKS``: Maximum nr. of tasks.

    ``JUG_MAX_HOURS``: Maximum hours

    ``JUG_MAX_MINUTES``: Maximum minutes

    ``JUG_MAX_SECONDS``: Maximum seconds

    For the time based limits, see the comment on `exit_after_time` on how
    these limits are not strict as they are only checked after each task
    completion event.

    If either of the variables above is set, its value should be an int or an
    error will be raised.

    JUG_EXIT_IF_FILE_EXISTS: Set exit file name

    See Also
    --------
    exit_after_n_tasks
    exit_after_time
    exit_if_file_exists
    '''

    if environ is None:
        import os
        environ = os.environ
    if 'JUG_MAX_TASKS' in environ:
        exit_after_n_tasks(int(environ['JUG_MAX_TASKS']))

    hours = 0
    minutes = 0
    seconds = 0
    if 'JUG_MAX_HOURS' in environ:
        hours = int(environ['JUG_MAX_HOURS'])
    if 'JUG_MAX_MINUTES' in environ:
        minutes = int(environ['JUG_MAX_MINUTES'])
    if 'JUG_MAX_SECONDS' in environ:
        seconds = int(environ['JUG_MAX_SECONDS'])
    if hours or minutes or seconds:
        exit_after_time(hours=hours, minutes=minutes, seconds=seconds)

    if 'JUG_EXIT_IF_FILE_EXISTS' in environ:
        exit_if_file_exists(environ['JUG_EXIT_IF_FILE_EXISTS'])

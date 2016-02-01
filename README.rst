.. image:: https://travis-ci.org/ImmobilienScout24/shmock.png?branch=master
   :alt: Travis build status image
   :align: left
   :target: https://travis-ci.org/ImmobilienScout24/shmock

.. image:: https://coveralls.io/repos/ImmobilienScout24/shmock/badge.png?branch=master
    :alt: Coverage status
    :target: https://coveralls.io/r/ImmobilienScout24/shmock?branch=master

.. image:: https://badge.fury.io/py/shmock.png
    :alt: Latest PyPI version
    :target: https://badge.fury.io/py/shmock


SHell command MOCK (SHMOCK)
===========================

Purpose
-------

Tools for system administration typically call lots of programs on the command line. This makes automated testing quite tricky, since you may need to

* run "sudo ....", even though the build system is not allowed to use sudo
* have tools like "uname" or "ifconfig" produce certain output for testing

shmock helps you by creating mock commands that supersede the system's own commands due to a temporarily manipulated $PATH. Based on the command line parameters, mock commands can have different

* output on STDOUT and STDERR
* exit code

It is not possible to simulate slowness or commands that behave differently the second time you call them. Command line parsing is very limited, but that's not a problem for auto-generated calls. However, these limitations make the implementation very simple.


Configuration
-------------

To configure which commands should be mocked (and how), use a dictionary like this:

.. code-block:: python

    commands_to_mock = {
        'saynay': 'Nay sayers say nay.',
        'jonny': {
            (): "walker",
            "foo": "bar",
            ("b", "goode"): "Go, Jonny, go!",
            ("be", "bad"): {"stderr": "yup", "returncode": 255},
            None: {
                "stdout": "You called me with some unknown parameters.",
                "stderr": "And I don't like that.",
                "returncode": 1
            }
        }
    }

The first part uses the most simple way of defining a mocked command: A 'saynay' command is defined that always prints "Nay sayers say nay." and exits successfully, regardless of command line options.

After that, a 'jonny' command is defined that illustrates the full feature set of the shmock module. The command is defined to

* When called with no parameters, print "walker".
* When called with a single parameter "foo", print "bar".
* When called with the two parameters "b" and "goode", print "Go, Jonny, go!".
* When called with "be bad", print "yup" to standard error and then exit with 255.
* When called with any other parameters, print "You..." to standard out, print "And..." to standard error and then exit with 1.

Usage
-----

The ShellCommandMock is intended to be used in "with" contexts as shown below:

.. code-block:: python

    import os
    from shmock import ShellCommandMock
    with ShellCommandMock(commands_to_mock):
        os.system("echo $PATH")

        os.system("jonny")
        os.system("jonny b goode")
        os.system("jonny be bad")
        os.system("jonny foobar")

    os.system("echo $PATH")

Advanced Usage
--------------

Sometimes you want to keep the mocked shell commands for further testing/debugging. You can tell shmock to not clean up the mock environment with

.. code-block:: python

    from shmock import ShellCommandMock
    with ShellCommandMock(commands_to_mock, keep_temp_dir=True):
        pass

shmock will print the location of the mock environment, so that you can add it to you $PATH.

When output is printed, shmock calls print(), and print() automatically appends a newline to the output. As a result, it is currently not possible to produce output that does not end in a newline. This will be fixed once it becomes a problem.

License
-------

Copyright 2015 Immobilien Scout GmbH

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

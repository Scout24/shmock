from __future__ import print_function, absolute_import, unicode_literals, division

import six
import subprocess
import unittest2

from mock import patch

from shmock import ShellCommandMock


def call(args):
    process = subprocess.Popen(args,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_data, stderr_data = process.communicate()
    exit_code = process.returncode

    return stdout_data, stderr_data, exit_code

class ShmockTest(unittest2.TestCase):
    def test_empty_config(self):
        commands_to_mock = {}
        with ShellCommandMock(commands_to_mock):
            pass

    def test_string_config(self):
        """Regardless of parameters, saynay must always do the same thing"""
        commands_to_mock = {'saynay': 'Nay sayers say nay.'}
        with ShellCommandMock(commands_to_mock):
            for extra_args in ([], ['foo'], ['foo', '--bar']):
                args = ['saynay']
                args.extend(extra_args)
                out, err, code = call(args)

                self.assertEqual(out, b"Nay sayers say nay.\n")
                self.assertEqual(err, b"")
                self.assertEqual(code, 0)


    def test_replace_existing_commands(self):
        """Mocked commands must replace existing commands""" 
        commands_to_mock = {
            'grep': 'I am fake',
            'bash': 'I am fake',
            'id': 'I am fake'}
        with ShellCommandMock(commands_to_mock):
            for command in ('grep', 'bash', 'id'):
                out, err, code = call([command])

                self.assertEqual(out, b"I am fake\n")
                self.assertEqual(err, b"")
                self.assertEqual(code, 0)

    def test_dont_replace_unmocked_commands(self):
        """commands that were not mocked must remain unchanged""" 
        commands_to_mock = {'foo': 'bar'}
        with ShellCommandMock(commands_to_mock):
            out, err, code = call(['true'])
            self.assertEqual(out, b"")
            self.assertEqual(err, b"")
            self.assertEqual(code, 0)

            out, err, code = call(['false'])
            self.assertEqual(out, b"")
            self.assertEqual(err, b"")
            self.assertNotEqual(code, 0)

    def test_no_params(self):
        """Mocking no params must work"""
        commands_to_mock = {
            'foo': {
                (): "I have no parameters"
            }
        }
        with ShellCommandMock(commands_to_mock):
            out, err, code = call(['foo'])
            self.assertEqual(out, b"I have no parameters\n")
            self.assertEqual(err, b"")
            self.assertEqual(code, 0)

    def test_string_params(self):
        """Mock params provided as strings must work"""
        commands_to_mock = {
            'foo': {
                'param1': 'foo',
                'param2': 'bar',
            }
        }
        with ShellCommandMock(commands_to_mock):
            out, err, code = call(['foo', 'param1'])
            self.assertEqual(out, b"foo\n")
            self.assertEqual(err, b"")
            self.assertEqual(code, 0)

            out, err, code = call(['foo', 'param2'])
            self.assertEqual(out, b"bar\n")
            self.assertEqual(err, b"")
            self.assertEqual(code, 0)

            out, err, code = call(['foo', 'param3'])
            self.assertNotEqual(out, b"")
            self.assertNotEqual(err, b"")
            self.assertNotEqual(code, 0)

    def test_tuple_params(self):
        """Mock params provided as tuples must work"""
        commands_to_mock = {
            'foo': {
                ('param1', 'x'): 'foo',
                ('param2', 'y'): 'bar',
            }
        }
        with ShellCommandMock(commands_to_mock):
            out, err, code = call(['foo', 'param1', 'x'])
            self.assertEqual(out, b"foo\n")
            self.assertEqual(err, b"")
            self.assertEqual(code, 0)

            out, err, code = call(['foo', 'param2', 'y'])
            self.assertEqual(out, b"bar\n")
            self.assertEqual(err, b"")
            self.assertEqual(code, 0)

            out, err, code = call(['foo', 'param3', 'z'])
            self.assertNotEqual(out, b"")
            self.assertNotEqual(err, b"")
            self.assertNotEqual(code, 0)

    def test_partial_dict_behavior(self):
        """Behavior specified as dict must apply defaults when incomplete"""
        commands_to_mock = {
            'foo': {'x': {'stdout': "xxx"}},
            'bar': {'y': {'stderr': "yyy"}},
            'batz': {'z': {'returncode': 42}}
        }
        with ShellCommandMock(commands_to_mock):
            out, err, code = call(['foo', 'x'])
            self.assertEqual(out, b"xxx\n")
            self.assertEqual(err, b"")
            self.assertEqual(code, 0)

            out, err, code = call(['bar', 'y'])
            self.assertEqual(out, b"")
            self.assertEqual(err, b"yyy\n")
            self.assertEqual(code, 0)

            out, err, code = call(['batz', 'z'])
            self.assertEqual(out, b"")
            self.assertEqual(err, b"")
            self.assertEqual(code, 42)

    def test_full_dict_behavior(self):
        """Behavior completely specified as dict must work"""
        commands_to_mock = {
            'foo': {'x': {'stdout': "xxx", 'stderr': "yyy", 'returncode': 42}}}

        with ShellCommandMock(commands_to_mock):
            out, err, code = call(['foo', 'x'])
            self.assertEqual(out, b"xxx\n")
            self.assertEqual(err, b"yyy\n")
            self.assertEqual(code, 42)

    def test_default_behavior(self):
        """Behavior for None must become the default"""
        commands_to_mock = {
            'foo': {
                'x': "hello world",
                None: "default"
            }
        }
        with ShellCommandMock(commands_to_mock):
            out, err, code = call(['foo', 'x'])
            self.assertEqual(out, b"hello world\n")
            self.assertEqual(err, b"")
            self.assertEqual(code, 0)

            out, err, code = call(['foo', 'what', 'ever'])
            self.assertEqual(out, b"default\n")
            self.assertEqual(err, b"")
            self.assertEqual(code, 0)

            out, err, code = call(['foo'])
            self.assertEqual(out, b"default\n")
            self.assertEqual(err, b"")
            self.assertEqual(code, 0)

    @patch("six.moves.builtins.print")
    def test_keep_temp_dir(self, mock_print):
        """keep_temp_dir=True must preserve the mock files on disc

        Also, it must print the location of the temporary directory.
        """
        commands_to_mock = {
            'foo': 'bar'
        }
        import os
        import shutil

        with ShellCommandMock(commands_to_mock, keep_temp_dir=True) as shmocker:
                mock_dir = shmocker.temp_dir
        try:
            printed = "\n".join([x[0][0] for x in mock_print.call_args_list])
            self.assertIn(mock_dir, printed)

            expected_mock = os.path.join(mock_dir, 'foo')
            self.assertTrue(os.path.exists(expected_mock))
        finally:
            shutil.rmtree(mock_dir)

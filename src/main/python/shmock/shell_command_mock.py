from __future__ import print_function, absolute_import, unicode_literals, division

import os
import shutil
import six
import stat
import tempfile

_MOCK_SCRIPT_TEMPLATE = """#!/usr/bin/env python
from __future__ import print_function, absolute_import, unicode_literals, division
import sys

expected_behavior = {behavior!r}
my_parameters = tuple(sys.argv[1:])
for parameters, special_behavior in expected_behavior.items():
    if parameters is None:
        continue
    parameters = parameters
    if parameters == my_parameters:
        if special_behavior['stdout']:
            print(special_behavior['stdout'], file=sys.stdout)
        if special_behavior['stderr']:
            print(special_behavior['stderr'], file=sys.stderr)
        sys.exit(special_behavior['returncode'])

special_behavior = expected_behavior[None]
if special_behavior['stdout']:
    print(special_behavior['stdout'], file=sys.stdout)
if special_behavior['stderr']:
    print(special_behavior['stderr'], file=sys.stderr)
sys.exit(special_behavior['returncode'])
"""


class ShellCommandMock(object):
    def __init__(self, commands_to_mock, keep_temp_dir=False):
        self.commands_to_mock = commands_to_mock
        self.keep_temp_dir = keep_temp_dir
        self.temp_dir = None
        self.old_path = None

    def __enter__(self):
        self.temp_dir = tempfile.mkdtemp(prefix=self.__class__.__name__ + "_")
        self.old_path = os.getenv("PATH", "")
        os.environ['PATH'] = self.temp_dir + ":" + self.old_path
        self.create_scripts()
        return self

    def __exit__(self, *args):
        os.environ['PATH'] = self.old_path
        if self.keep_temp_dir:
            print("Temp dir of %s is at %s" % (
                self.__class__.__name__, self.temp_dir))
        else:
            shutil.rmtree(self.temp_dir)

    @staticmethod
    def _normalize_parameters(params):
        if params is None:
            return None
        if isinstance(params, six.string_types):
            return (params,)
        return tuple(params)

    @staticmethod
    def _normalize_reaction(reaction, default_reaction=None):
        default_reaction = default_reaction or {
            "stdout": "",
            "stderr": "",
            "returncode": 0}
        if isinstance(reaction, six.string_types):
            reaction = {'stdout': reaction}
        default_reaction.update(reaction)
        return default_reaction

    def normalize_behavior(self, behavior):
        """Convert various behavior for a single command

        This expands the various shortcut notations into the very verbose
        (par1, par2,...): {'stdout': '...', 'stderr': '...', 'returncode': 42}
        notation.
        """
        if isinstance(behavior, six.string_types):
            # Use $behavior as stdout for any parameters
            return {None: {'stdout': behavior, 'stderr': "", 'returncode': 0}}

        normalized_behavior = {}
        for params, reaction in behavior.items():
            params = self._normalize_parameters(params)
            reaction = self._normalize_reaction(reaction)
            normalized_behavior[params] = reaction

        # Default action when none of the params matched
        if None in behavior:
            none_reaction = self._normalize_reaction(behavior[None])
        else:
            none_reaction = {
                "stdout": "These parameters are not mocked!",
                "stderr": "These parameters are not mocked!",
                "returncode": 1}
        normalized_behavior[None] = none_reaction

        return normalized_behavior

    def create_scripts(self):
        for command, behavior in self.commands_to_mock.items():
            behavior = self.normalize_behavior(behavior)
            mock_script_name = os.path.join(self.temp_dir, command)
            with open(mock_script_name, "w") as mock_script:
                mock_script.write(
                    _MOCK_SCRIPT_TEMPLATE.format(behavior=behavior))
            os.chmod(mock_script_name, stat.S_IRWXU)

from pybuilder.core import use_plugin, init, Author

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "shmock"
summary = 'SHell command MOCKer for integration testing'
version = '1.0.0'
description = open("README.rst").read()
url = 'https://github.com/ImmobilienScout24/shmock'
authors = [Author('Stefan Nordhausen', "stefan.nordhausen@immobilienscout24.de")]
license = 'Apache License 2.0'
default_task = ['analyze', 'publish']


@init
def set_properties(project):
    project.build_depends_on("mock<1.1")
    project.build_depends_on("unittest2")
    project.depends_on("six")

    project.set_property("distutils_classifiers", [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
         ])

@init(environments='teamcity')
def set_properties_for_teamcity_builds(project):
    import os
    project.set_property('teamcity_output', True)
    project.version = '%s-%s' % (project.version,
                                 os.environ.get('BUILD_NUMBER', 0))
    project.default_task = ['clean', 'install_build_dependencies', 'publish']
    project.set_property('install_dependencies_index_url',
                         os.environ.get('PYPIPROXY_URL'))
    project.rpm_release = os.environ.get('RPM_RELEASE', 0)

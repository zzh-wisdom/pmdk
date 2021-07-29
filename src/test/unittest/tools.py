# SPDX-License-Identifier: BSD-3-Clause
# Copyright 2019-2021, Intel Corporation
#
"""External tools integration"""

import os
import json
import sys
import subprocess as sp

import futils

try:
    import envconfig
    envconfig = envconfig.config
except ImportError:
    # if file doesn't exist create dummy object
    envconfig = {'GLOBAL_LIB_PATH': '', 'PMEM2_AVX512F_ENABLED': ''}


class Tools:
    PMEMDETECT_FALSE = 0
    PMEMDETECT_TRUE = 1
    PMEMDETECT_ERROR = 2

    def __init__(self, env, build):
        self.env = env
        self.build = build
        global_lib_path = envconfig['GLOBAL_LIB_PATH']

        if sys.platform == 'win32':
            futils.add_env_common(self.env, {'PATH': global_lib_path})
            futils.add_env_common(self.env, {'PATH': build.libdir})
        else:
            futils.add_env_common(self.env,
                                  {'LD_LIBRARY_PATH': global_lib_path})
            futils.add_env_common(self.env, {'LD_LIBRARY_PATH': build.libdir})

    def _run_test_tool(self, name, *args):
        exe = futils.get_test_tool_path(self.build, name)
        if sys.platform == 'win32':
            exe += '.exe'

        return sp.run([exe, *args], env=self.env, stdout=sp.PIPE,
                      stderr=sp.STDOUT, universal_newlines=True)

    def pmemdetect(self, *args):
        return self._run_test_tool('pmemdetect', *args)

    def gran_detecto(self, *args):
        return self._run_test_tool('gran_detecto', *args)

    def cpufd(self):
        return self._run_test_tool('cpufd')

    def mapexec(self, *args):
        return self._run_test_tool('mapexec', *args)


class Ndctl:
    """ndctl CLI handle

    Attributes:
        version (str): ndctl version
        ndctl_list_output (dict): output of 'ndctl list' command
            decoded from JSON into dictionary
    """
    def __init__(self):
        self.version = self._get_ndctl_version()
        self.ndctl_list_output = self._get_ndctl_list_output('list')

    def _get_ndctl_version(self):
        """
        Get ndctl version.

        Acquiring the version is simultaneously used as a check whether
        the ndctl is installed on the system.

        Returns:
            ndctl version (str)

        """
        proc = sp.run(['ndctl', '--version'], stdout=sp.PIPE, stderr=sp.STDOUT)
        if proc.returncode != 0:
            raise futils.Fail('checking if ndctl exists failed:{}{}'
                              .format(os.linesep, proc.stdout))

        version = proc.stdout.strip()
        return version

    def _get_ndctl_list_output(self, *args):
        """
        Parse 'ndctl list' command output as JSON
        into a dictionary and return it.
        """
        proc = sp.run(['ndctl', *args], stdout=sp.PIPE, stderr=sp.STDOUT)
        if proc.returncode != 0:
            raise futils.Fail('ndctl list failed:{}{}'.format(os.linesep,
                                                              proc.stdout))
        try:
            ndctl_list_out = json.loads(proc.stdout)
        except json.JSONDecodeError:
            raise futils.Fail('Invalid "ndctl list" output (could '
                              'not read as JSON): {}'.format(proc.stdout))
        return ndctl_list_out

    def _get_dev_info(self, dev_path):
        """
        Get ndctl information about the given device.
        Returns dictionary associated with device.
        """
        dev = None

        # Possible viable device types as shown with
        # 'ndctl list' output
        devtypes = ('blockdev', 'chardev')

        for d in self._get_ndctl_list_output('list'):
            for dt in devtypes:
                if dt in d and os.path.join('/dev', d[dt]) == dev_path:
                    dev = d

        if not dev:
            raise futils.Fail('ndctl does not recognize the device: "{}"'
                              .format(dev_path))
        return dev

    # for ndctl v63 we need to parse ndctl list in a different way than for v64
    def _get_dev_info_63(self, dev_path):
        dev = None
        devtype = 'chardev'
        daxreg = 'daxregion'

        for d in self._get_ndctl_list_output('list', '-v'):
            if daxreg in d:
                devices = d[daxreg]['devices']
                for device in devices:
                    if devtype in device and \
                            os.path.join('/dev', device[devtype]) == dev_path:
                        # only params from daxreg are interested at this point,
                        # other values are read by _get_dev_info() earlier
                        dev = d[daxreg]

        if not dev:
            raise futils.Fail('ndctl does not recognize the device: "{}"'
                              .format(dev_path))

        return dev

    def _get_dev_param(self, dev_path, param):
        """
        Acquire device parameter from 'ndctl list' output.

        Args:
            dev_path (str): path of device
            param (str): parameter

        """
        p = None
        dev = self._get_dev_info(dev_path)

        try:
            p = dev[param]
        except KeyError:
            dev = self._get_dev_info_63(dev_path)
            p = dev[param]

        return p

    def get_dev_size(self, dev_path):
        return int(self._get_dev_param(dev_path, 'size'))

    def get_dev_alignment(self, dev_path):
        return int(self._get_dev_param(dev_path, 'align'))

    def get_dev_mode(self, dev_path):
        return self._get_dev_param(dev_path, 'mode')

    def is_devdax(self, dev_path):
        return self.get_dev_mode(dev_path) == 'devdax'

    def is_fsdax(self, dev_path):
        return self.get_dev_mode(dev_path) == 'fsdax'

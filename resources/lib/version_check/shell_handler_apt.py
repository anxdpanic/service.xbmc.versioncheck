# -*- coding: utf-8 -*-

"""

    Copyright (C) 2013-2014 Team-XBMC
    Copyright (C) 2014-2019 Team Kodi

    This file is part of service.xbmc.versioncheck

    SPDX-License-Identifier: GPL-3.0-or-later
    See LICENSES/GPL-3.0-or-later.txt for more information.

"""

import sys

from .common import log
from .handler import Handler

try:
    from subprocess import check_output
except:
    log('subprocess import error')


class ShellHandlerApt(Handler):

    def __init__(self, use_sudo=False):
        super(ShellHandlerApt, self).__init__()
        self.sudo = use_sudo
        installed, _ = self._check_versions('xbmc', False)
        if not installed:
            # there is no package installed via repo, so we exit here
            log('No installed package found, exiting')
            sys.exit(0)

    def _check_versions(self, package, update=True):
        _cmd = 'apt-cache policy ' + package

        if update and not self._update_cache():
            return False, False

        try:
            result = check_output([_cmd], shell=True).split('\n')
        except Exception as error:
            log('ShellHandlerApt: exception while executing shell command %s: %s' % (_cmd, error))
            return False, False

        if result[0].replace(':', '') == package:
            installed = result[1].split()[1]
            candidate = result[2].split()[1]
            if installed == '(none)':
                installed = False
            if candidate == '(none)':
                candidate = False
            return installed, candidate

        log('ShellHandlerApt: error during version check')
        return False, False

    def _update_cache(self):
        _cmd = 'apt-get update'
        try:
            if self.sudo:
                _ = check_output('echo \'%s\' | sudo -S %s' %
                                 (self._get_password(), _cmd), shell=True)
            else:
                _ = check_output(_cmd.split())
        except Exception as error:
            log('Exception while executing shell command %s: %s' % (_cmd, error))
            return False

        return True

    def upgrade_package(self, package):
        _cmd = 'apt-get install -y ' + package
        try:
            if self.sudo:
                _ = check_output('echo \'%s\' | sudo -S %s' %
                                 (self._get_password(), _cmd), shell=True)
            else:
                _ = check_output(_cmd.split())
            log('Upgrade successful')
        except Exception as error:
            log('Exception while executing shell command %s: %s' % (_cmd, error))
            return False

        return True

    def upgrade_system(self):
        _cmd = 'apt-get upgrade -y'
        try:
            log('Upgrading system')
            if self.sudo:
                _ = check_output('echo \'%s\' | sudo -S %s' %
                                 (self._get_password(), _cmd), shell=True)
            else:
                _ = check_output(_cmd.split())
        except Exception as error:
            log('Exception while executing shell command %s: %s' % (_cmd, error))
            return False

        return True

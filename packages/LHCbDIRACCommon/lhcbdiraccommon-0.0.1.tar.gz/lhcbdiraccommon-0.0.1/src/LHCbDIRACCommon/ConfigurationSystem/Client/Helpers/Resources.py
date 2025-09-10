###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""LHCbDIRACCommon Resources helper containing platform utilities."""

import LbPlatformUtils

from DIRACCommon.Core.Utilities.ReturnValues import S_OK, S_ERROR


def getDIRACPlatform(platform):
    """Returns list of compatible platforms.

    Used in JobDB.py instead of DIRAC.ConfigurationSystem.Client.Helpers.Resources.getDIRACPlatform

    :param str platform: a string (or a list with 1 string in)
                         representing a DIRAC platform, e.g. x86_64-centos7.avx2+fma
    :returns: S_ERROR or S_OK() with a list of DIRAC platforms that can run platform (e.g. slc6 can run on centos7)
    """

    # In JobDB.py this function is called with a list in input
    # In LHCb it should always be 1 and 1 only. If it's more there's an issue.
    if isinstance(platform, list):
        if len(platform) > 1:
            return S_ERROR("More than 1 platform specified for the job")
        platform = platform[0]

    if not platform or platform.lower() == "any":
        return S_OK([])

    return S_OK(LbPlatformUtils.compatible_platforms(platform))

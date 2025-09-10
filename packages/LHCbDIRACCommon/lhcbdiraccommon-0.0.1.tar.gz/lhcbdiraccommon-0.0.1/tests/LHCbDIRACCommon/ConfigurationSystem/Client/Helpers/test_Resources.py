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
"""Unit tests for LHCbDIRACCommon Configuration Helpers."""

import pytest

from LHCbDIRACCommon.ConfigurationSystem.Client.Helpers.Resources import (
    getDIRACPlatform,
)


@pytest.mark.parametrize(
    "platform, expectedRes, expectedValue",
    [
        ("", True, []),
        ("ANY", True, []),
        (["ANY"], True, []),
        ([None], True, []),
        (["bih", "boh"], False, []),
        (
            "x86_64-slc6",
            True,
            [
                "cannonlake-slc6",
                "skylake_avx512-slc6",
                "skylake-slc6",
                "broadwell-slc6",
                "haswell-slc6",
                "ivybridge-slc6",
                "sandybridge-slc6",
                "westmere-slc6",
                "nehalem-slc6",
                "core2-slc6",
                "x86_64-slc6",
            ],
        ),
        (
            "x86_64-centos7",
            True,
            [
                "cannonlake-centos7",
                "skylake_avx512-centos7",
                "skylake-centos7",
                "broadwell-centos7",
                "haswell-centos7",
                "ivybridge-centos7",
                "sandybridge-centos7",
                "westmere-centos7",
                "nehalem-centos7",
                "core2-centos7",
                "x86_64-centos7",
            ],
        ),
        (
            "x86_64-slc5",
            True,
            [
                "cannonlake-slc6",
                "skylake_avx512-slc6",
                "skylake-slc6",
                "broadwell-slc6",
                "haswell-slc6",
                "ivybridge-slc6",
                "sandybridge-slc6",
                "westmere-slc6",
                "nehalem-slc6",
                "core2-slc6",
                "x86_64-slc6",
                "cannonlake-slc5",
                "skylake_avx512-slc5",
                "skylake-slc5",
                "broadwell-slc5",
                "haswell-slc5",
                "ivybridge-slc5",
                "sandybridge-slc5",
                "westmere-slc5",
                "nehalem-slc5",
                "core2-slc5",
                "x86_64-slc5",
            ],
        ),
        (
            "x86_64-slc5.avx2",
            True,
            [
                "cannonlake-slc6",
                "skylake_avx512-slc6",
                "skylake-slc6",
                "broadwell-slc6",
                "haswell-slc6",
                "cannonlake-slc5",
                "skylake_avx512-slc5",
                "skylake-slc5",
                "broadwell-slc5",
                "haswell-slc5",
            ],
        ),
        (
            "x86_64-slc6.avx2+fma",
            True,
            [
                "cannonlake-slc6",
                "skylake_avx512-slc6",
                "skylake-slc6",
                "broadwell-slc6",
                "haswell-slc6",
            ],
        ),
    ],
)
def test_getDIRACPlatform(platform, expectedRes, expectedValue):
    res = getDIRACPlatform(platform)
    assert res["OK"] is expectedRes
    if res["OK"]:
        assert set(expectedValue).issubset(set(res["Value"])) is True

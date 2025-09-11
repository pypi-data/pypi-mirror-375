# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Test suite for progress counters (lima2/client/progress_counter.py)"""

from lima2.client import progress_counter
from lima2.client.progress_counter import SingleCounter


def test_aggregate_single():
    """Nominal case"""
    single_counters = [
        SingleCounter(name="my_counter", value=42, source="id00/some/device")
    ]

    counter = progress_counter.aggregate(single_counters=single_counters)

    assert counter.name == "my_counter"
    assert counter.sum == 42
    assert counter.min == 42
    assert counter.max == 42
    assert counter.avg == 42


def test_aggregate_multiple():
    """Nominal case"""
    single_counters = [
        SingleCounter(name="my_counter", value=42, source="id00/some/device"),
        SingleCounter(name="also_my_counter", value=43, source="id00/some/device"),
    ]

    counter = progress_counter.aggregate(single_counters=single_counters)

    assert counter.name == "my_counter"
    assert counter.sum == 42 + 43
    assert counter.min == 42
    assert counter.max == 43
    assert counter.avg == (42 + 43) / 2

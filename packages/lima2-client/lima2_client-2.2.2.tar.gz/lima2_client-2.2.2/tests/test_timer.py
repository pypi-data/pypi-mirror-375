# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Test suite for the async timer module (lima2/server/timer.py)"""

import gevent
from lima2.server.timer import Timer

hub = gevent.get_hub()


def test_timer():
    last_count = 0

    def callback(count):
        nonlocal last_count
        last_count = count

    _ = Timer(callback, 0.01, 10)

    hub.join()

    assert last_count == 10

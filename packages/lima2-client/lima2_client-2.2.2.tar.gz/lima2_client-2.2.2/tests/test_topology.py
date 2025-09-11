# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Test suite for topology logic (lima2/client/topology.py)"""

from unittest.mock import Mock

import pytest
import tango as tg

from lima2.client import topology
from lima2.client.topology import (
    RoundRobinTopology,
    SingleTopology,
    TopologyKind,
    UnevenTopology,
)


def test_distribute_acq():
    """Param handling for homogeneous distribution of acquisition

    Case where the number of frames wanted isn't a multiple of the
    number of receivers -> it should be rounded up to the nearest
    multiple.
    """
    num_rcv = 4

    ctl_params = {"acq": {"nb_frames": 16}}
    acq_params = {
        "acq": {"nb_frames": 16},
        "saving": {"filename_rank": 0},
    }
    proc_params = {
        "class_name": "LimaProcessingLegacy",
        "saving": {"filename_rank": "cafedeca"},
    }

    ctl, acq, proc = topology.distribute_acq(
        ctl_params=ctl_params,
        acq_params=acq_params,
        proc_params=proc_params,
        num_receivers=num_rcv,
    )

    for i in range(num_rcv):
        # Filename rank has been diversified
        assert proc[i]["saving"]["filename_rank"] == i
        assert acq[i]["saving"]["filename_rank"] == i


def test_topology_kind():
    with pytest.raises(ValueError):
        _ = TopologyKind("cafedeca")


###############################################################################
# Topology subclasses
###############################################################################


class MockFrame(Mock):
    def __init__(self, frame_idx: int):
        super().__init__(spec=bytes)
        self.frame_idx = frame_idx


mock_frames = [MockFrame(frame_idx=i) for i in range(8)]


def mock_getFrame(rcv_idx: int):
    """Generate a getFrame function given a receiver index."""

    def getFrame(frame_idx: int):
        frame = mock_frames[frame_idx]
        frame.rcv_idx = rcv_idx
        return frame

    return getFrame


def test_single_lookup():
    topo = SingleTopology()

    getters = [mock_getFrame(rcv_idx=0)]

    # Just run the function (nothing to assert in particular)
    topo.lookup(frame_idx=0, getters=getters)

    # No getters -> no frame
    with pytest.raises(IndexError):
        topo.lookup(frame_idx=0, getters=[])


def test_round_robin_lookup():
    num_receivers = 4
    getters = [mock_getFrame(rcv_idx=i) for i in range(num_receivers)]

    # Monotonic ordering
    topo = RoundRobinTopology(num_receivers=num_receivers, ordering=[0, 1, 2, 3])
    assert topo.lookup(frame_idx=0, getters=getters).rcv_idx == 0
    assert topo.lookup(frame_idx=1, getters=getters).rcv_idx == 1
    assert topo.lookup(frame_idx=2, getters=getters).rcv_idx == 2
    assert topo.lookup(frame_idx=3, getters=getters).rcv_idx == 3
    assert topo.lookup(frame_idx=4, getters=getters).rcv_idx == 0

    # Non-monotonic ordering
    topo = RoundRobinTopology(num_receivers=4, ordering=[1, 3, 2, 0])
    assert topo.lookup(frame_idx=0, getters=getters).rcv_idx == 1
    assert topo.lookup(frame_idx=1, getters=getters).rcv_idx == 3
    assert topo.lookup(frame_idx=2, getters=getters).rcv_idx == 2
    assert topo.lookup(frame_idx=3, getters=getters).rcv_idx == 0
    assert topo.lookup(frame_idx=4, getters=getters).rcv_idx == 1


def mock_uneven_getFrame(rcv_idx: int, num_rcv: int):
    """Generate a getFrame function which raises if the receiver does not hold the frame."""

    def getFrame(frame_idx: int):
        if frame_idx % num_rcv != rcv_idx:
            raise tg.DevFailed()
        elif frame_idx >= len(mock_frames):
            raise tg.DevFailed()
        else:
            frame = mock_frames[frame_idx]
            frame.rcv_idx = rcv_idx
            return frame

    return getFrame


def test_uneven_lookup():
    num_receivers = 3
    getters = [
        mock_uneven_getFrame(rcv_idx=i, num_rcv=num_receivers)
        for i in range(num_receivers)
    ]

    topo = UnevenTopology(num_receivers=num_receivers)
    assert topo.lookup(frame_idx=0, getters=getters).rcv_idx == 0
    assert topo.lookup(frame_idx=1, getters=getters).rcv_idx == 1
    assert topo.lookup(frame_idx=2, getters=getters).rcv_idx == 2
    assert topo.lookup(frame_idx=3, getters=getters).rcv_idx == 0
    assert topo.lookup(frame_idx=4, getters=getters).rcv_idx == 1

    # Check that if no receiver holds a given frame, lookup raises
    with pytest.raises(IndexError):
        topo.lookup(frame_idx=len(mock_frames), getters=getters)

# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT license. See LICENSE for more info.

"""Test suite for pipeline module (lima2/client/pipeline.py)"""

import json
from collections import namedtuple
from dataclasses import dataclass
from unittest.mock import Mock
from uuid import uuid1

import numpy as np
import pytest
import tango

from lima2.client import pipeline, progress_counter
from lima2.client.pipeline import FrameSource, FrameType, Pipeline
from lima2.client.pipelines.smx import Smx
from lima2.client.pipelines.xpcs import Xpcs
from lima2.client.topology import TopologyKind

from .mock_devencoded import (
    fill_factors_frame,
    peak_counters_frame,
    roi_profiles_frame,
    roi_stats_frame,
)


@pytest.fixture
def processing_devices():
    class MockProcessingDevice(tango.DeviceProxy):
        """Mock Processing tango device

        Using Mock with spec=tango.DeviceProxy is not sufficient: trying to assign
        return values for e.g. popRoiStatistics() will raise an AttributeError because
        the method isn't defined by tango.DeviceProxy (instead found dynamically at
        call-time).
        """

        def popRoiStatistics(self):
            pass

        def popRoiProfiles(self):
            pass

        def getFrame(self, frame_idx: int):
            pass

        def popPeakCounters(self):
            pass

        def popFillFactors(self):
            pass

        @property
        def progress_counters(self):
            pass

    proc_devs = [Mock(spec=MockProcessingDevice) for _ in range(2)]
    for i, dev in enumerate(proc_devs):
        dev.name.return_value = f"MockProc{i}"

    return proc_devs


def test_constructor_no_devices():
    """Construct a Pipeline object with no processing devices."""
    with pytest.raises(ValueError):
        _ = Pipeline(
            uuid=uuid1(),
            proc_devs=[],
            topology_kind=TopologyKind.ROUND_ROBIN,
            timeout=10,
        )


def test_constructor_single(processing_devices):
    """Construct a single-receiver Pipeline object."""
    _ = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices[:1],
        topology_kind=TopologyKind.SINGLE,
        timeout=10,
    )


def test_constructor_uneven(processing_devices):
    """Construct an Pipeline object with uneven topology."""
    _ = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices[:1],
        topology_kind=TopologyKind.UNEVEN,
        timeout=10,
    )


def test_bad_subclass():
    with pytest.raises(ValueError):

        class NoFrameSourcePipeline(Pipeline):
            tango_class = "badcafe"
            # Missing FRAME_SOURCES

    with pytest.raises(ValueError):

        class NoTangoClassPipeline(Pipeline):
            FRAME_SOURCES = {}
            # Missing tango_class


def test_progress_counters(processing_devices):
    """Read progress_counters."""
    processing_devices[0].progress_counters = json.dumps(
        {
            "cool_counter": 42,
            "nice_counter": 4,
            "evil_counter": -13,
        }
    )
    processing_devices[1].progress_counters = json.dumps(
        {
            "cool_counter": 43,
            "nice_counter": 3,
            "evil_counter": -37,
        }
    )

    proc = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices[:1],
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    pc = proc.progress_counters

    assert len(pc) == 3
    assert set(pc.keys()) == {
        "cool_counter",
        "nice_counter",
        "evil_counter",
    }


def test_cache_byproduct_limit(processing_devices):
    """Check cached entries are discarded when cache is too large."""
    proc = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices,
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    # Force the pipeline to cache too many entries
    # Assume our byproduct has multiple values per frame (like roi profiles)
    # Simulate a situation where one receiver is not yielding anything
    rows_per_frame = 4
    data = np.array(
        [
            (i * 2, j + i * 10.0)
            for i in range(proc.BYPRODUCT_CACHE_LIMIT + 2)
            for j in range(rows_per_frame)
        ],
        dtype=[("frame_idx", np.int32), ("overflowing_factor", np.float32)],
    )
    proc.cache_byproduct(key="overflowing_factors", data=data)

    # The cache is at its max size
    assert (
        proc.byproduct_cache["overflowing_factors"].size
        == proc.BYPRODUCT_CACHE_LIMIT * rows_per_frame
    )

    # data from frames 0 and 2 has been discarded
    assert (proc.byproduct_cache["overflowing_factors"]["frame_idx"] <= 2).sum() == 0


def test_nb_roi_statistics(processing_devices):
    """Aggregation of nb_roi_statistics."""
    processing_devices[0].nb_roi_statistics = 42
    processing_devices[1].nb_roi_statistics = 44

    proc = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices,
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    assert proc.nb_roi_statistics.counters == [
        progress_counter.SingleCounter(
            name="nb_roi_statistics",
            value=dev.nb_roi_statistics,
            source=dev.name(),
        )
        for dev in processing_devices
    ]


def test_nb_roi_profiles(processing_devices):
    """Aggregation of nb_roi_profiles."""
    processing_devices[0].nb_roi_profiles = 13
    processing_devices[1].nb_roi_profiles = 37

    proc = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices,
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    assert proc.nb_roi_profiles.counters == [
        progress_counter.SingleCounter(
            name="nb_roi_profiles",
            value=dev.nb_roi_profiles,
            source=dev.name(),
        )
        for dev in processing_devices
    ]


def test_pop_roi_statistics_empty(processing_devices):
    # Let popRoiStatistics return an empty payload on both devices
    processing_devices[0].popRoiStatistics.side_effect = [
        roi_stats_frame(num_frames=0, num_receivers=2, start_idx=0)
    ]
    processing_devices[1].popRoiStatistics.side_effect = [
        roi_stats_frame(num_frames=0, num_receivers=2, start_idx=0)
    ]

    proc = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices,
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    assert proc.pop_roi_statistics() == []


def test_pop_roi_statistics(processing_devices):
    """Decoding and caching of roi statistics.

    The two processing devices will return different number of roi stats at each call to
    popRoiStatistics(). The goal is to check that the caching works as expected, i.e.
    the return value is the concatenation of cached values with new values, in frame order,
    without any discontinuity.
    """

    # Dev 0 will return 3 stats on the first pop, then 2, then 2
    # 1. frames 0, 2, 4
    # 2. frames 6, 8
    # 3. frames 10, 12, 14
    # 4. no frame
    # 5. no frame
    processing_devices[0].popRoiStatistics.side_effect = [
        roi_stats_frame(num_frames=3, num_receivers=2, start_idx=0),
        roi_stats_frame(num_frames=2, num_receivers=2, start_idx=6),
        roi_stats_frame(num_frames=3, num_receivers=2, start_idx=10),
        roi_stats_frame(num_frames=0, num_receivers=2, start_idx=16),
        roi_stats_frame(num_frames=0, num_receivers=2, start_idx=16),
    ]
    # Dev 1 will return 1 stats on the first pop, then 6, then 0
    # 1. frame 1
    # 2. frames 3, 5, 7, 9, 11, 13
    # 3. no frame
    # 4. frame 15 (final)
    # 5. no frame

    processing_devices[1].popRoiStatistics.side_effect = [
        roi_stats_frame(num_frames=1, num_receivers=2, start_idx=1),
        roi_stats_frame(num_frames=6, num_receivers=2, start_idx=3),
        roi_stats_frame(num_frames=0, num_receivers=2, start_idx=15),
        roi_stats_frame(num_frames=1, num_receivers=2, start_idx=15),
        roi_stats_frame(num_frames=0, num_receivers=2, start_idx=15),
    ]

    proc = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices,
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    # First pop -> receiver 0 is ahead by 2 frames
    # We should get stats for frames 0 to 2
    # (= 3 stats, 2 from receiver 0 and 1 from receiver 1)
    # and proc should cache the stats for frame 4.
    s1 = proc.pop_roi_statistics()

    assert len(s1) == 1  # 1 roi
    assert len(s1[0][0]) == 3  # 3 frames
    assert max(s1[0][0]) == 2  # First missing frame == 3
    assert (
        proc.byproduct_cache["roi_statistics"]["frame_idx"] == [4]
    ).all()  # Frame 4 in cache

    # Second pop -> now receiver 1 is ahead by 2 frames
    s2 = proc.pop_roi_statistics()

    assert max(s2[0][0]) == 9  # First missing frame == 10
    assert (
        proc.byproduct_cache["roi_statistics"]["frame_idx"].flatten() == [11, 13]
    ).all()  # Frames (11, 13) cached

    # Third pop -> receiver 0 gets the two missing frames, receiver 1 yields 0
    s3 = proc.pop_roi_statistics()

    assert max(s3[0][0]) == 14  # First missing frame == 15
    assert proc.byproduct_cache["roi_statistics"].size == 0  # Nothing cached

    # Fourth pop -> receiver 0 gets no frame, receiver 1 gets 1
    s4 = proc.pop_roi_statistics()

    assert max(s4[0][0]) == 15  # 16 frames acquired in total (8 / receiver)
    assert proc.byproduct_cache["roi_statistics"].size == 0  # No cache

    # Last pop -> No more data is arriving on either receiver -> no change from previous state
    s5 = proc.pop_roi_statistics()

    assert s5 == []  # No new data
    assert proc.byproduct_cache["roi_statistics"].size == 0  # No cache


def test_pop_roi_profiles_empty(processing_devices):
    roi_lengths = [17, 24]
    # Let popRoiProfiles return an empty payload on both devices
    processing_devices[0].popRoiProfiles.side_effect = [
        roi_profiles_frame(
            num_frames=0, num_receivers=2, start_idx=0, roi_lengths=roi_lengths
        )
    ]
    processing_devices[1].popRoiProfiles.side_effect = [
        roi_profiles_frame(
            num_frames=0, num_receivers=2, start_idx=0, roi_lengths=roi_lengths
        )
    ]

    proc = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices,
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    assert proc.pop_roi_profiles(roi_lengths=roi_lengths) == []


def test_pop_roi_profiles(processing_devices):
    """Decoding and caching of roi profiles.

    Similar to test_pop_roi_statistics().
    """

    roi_lengths = [10, 5]

    # Dev 0 will return 3 stats on the first pop, then 1
    # 1. frames 0, 2, 4
    # 2. frame 6
    processing_devices[0].popRoiProfiles.side_effect = [
        roi_profiles_frame(
            num_frames=3, num_receivers=2, start_idx=0, roi_lengths=roi_lengths
        ),
        roi_profiles_frame(
            num_frames=1, num_receivers=2, start_idx=6, roi_lengths=roi_lengths
        ),
    ]

    # Dev 1 will return 1 stats on the first pop, then 3
    # 1. frame 1
    # 2. frames 3, 5, 7
    processing_devices[1].popRoiProfiles.side_effect = [
        roi_profiles_frame(
            num_frames=1, num_receivers=2, start_idx=1, roi_lengths=roi_lengths
        ),
        roi_profiles_frame(
            num_frames=3, num_receivers=2, start_idx=3, roi_lengths=roi_lengths
        ),
    ]

    proc = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices,
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    # First pop -> 3 frames available
    s1 = proc.pop_roi_profiles(roi_lengths=roi_lengths)

    assert len(s1) == 2  # 2 rois
    assert len(s1[0][0]) == 3  # 3 frames

    for roi_idx in range(len(roi_lengths)):
        # Number of elements is roi_length * num_frames
        assert s1[roi_idx][1].size == len(s1[roi_idx][0]) * roi_lengths[roi_idx]

    assert max(s1[0][0]) == 2  # First missing frame == 3
    assert (
        proc.byproduct_cache["roi_profiles"]["frame_idx"] == [4]
    ).all()  # Frame 4 in cache

    # Second pop -> 5 new frames available (3, 4, 5, 6, 7)
    s2 = proc.pop_roi_profiles(roi_lengths=roi_lengths)

    assert len(s2[0][0]) == 5  # 5 new frames

    for roi_idx in range(len(roi_lengths)):
        # Number of elements is roi_length * num_frames
        assert s1[roi_idx][1].size == len(s1[roi_idx][0]) * roi_lengths[roi_idx]

    assert max(s2[0][0]) == 7  # All frames received up to 7
    assert proc.byproduct_cache["roi_profiles"].size == 0  # No cache


def test_get_frame(processing_devices, monkeypatch):
    proc = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices,
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    @dataclass
    class MockFrame:
        idx: int
        data: bytes

    # Mock FRAME_SOURCES (normally defined by Pipeline subclass)
    proc.FRAME_SOURCES = {
        "cafedeca": FrameSource(
            getter_name="getFrame",
            frame_type=FrameType.DENSE,
            saving_channel=None,
        ),
        "sparse": FrameSource(
            getter_name="getSparseFrame",
            frame_type=FrameType.SPARSE,
            saving_channel=None,
        ),
    }

    def mock_decode(data: bytes):
        return MockFrame(data[0], data[1:])

    # Modify the decoder_by_type map to plug our mock decode function
    # No decoder for SPARSE frame so we can test the case where the decoder is not implemented
    monkeypatch.setattr(pipeline, "decoder_by_type", {FrameType.DENSE: mock_decode})

    with pytest.raises(NotImplementedError):
        proc.get_frame(0, source="sparse")

    rcv_0_frames = {
        0: b"\x00milk",
        -1: b"\x02milk",
    }
    rcv_1_frames = {
        1: b"\x01cookies",
        -1: b"\x03cookies",
    }

    processing_devices[0].getFrame.side_effect = lambda idx: rcv_0_frames.get(idx)
    processing_devices[1].getFrame.side_effect = lambda idx: rcv_1_frames.get(idx)

    with pytest.raises(ValueError):
        proc.get_frame(0, source="deadbeef")

    # get_frame(0) should yield the first frame from receiver 0 (using round robin)
    frame_0 = proc.get_frame(0, source="cafedeca")
    assert type(frame_0) is MockFrame
    assert frame_0.idx == 0
    assert frame_0.data == b"milk"

    frame_1 = proc.get_frame(1, source="cafedeca")
    assert type(frame_1) is MockFrame
    assert frame_1.idx == 1
    assert frame_1.data == b"cookies"

    # Ensure frame -1 yields the frame with the greatest frame idx
    frame_last = proc.get_frame(-1, source="cafedeca")
    assert type(frame_last) is MockFrame
    assert frame_last.idx == 3
    assert frame_last.data == b"cookies"

    def getFrameEmpty():
        """Simulate a receiver that has no frames to get"""
        raise tango.DevFailed("no frames sorry")

    # If receiver 1 has no frames, get_frame(-1) should return the last frame from receiver 0
    processing_devices[1].getFrame.side_effect = lambda _: getFrameEmpty()

    assert proc.get_frame(-1, source="cafedeca").idx == 2

    # If both receivers have no frames, get_frame(-1) should raise
    processing_devices[0].getFrame.side_effect = lambda _: getFrameEmpty()
    processing_devices[1].getFrame.side_effect = lambda _: getFrameEmpty()

    with pytest.raises(ValueError):
        proc.get_frame(-1, source="cafedeca")


def test_smx_peak_counters(processing_devices):
    processing_devices[0].popPeakCounters.side_effect = [
        peak_counters_frame(num_frames=3, num_receivers=2, start_idx=0),
    ]
    processing_devices[1].popPeakCounters.side_effect = [
        peak_counters_frame(num_frames=1, num_receivers=2, start_idx=1),
    ]

    proc = Smx(
        uuid=uuid1(),
        proc_devs=processing_devices,
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    # Receiver 0 yields 3 frames, versus 1 frame for receiver 1.
    # -> pop returns data for frames 0, 1 and 2
    s1 = proc.pop_peak_counters()
    assert np.all(s1[0] == [0, 1, 2])
    assert np.all(s1[1] == [1337 * 0, 1337 * 1, 1337 * 2])

    # Frame 4 is cached
    cached = proc.get_cached_byproduct("peak_counters", np.array([]))
    assert np.all(cached["frame_idx"] == [4])
    assert np.all(cached["nb_peaks"] == [1337 * 4])


def test_xpcs_fill_factors(processing_devices):
    processing_devices[0].popFillFactors.side_effect = [
        fill_factors_frame(num_frames=1, num_receivers=2, start_idx=0),
    ]
    processing_devices[1].popFillFactors.side_effect = [
        fill_factors_frame(num_frames=3, num_receivers=2, start_idx=1),
    ]

    proc = Xpcs(
        uuid=uuid1(),
        proc_devs=processing_devices,
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    # Receiver 1 yields 3 frames, versus 1 frame for receiver 0.
    # -> pop returns data for frames 0, and 1
    s1 = proc.pop_fill_factors()
    assert np.all(s1[0] == [0, 1])
    assert np.all(s1[1] == [1337 * 0, 1337 * 1])

    # Frames 3 and 5 are cached
    cached = proc.get_cached_byproduct("fill_factors", np.array([]))
    assert np.all(cached["frame_idx"] == [3, 5])
    assert np.all(cached["fill_factor"] == [1337 * 3, 1337 * 5])


################################################################################
# Callback tests
################################################################################


MockEvent = namedtuple("MockEvent", ["device", "err", "errors"])
MockEventError = namedtuple("MockEventError", ["desc"])


class EventMan:
    """Event manager: register and call callbacks."""

    def __init__(self):
        self.callbacks = {}

    def register(self, device, callback):
        self.callbacks[device] = callback

    def call(self, device):
        event = MockEvent(device=device, err=False, errors=[])
        self.callbacks[device](event)

    def call_err(self, device):
        event = MockEvent(
            device=device,
            err=True,
            errors=[
                MockEventError(desc="no"),
                MockEventError(desc="bueno"),
            ],
        )
        self.callbacks[device](event)


@pytest.fixture
def event_man():
    return EventMan()


def test_register_on_finished(processing_devices, event_man):
    """Test the callback behaviour of Pipeline.register_on_finished()"""

    processing_devices[
        0
    ].subscribe_event.side_effect = lambda name, type, callback: event_man.register(
        processing_devices[0], callback
    )
    processing_devices[
        1
    ].subscribe_event.side_effect = lambda name, type, callback: event_man.register(
        processing_devices[1], callback
    )

    proc = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices,
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    # Flag for pipelines on all receivers finished
    all_finished = False

    def on_finished():
        nonlocal all_finished
        all_finished = True

    proc.register_on_finished(on_finished=on_finished)
    assert len(event_man.callbacks) == 2

    # All devices need to be finished for the on_finished callback to be called
    event_man.call(processing_devices[0])
    assert not all_finished
    event_man.call(processing_devices[1])
    assert all_finished

    processing_devices[0].unsubscribe_event.assert_called_once()
    processing_devices[1].unsubscribe_event.assert_called_once()

    processing_devices[0].reset_mock()

    # Call with the error flag (simulates disconnect)
    event_man.call_err(processing_devices[0])
    processing_devices[0].unsubscribe_event.assert_called_once()


def test_register_on_error(processing_devices, event_man):
    """Test the callback behaviour of Pipeline.register_on_error()"""

    processing_devices[
        0
    ].subscribe_event.side_effect = lambda name, type, callback: event_man.register(
        processing_devices[0], callback
    )
    processing_devices[
        1
    ].subscribe_event.side_effect = lambda name, type, callback: event_man.register(
        processing_devices[1], callback
    )

    proc = Pipeline(
        uuid=uuid1(),
        proc_devs=processing_devices,
        topology_kind=TopologyKind.ROUND_ROBIN,
        timeout=10,
    )

    errored_devices = set()

    def on_error(evt):
        nonlocal errored_devices
        errored_devices.add(evt.device)

    proc.register_on_error(cbk=on_error)
    assert len(event_man.callbacks) == 2

    # All devices need to be finished for the on_finished callback to be called
    event_man.call(processing_devices[0])
    assert errored_devices == {processing_devices[0]}
    event_man.call(processing_devices[1])
    assert errored_devices == set(processing_devices)

    processing_devices[0].unsubscribe_event.assert_called_once()
    processing_devices[1].unsubscribe_event.assert_called_once()

    processing_devices[1].reset_mock()

    # Call with the error flag (simulates disconnect)
    event_man.call_err(processing_devices[1])
    processing_devices[1].unsubscribe_event.assert_called_once()

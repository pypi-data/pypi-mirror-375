# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Test suite for the sparse_frame module (lima2/client/devencoded/sparse_frame.py)"""

import struct

import numpy as np
import pytest

from lima2.client.devencoded import sparse_frame
from lima2.client.devencoded.exception import DevEncodedFormatNotSupported


def test_decode_invalid_type():
    with pytest.raises(DevEncodedFormatNotSupported):
        sparse_frame.decode(raw_data=("DEADBEEF", b"cafedeca"))


def encode(
    width=256,
    height=256,
    nb_pixels=4000,
    frame_idx=0,
    index=None,
    intensity=None,
):
    """Encode a frame as if it came out of recv.getSparseFrame()"""

    header_data = struct.pack(
        sparse_frame.DATA_HEADER_FORMAT,
        width,
        height,
        nb_pixels,
        frame_idx,
    )

    if index is None:
        index = np.random.choice(width * height, size=nb_pixels, replace=False)

    if intensity is None:
        intensity = np.random.randint(
            low=0, high=np.iinfo(np.int16).max, size=nb_pixels, dtype=np.int16
        )

    return header_data + index.tobytes() + intensity.tobytes()


def noisy_frame(data_type, dim1, dim2, dim3):
    # If data_type is not valid, use a default numpy dtype
    # This allows a test to set a bad data_type in the header
    try:
        dtype = sparse_frame.MODE_TO_NUMPY[sparse_frame.IMAGE_MODES(data_type)]
    except (ValueError, KeyError):
        dtype = np.float32

    return (
        (np.random.random_sample(size=(dim3, dim2, dim1)) * 10)
        .astype(dtype=dtype)
        .tobytes()
    )


def test_decode_ok():
    data = encode()
    _ = sparse_frame.decode(raw_data=data)


def test_decode_tuple():
    data = encode()
    _ = sparse_frame.decode(raw_data=("SPARSE_FRAME", data))


def test_encode_bad_tuple():
    data = encode()
    with pytest.raises(DevEncodedFormatNotSupported):
        _ = sparse_frame.decode(raw_data=("DEAD_BEEF", data))


def test_is_empty():
    frame = sparse_frame.SparseFrame(
        index=np.ones(64, dtype=np.int32),
        intensity=np.ones(64) * 0.5,
        idx=0,
        shape=(32, 32),
    )
    assert frame


def test_densify():
    shape = (32, 32)
    index = np.random.choice(32 * 32, size=64, replace=False)
    intensity = np.random.randint(low=1, high=1337, size=64, dtype=np.int16)

    frame = sparse_frame.SparseFrame(
        index=index,
        intensity=intensity,
        idx=1337,
        shape=shape,
    )

    dense = frame.densify()

    assert dense.data.dtype == intensity.dtype
    assert (dense.data.flat[index] == intensity).all()
    assert dense.data.shape == frame.shape
    assert dense.idx == frame.idx

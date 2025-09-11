# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Test suite for the dense_frame module (lima2/client/devencoded/dense_frame.py)"""

import struct

import numpy as np
import pytest

from lima2.client.devencoded import dense_frame
from lima2.client.devencoded.exception import DevEncodedFormatNotSupported


def encode(
    magic=dense_frame.DATA_MAGIC,
    version=1,
    header_size=dense_frame.DATA_HEADER_SIZE,
    category=0,
    data_type=0,
    endianness=0,
    nb_dim=3,
    dim1=2,
    dim2=3,
    dim3=4,
    dim4=1,
    dim5=1,
    dim6=1,
    dim_step1=1,
    dim_step2=1,
    dim_step3=1,
    dim_step4=1,
    dim_step5=1,
    dim_step6=1,
    frame_idx=0,
    frame_data=None,
):
    """Encode a frame as if it came out of recv.getFrame()"""

    header_data = struct.pack(
        dense_frame.DATA_HEADER_FORMAT,
        magic,
        version,
        header_size,
        category,
        data_type,
        endianness,
        nb_dim,
        dim1,
        dim2,
        dim3,
        dim4,
        dim5,
        dim6,
        dim_step1,
        dim_step2,
        dim_step3,
        dim_step4,
        dim_step5,
        dim_step6,
        frame_idx,
    )

    if frame_data is None:
        frame_data = noisy_frame(data_type, dim1, dim2, dim3)

    return header_data + frame_data


def noisy_frame(data_type, dim1, dim2, dim3):
    """Generate frame data from random noise"""

    # If data_type is not valid, use a default numpy dtype
    # This allows a test to set a bad data_type in the header
    try:
        dtype = dense_frame.MODE_TO_NUMPY[dense_frame.IMAGE_MODES(data_type)]
    except (ValueError, KeyError):
        dtype = np.float32

    return (
        (np.random.random_sample(size=(dim3, dim2, dim1)) * 10)
        .astype(dtype=dtype)
        .tobytes()
    )


def test_decode_invalid_type():
    with pytest.raises(DevEncodedFormatNotSupported):
        dense_frame.decode(raw_data=("DEADBEEF", b"cafedeca"))


def test_decode_ok():
    data = encode()
    _ = dense_frame.decode(raw_data=data)


def test_decode_tuple():
    data = encode()
    _ = dense_frame.decode(raw_data=("DENSE_FRAME", data))


def test_encode_bad_tuple():
    data = encode()
    with pytest.raises(DevEncodedFormatNotSupported):
        _ = dense_frame.decode(raw_data=("DEAD_BEEF", data))


def test_decode_bad_magic():
    data = encode(magic=struct.unpack(">I", b"CAFE")[0])
    with pytest.raises(DevEncodedFormatNotSupported):
        _ = dense_frame.decode(raw_data=data)


def test_decode_bad_version():
    data = encode(version=0)
    with pytest.raises(DevEncodedFormatNotSupported):
        _ = dense_frame.decode(raw_data=data)


def test_decode_bad_dtype():
    data = encode(data_type=1337)
    with pytest.raises(DevEncodedFormatNotSupported):
        _ = dense_frame.decode(raw_data=data)


def test_decode_bad_endianness():
    data = encode(endianness=1)
    with pytest.raises(DevEncodedFormatNotSupported):
        _ = dense_frame.decode(raw_data=data)


def test_decode_bad_nb_dim():
    data = encode(nb_dim=4)
    with pytest.raises(DevEncodedFormatNotSupported):
        _ = dense_frame.decode(raw_data=data)


def test_decode_bad_frame_size():
    """The frame shape given in the header is not equal to the actual frame shape"""
    data_type = dense_frame.IMAGE_MODES.DARRAY_FLOAT32
    dtype = dense_frame.MODE_TO_NUMPY[data_type]
    frame_data = np.random.random_sample(size=(2, 3, 5)).astype(dtype=dtype).tobytes()

    data = encode(
        data_type=data_type.value,
        dim1=2,
        dim2=3,
        dim3=4,
        frame_data=frame_data,
    )
    # Frame cannot be reshaped by numpy
    with pytest.raises(ValueError):
        dense_frame.decode(raw_data=data)

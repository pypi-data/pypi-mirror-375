# This file is part of the Lima2 project
#
# Copyright (c) 2020-2024 Beamline Control Unit, ESRF
# Distributed under the MIT licence. See LICENSE for more info.

"""Test suite for the convert module (lima2/client/convert.py)"""

import numpy as np
import pytest
from lima2.client.convert import frame_info_to_shape_dtype


def test_frame_info_to_shape_dtype():
    shape_dtype = frame_info_to_shape_dtype(
        frame_info={
            "nb_channels": 3,
            "dimensions": {
                "x": 64,
                "y": 32,
            },
            "pixel_type": "gray32",
        }
    )
    assert shape_dtype["shape"] == (3, 32, 64)
    assert shape_dtype["dtype"] == np.uint32


def test_frame_info_to_shape_dtype_bad_type():
    with pytest.raises(KeyError):
        frame_info_to_shape_dtype(
            frame_info={
                "nb_channels": 3,
                "dimensions": {
                    "x": 32,
                    "y": 64,
                },
                "pixel_type": "cafedeca",
            }
        )

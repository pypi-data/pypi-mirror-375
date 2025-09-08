# Copyright (c) AIoWay Authors - All Rights Reserved

import random

import pytest

from aioway.ops import FrameOp
from tests import fake


def test_block_frame_len(block_frame):
    assert len(block_frame) == max(fake.block_sizes())


def test_block_frame_getitem(block_frame):
    idx = random.randrange(len(block_frame))
    assert isinstance(idx, int)

    assert (block_frame[idx].data == block_frame.block.data[idx]).all()
    assert not block_frame[idx].batch_dims


@pytest.fixture
def block_frame_op(block_frame, size, num_workers):
    return FrameOp(block_frame, {"batch_size": size, "num_workers": num_workers})


@pytest.fixture
def another_block_frame_op(block_frame, size, num_workers):
    return FrameOp(block_frame, {"batch_size": size, "num_workers": num_workers})


def test_frame_iter_is_new(block_frame_op):
    # Ensure that everytime it is called, a new iterator is produced.
    iterable = block_frame_op.it()
    assert iter(iterable) is not iter(iterable)


def test_frame_iter_is_clone(block_frame_op):
    for left, right in zip(block_frame_op.it(), block_frame_op.it()):
        assert (left.data == right.data).all()
        assert left is not right


def test_iterator_eq(block_frame_op, another_block_frame_op):
    for left, right in zip(block_frame_op.it(), another_block_frame_op.it()):
        assert (left.data == right.data).all()

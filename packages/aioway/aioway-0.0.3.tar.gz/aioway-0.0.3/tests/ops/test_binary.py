# Copyright (c) AIoWay Authors - All Rights Reserved

from collections import Counter

import pytest
import tensordict
from tensordict import TensorDict

from aioway.blocks import Block
from aioway.ops import FrameOp, MatchOp, ZipOp


@pytest.fixture
def concat_frame_op(concat_frame, size, num_workers):
    return FrameOp(concat_frame, {"batch_size": size, "num_workers": num_workers})


@pytest.fixture
def block_frame_op(block_frame, size, num_workers):
    return FrameOp(block_frame, {"batch_size": size, "num_workers": num_workers})


@pytest.fixture
def joinable_frame_op(joinable_frame, size, num_workers):
    return FrameOp(joinable_frame, {"batch_size": size, "num_workers": num_workers})


@pytest.fixture
def match_op():
    return MatchOp(key="i1d")


def combine_results(results: list[Block], /) -> TensorDict:
    data = [result.data for result in results]
    return tensordict.cat(data)


def test_zip_input_len(block_frame, concat_frame):
    assert len(block_frame) == len(concat_frame)


def test_zip(block_frame_op, concat_frame_op):
    stream = ZipOp().it(block_frame_op.it(), concat_frame_op.it())

    for result, lhs, rhs in zip(stream, block_frame_op.it(), concat_frame_op.it()):
        concat = TensorDict({**lhs.data, **rhs.data}, device=result.data.device)
        assert (result.data == concat).all()


def test_join_input_len(block_frame, joinable_frame):
    assert len(block_frame) * len(joinable_frame)


def test_match_is_reduction(match_op, block_frame_op, joinable_frame_op):
    stream = match_op.it(block_frame_op.it(), joinable_frame_op.it())
    block_frame_block = block_frame_op.dataset.block
    joinable_frame_block = joinable_frame_op.dataset.block

    # Performing the join here.
    results: list[Block] = list(stream)
    answer_items = combine_results(results)["i1d"]

    # Do it at once.
    ground_truth = match_op.join(block_frame_block, joinable_frame_block)

    answer_count = Counter(answer_items.tolist())
    truth_count = Counter(ground_truth.data["i1d"].tolist())

    assert answer_count == truth_count


def test_match_functionally_correct(match_op, block_frame_op, joinable_frame_op):
    stream = match_op.it(block_frame_op.it(), joinable_frame_op.it())
    block_frame_block = block_frame_op.dataset.block
    joinable_frame_block = joinable_frame_op.dataset.block

    # Performing the join here.
    results: list[Block] = list(stream)
    answer_items = combine_results(results)["i1d"]

    answer_count = Counter(answer_items.tolist())

    left_count = Counter(block_frame_block.data["i1d"].tolist())
    right_count = Counter(joinable_frame_block.data["i1d"].tolist())

    # Functionally correct join.
    assert left_count.keys() == {*block_frame_block.data["i1d"].tolist()}
    assert right_count.keys() == {*joinable_frame_block.data["i1d"].tolist()}
    assert answer_count.keys() == left_count.keys() & right_count.keys()

    for key in answer_count.keys():
        assert answer_count[key] == left_count[key] * right_count[key]

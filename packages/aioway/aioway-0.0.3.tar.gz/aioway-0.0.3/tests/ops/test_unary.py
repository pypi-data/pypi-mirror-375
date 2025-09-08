# Copyright (c) AIoWay Authors - All Rights Reserved

import pytest

from aioway.ops import (
    ExprFilterOp,
    FrameOp,
    FuncFilterOp,
    MapOp,
    Op,
    ProjectOp,
    RenameOp,
)


@pytest.fixture
def block_frame_op(block_frame, size, num_workers):
    return FrameOp(block_frame, {"batch_size": size, "num_workers": num_workers})


def filter_expr_exec():
    return ExprFilterOp("f1d > 0")


def filter_pred_frame():
    return FuncFilterOp(predicate=lambda t: (t["f1d"] > 0).cpu().numpy())


@pytest.fixture(params=[filter_expr_exec, filter_pred_frame])
def filter_op(request) -> Op:
    return request.param()


def test_filter(filter_op, block_frame_op):
    for filtered, original in zip(
        filter_op.it(block_frame_op.it()), block_frame_op.it()
    ):
        assert (filtered.data == original.filter("f1d > 0").data).all()


@pytest.fixture(scope="module")
def renames():
    return {"f1d": "f1", "f2d": "f2", "i1d": "i1", "i2d": "i2"}


def test_rename_exec_next(block_frame_op, renames):
    rename_op = RenameOp(renames)
    for renamed, original in zip(
        rename_op.it(block_frame_op.it()), block_frame_op.it()
    ):
        assert (
            renamed.data == original.rename(f1d="f1", f2d="f2", i1d="i1", i2d="i2").data
        ).all()


@pytest.fixture
def map_rename():
    return {"f1d": "f", "i1d": "i"}


def test_map_op(block_frame_op, map_rename):
    map_op = MapOp(compute=lambda b: b.rename(**map_rename))
    for mapped, original in zip(map_op.it(block_frame_op.it()), block_frame_op.it()):
        assert (mapped.data == original.rename(**map_rename).data).all()


def test_project_exec_next(block_frame_op):
    project_op = ProjectOp(subset=["f1d", "i2d"])
    for curr, other in zip(project_op.it(block_frame_op.it()), block_frame_op.it()):
        assert (curr.data == other[["f1d", "i2d"]].data).all()

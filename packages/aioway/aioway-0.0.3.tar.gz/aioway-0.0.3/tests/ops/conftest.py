# Copyright (c) AIoWay Authors - All Rights Reserved


import pytest

from aioway.frames import BlockFrame
from tests import fake


@pytest.fixture(params=fake.cpu_and_maybe_cuda(), scope="module")
def device(request) -> str:
    return request.param


@pytest.fixture(scope="module")
def num_workers() -> int:
    return 0


@pytest.fixture(params=fake.block_sizes(), scope="module")
def size(request) -> int:
    return request.param


@pytest.fixture(scope="module")
def block_frame(device) -> BlockFrame:
    block = fake.block_ok(size=max(fake.block_sizes()), device=device)
    return BlockFrame(block)


@pytest.fixture(scope="module")
def concat_frame(device) -> BlockFrame:
    block = fake.concat_block_ok(size=max(fake.block_sizes()), device=device)
    return BlockFrame(block)


@pytest.fixture(scope="module")
def joinable_frame(device):
    block = fake.unionable_block_ok(size=max(fake.block_sizes()), device=device)
    return BlockFrame(block)

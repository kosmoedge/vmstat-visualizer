import os
import pytest

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


@pytest.fixture
def active_log():
    return os.path.join(FIXTURES_DIR, "vmstat_active.log")


@pytest.fixture
def standard_log():
    return os.path.join(FIXTURES_DIR, "vmstat_standard.log")


@pytest.fixture
def no_header_log():
    return os.path.join(FIXTURES_DIR, "vmstat_no_header.log")

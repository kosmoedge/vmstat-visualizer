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


@pytest.fixture
def empty_log():
    return os.path.join(FIXTURES_DIR, "vmstat_empty.log")


@pytest.fixture
def header_only_log():
    return os.path.join(FIXTURES_DIR, "vmstat_header_only.log")


@pytest.fixture
def example_log():
    return os.path.join(
        os.path.dirname(__file__), "..", "examples", "example.log"
    )


@pytest.fixture
def example_standard_log():
    return os.path.join(
        os.path.dirname(__file__), "..", "examples", "example_standard.log"
    )

"""Tests for Elasticsearch ECS export helpers."""

import json
import sys
from types import ModuleType
from unittest.mock import MagicMock, patch

import pytest

from vmstat_visualizer.parser.timeseries import Timeseries


def _timeseries_metric_attr_names():
    """Attributes on Timeseries that represent exported metrics."""
    exclude = frozenset({"raw_data"})
    names = []
    ts = Timeseries()
    for name in vars(ts):
        if name.startswith("_") or name in exclude:
            continue
        names.append(name)
    return frozenset(names)


@pytest.fixture
def elasticsearch_fake():
    """Inject a stub ``elasticsearch`` package so exporter can import locally."""
    es_pkg = ModuleType("elasticsearch")
    helpers_pkg = ModuleType("elasticsearch.helpers")

    es_pkg.Elasticsearch = MagicMock(return_value=MagicMock(name="client"))
    helpers_pkg.bulk = MagicMock(return_value=(0, []))
    es_pkg.helpers = helpers_pkg

    with patch.dict(
        sys.modules,
        {
            "elasticsearch": es_pkg,
            "elasticsearch.helpers": helpers_pkg,
        },
    ):
        yield es_pkg


def test_ecs_field_map_covers_timeseries_metric_attrs():
    from vmstat_visualizer.es_exporter import ECS_FIELD_MAP

    expected = _timeseries_metric_attr_names()
    assert set(ECS_FIELD_MAP.keys()) == expected


def test_kb_fields_and_pct_fields_are_subsets():
    from vmstat_visualizer.es_exporter import ECS_FIELD_MAP, KB_FIELDS, PCT_FIELDS

    keys = set(ECS_FIELD_MAP)
    assert KB_FIELDS.issubset(keys)
    assert PCT_FIELDS.issubset(keys)


def test_to_ecs_doc_timestamp_and_transforms_and_event_fields():
    from vmstat_visualizer.es_exporter import _to_ecs_doc

    e = Timeseries()
    e.time = "2025-07-31 23:52:52"
    e.free_memory_kb = 100
    e.user_cpu_percent = 50
    e.interrupts = 12345
    e.context_switches = 987654

    doc = _to_ecs_doc(e, source_file=None)

    assert doc["@timestamp"] == "2025-07-31T23:52:52"
    assert doc["system.memory.free.bytes"] == 102400
    assert doc["system.cpu.user.pct"] == 0.5
    assert doc["system.cpu.interrupts"] == 12345
    assert doc["system.cpu.context_switches"] == 987654
    assert doc["event.module"] == "vmstat"
    assert doc["event.dataset"] == "system.vmstat"
    assert "file.path" not in doc


def test_to_ecs_doc_omits_none_and_includes_file_path():
    from vmstat_visualizer.es_exporter import _to_ecs_doc

    e = Timeseries()
    e.time = "2025-01-01 00:00:00"
    e.user_cpu_percent = 10

    doc = _to_ecs_doc(e, source_file="/logs/vm.csv")

    assert "@timestamp" in doc
    assert "system.cpu.user.pct" in doc
    assert doc["file.path"] == "/logs/vm.csv"


def test_build_bulk_body_ndjson_structure():
    from vmstat_visualizer.es_exporter import build_bulk_body

    e = Timeseries()
    e.time = "2025-07-31 01:02:03"
    e.run_queue = 1

    body = build_bulk_body([e], index="vmstat", source_file="/a.log")
    lines = body.splitlines()

    assert len(lines) == 2
    action = json.loads(lines[0])
    doc = json.loads(lines[1])

    assert action == {"index": {"_index": "vmstat"}}
    assert doc["event.module"] == "vmstat"
    assert doc["file.path"] == "/a.log"
    assert body.endswith("\n")


def test_build_bulk_body_empty_returns_single_newline():
    from vmstat_visualizer.es_exporter import build_bulk_body

    body = build_bulk_body([], index="vmstat")
    assert body == "\n"


def test_export_to_elasticsearch_hosts_and_bulk(elasticsearch_fake):
    from vmstat_visualizer.es_exporter import export_to_elasticsearch

    es_cls = elasticsearch_fake.Elasticsearch
    bulk = elasticsearch_fake.helpers.bulk
    bulk.return_value = (2, ["err1"])

    e1 = Timeseries()
    e1.time = "2025-07-31 01:02:03"
    e1.idle_cpu_percent = 90
    e2 = Timeseries()
    e2.time = "2025-07-31 01:03:03"
    e2.idle_cpu_percent = 91

    result = export_to_elasticsearch(
        [e1, e2],
        es_url="https://localhost:9200",
        api_key="sekret",
        cloud_id=None,
        index="myidx",
        source_file="/tmp/f.log",
        verify_certs=False,
    )

    es_cls.assert_called_once_with(
        hosts=["https://localhost:9200"],
        api_key="sekret",
        verify_certs=False,
    )
    client = es_cls.return_value

    bulk.assert_called_once()
    call_args = bulk.call_args
    assert call_args.args[0] is client

    actions = call_args.args[1]
    assert len(actions) == 2
    assert actions[0]["_index"] == "myidx"
    assert actions[0]["_source"]["file.path"] == "/tmp/f.log"

    assert result == {"indexed": 2, "errors": ["err1"]}


def test_export_to_elasticsearch_cloud_id(elasticsearch_fake):
    from vmstat_visualizer.es_exporter import export_to_elasticsearch

    es_cls = elasticsearch_fake.Elasticsearch
    bulk = elasticsearch_fake.helpers.bulk
    bulk.return_value = (1, [])

    e = Timeseries()
    e.time = "2025-07-31 01:02:03"

    export_to_elasticsearch(
        [e],
        es_url="ignored",
        api_key=None,
        cloud_id="cloud:ZWxhc3RpYw==",
        index="cloudidx",
        source_file=None,
        verify_certs=True,
    )

    es_cls.assert_called_once_with(
        cloud_id="cloud:ZWxhc3RpYw==",
        verify_certs=True,
    )


def test_export_helpers_bulk_empty_errors_normalized(elasticsearch_fake):
    from vmstat_visualizer.es_exporter import export_to_elasticsearch

    bulk = elasticsearch_fake.helpers.bulk
    bulk.return_value = (3, [])  # falsy errors -> []

    e = Timeseries()
    e.time = "2025-07-31 01:02:03"

    result = export_to_elasticsearch([e], es_url="http://es", index="x")
    assert result == {"indexed": 3, "errors": []}

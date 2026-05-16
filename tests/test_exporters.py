"""Unit tests for JSON/CSV export helpers."""

import csv
import io
import json

from vmstat_visualizer.exporters import (
    FIELD_ORDER,
    _entry_to_dict,
    export_csv,
    export_ndjson,
)
from vmstat_visualizer.parser.timeseries import Timeseries


class TestEntryToDict:
    def test_short_names_and_known_values(self):
        ts = Timeseries()
        ts.time = "2025-09-15 14:00:01"
        ts.run_queue = "2"
        ts.blocked_processes = "0"
        ts.user_cpu_percent = "5"
        d = _entry_to_dict(ts)
        assert d["time"] == "2025-09-15 14:00:01"
        assert d["r"] == "2"
        assert d["b"] == "0"
        assert d["us"] == "5"

    def test_omits_none_attributes(self):
        ts = Timeseries()
        ts.time = "2025-01-01 00:00:00"
        ts.run_queue = "1"
        # All other attrs remain None by default
        d = _entry_to_dict(ts)
        assert set(d.keys()) == {"time", "r"}
        assert "b" not in d
        assert "swpd" not in d

    def test_field_order_covers_exporter_mapping(self):
        """Sanity check: FIELD_ORDER attrs exist on Timeseries."""
        attrs = [a for a, _ in FIELD_ORDER]
        ts = Timeseries()
        missing = [a for a in attrs if not hasattr(ts, a)]
        assert missing == [], f"Timeseries missing attrs: {missing}"


class TestExportNdjson:
    def test_each_line_valid_json_and_fields(self):
        ts1 = Timeseries()
        ts1.time = "t1"
        ts1.run_queue = "1"
        ts2 = Timeseries()
        ts2.time = "t2"
        ts2.blocks_in = "10"
        out = export_ndjson([ts1, ts2])
        lines = out.splitlines()
        assert len(lines) == 2
        d1 = json.loads(lines[0])
        d2 = json.loads(lines[1])
        assert d1 == {"time": "t1", "r": "1"}
        assert d2 == {"time": "t2", "bi": "10"}

    def test_empty_timeseries(self):
        assert export_ndjson([]) == ""


class TestExportCsv:
    def test_header_and_rows(self):
        ts1 = Timeseries()
        ts1.time = "2025-09-15 14:00:01"
        ts1.run_queue = "2"
        ts1.user_cpu_percent = "5"

        ts2 = Timeseries()
        ts2.time = "2025-09-15 14:00:02"
        ts2.run_queue = "1"
        ts2.user_cpu_percent = "3"

        csv_text = export_csv([ts1, ts2])
        reader = csv.DictReader(io.StringIO(csv_text))
        rows = list(reader)
        assert reader.fieldnames is not None
        assert rows[0]["time"] == "2025-09-15 14:00:01"
        assert rows[0]["r"] == "2"
        assert rows[0]["us"] == "5"
        assert rows[1]["time"] == "2025-09-15 14:00:02"
        assert rows[1]["r"] == "1"
        assert rows[1]["us"] == "3"

    def test_multiple_rows(self):
        entries = []
        for i in range(3):
            ts = Timeseries()
            ts.time = f"t{i}"
            ts.idle_cpu_percent = str(90 + i)
            entries.append(ts)
        csv_text = export_csv(entries)
        body_lines = [ln for ln in csv_text.strip().split("\n")]
        assert len(body_lines) == 4  # header + 3 data rows

    def test_empty_timeseries(self):
        assert export_csv([]) == ""

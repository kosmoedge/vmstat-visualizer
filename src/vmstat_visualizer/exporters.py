"""Export parsed vmstat data to JSON and CSV formats."""

import csv
import io
import json


FIELD_ORDER = [
    ("time", "time"),
    ("run_queue", "r"),
    ("blocked_processes", "b"),
    ("swapped_memory_kb", "swpd"),
    ("free_memory_kb", "free"),
    ("inactive_memory_kb", "inact"),
    ("active_memory_kb", "active"),
    ("swap_in_kb", "si"),
    ("swap_out_kb", "so"),
    ("blocks_in", "bi"),
    ("blocks_out", "bo"),
    ("interrupts", "in"),
    ("context_switches", "cs"),
    ("user_cpu_percent", "us"),
    ("system_cpu_percent", "sy"),
    ("idle_cpu_percent", "id"),
    ("wait_cpu_percent", "wa"),
    ("steal_cpu_percent", "st"),
    ("guest_cpu_percent", "gu"),
]


def _entry_to_dict(ts_entry):
    """Convert a Timeseries entry to a flat dict, omitting None values."""
    row = {}
    for attr, short_name in FIELD_ORDER:
        val = getattr(ts_entry, attr, None)
        if val is not None:
            row[short_name] = val
    return row


def export_ndjson(timeseries):
    """Export timeseries as newline-delimited JSON (NDJSON)."""
    lines = []
    for entry in timeseries:
        lines.append(json.dumps(_entry_to_dict(entry)))
    return "\n".join(lines)


def export_csv(timeseries):
    """Export timeseries as CSV."""
    if not timeseries:
        return ""

    all_rows = [_entry_to_dict(entry) for entry in timeseries]
    fieldnames = list(dict.fromkeys(
        key for row in all_rows for key in row.keys()
    ))

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for row in all_rows:
        writer.writerow(row)
    return output.getvalue()

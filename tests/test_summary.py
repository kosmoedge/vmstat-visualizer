"""Unit tests for summary statistics helpers."""

import json
from types import SimpleNamespace

import pytest

from vmstat_visualizer.summary import (
    compute_summary,
    format_summary_json,
    format_summary_text,
    _duration_above,
    _percentile,
    _safe_ints,
    _stats_for,
)


class TestSafeInts:
    def test_normal_values(self):
        assert _safe_ints(["1", "2", "3"]) == [1, 2, 3]

    def test_skips_none(self):
        assert _safe_ints([None, "5", None, "10"]) == [5, 10]

    def test_empty_list(self):
        assert _safe_ints([]) == []


class TestPercentile:
    def test_empty_returns_zero(self):
        assert _percentile([], 50) == 0

    def test_single_element(self):
        assert _percentile([42], 50) == 42
        assert _percentile([42], 99) == 42

    def test_p50_interpolated_odd_length(self):
        s = sorted([1, 2, 3, 4])
        assert _percentile(s, 50) == 2.5

    def test_p95_known_sorted(self):
        s = sorted([10, 20, 30, 40, 50])
        assert _percentile(s, 95) == pytest.approx(48.0)

    def test_p99_known_sorted(self):
        s = sorted(list(range(1, 101)))
        assert _percentile(s, 99) == pytest.approx(99.01)


class TestStatsFor:
    def test_normal_list(self):
        out = _stats_for(["3", None, "1", "4"])
        assert out is not None
        assert out["min"] == 1
        assert out["max"] == 4
        assert out["mean"] == pytest.approx(2.67, rel=1e-2)

    def test_all_none_returns_none(self):
        assert _stats_for([None, None]) is None

    def test_single_value(self):
        out = _stats_for(["99"])
        assert out == {"min": 99, "max": 99, "mean": 99.0, "p95": 99.0, "p99": 99.0}


class TestDurationAbove:
    def test_counts_above_threshold(self):
        vals = ["0", None, "5", "10", None, "21"]
        assert _duration_above(vals, 5) == 2

    def test_zero_results(self):
        assert _duration_above(["0", None, "-1"], 0) == 0


class TestComputeSummary:
    def test_known_plot_metrics_like_object(self):
        pm = SimpleNamespace(
            t=[0, 1, 2],
            user_cpu_percent=["50", "10", "90"],
            system_cpu_percent=["35", "10", "15"],
            idle_cpu_percent=["15", None, "70"],
            wait_cpu_percent=["5", "25", "10"],
            steal_cpu_percent=["0", "0", "0"],
            free_memory_kb=["1000", "2000", "3000"],
            swapped_memory_kb=["0", "0", "10"],
            inactive_memory_kb=["100", "200", "300"],
            active_memory_kb=["500", "500", "600"],
            blocks_in=["1", "2", "3"],
            blocks_out=["4", "5", "6"],
            swap_in_kb=["0", "1", "0"],
            swap_out_kb=["0", "0", "2"],
            run_queue=["0", "1", "2"],
            blocked_processes=["0", "0", "1"],
        )
        summary = compute_summary(pm)

        assert summary["total_samples"] == 3

        cpu = summary["cpu"]
        for key in (
            "user_cpu_percent",
            "system_cpu_percent",
            "idle_cpu_percent",
            "wait_cpu_percent",
            "steal_cpu_percent",
        ):
            assert key in cpu
            stat = cpu[key]
            for field in ("min", "max", "mean", "p95", "p99"):
                assert field in stat

        assert cpu["user_cpu_percent"]["min"] == 10
        assert cpu["user_cpu_percent"]["max"] == 90

        mem = summary["memory"]
        for key in ("free_memory_kb", "swapped_memory_kb",
                    "inactive_memory_kb", "active_memory_kb"):
            assert key in mem

        assert "blocks_in" in summary["io"] and "blocks_out" in summary["io"]
        assert "swap_in_kb" in summary["swap"] and "swap_out_kb" in summary["swap"]
        load = summary["system_load"]
        assert "run_queue" in load and "blocked_processes" in load

        alerts = summary["alerts"]
        assert alerts["high_cpu_seconds"] == 2
        assert alerts["high_wait_seconds"] == 1
        assert alerts["high_swap_seconds"] == 1


class TestFormatSummaryText:
    def test_contains_headers_and_metric_names(self):
        pm = SimpleNamespace(
            t=[0],
            user_cpu_percent=["5"],
            system_cpu_percent=["5"],
            idle_cpu_percent=["90"],
            wait_cpu_percent=["0"],
            steal_cpu_percent=["0"],
            free_memory_kb=["1000"],
            swapped_memory_kb=["0"],
            inactive_memory_kb=["0"],
            active_memory_kb=["500"],
            blocks_in=["1"],
            blocks_out=["1"],
            swap_in_kb=["0"],
            swap_out_kb=["0"],
            run_queue=["0"],
            blocked_processes=["0"],
        )
        summary = compute_summary(pm)
        text = format_summary_text(summary)
        assert "vmstat Summary" in text
        assert "CPU" in text or "MEMORY" in text
        assert "user_cpu_percent" in text


class TestFormatSummaryJson:
    def test_valid_json_round_trip(self):
        summary = compute_summary(
            SimpleNamespace(
                t=[0, 1],
                user_cpu_percent=["1", "2"],
                system_cpu_percent=["3", "4"],
                idle_cpu_percent=["96", "94"],
                wait_cpu_percent=["0", "0"],
                steal_cpu_percent=["0", "0"],
                free_memory_kb=["100", "101"],
                swapped_memory_kb=["0", "0"],
                inactive_memory_kb=["10", "11"],
                active_memory_kb=["20", "21"],
                blocks_in=["0", "0"],
                blocks_out=["0", "0"],
                swap_in_kb=["0", "0"],
                swap_out_kb=["0", "0"],
                run_queue=["0", "1"],
                blocked_processes=["0", "0"],
            )
        )
        dumped = format_summary_json(summary)
        restored = json.loads(dumped)
        assert restored["total_samples"] == summary["total_samples"]
        assert restored["cpu"] == summary["cpu"]

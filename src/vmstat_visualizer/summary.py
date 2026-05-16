"""Summary statistics for parsed vmstat data."""

import json
import math


def _safe_ints(values):
    """Convert a list of string values to integers, skipping None."""
    return [int(v) for v in values if v is not None]


def _percentile(sorted_data, p):
    """Calculate the p-th percentile from pre-sorted data."""
    if not sorted_data:
        return 0
    k = (len(sorted_data) - 1) * (p / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)


def _stats_for(values):
    """Return min/max/mean/p95/p99 dict for a list of string values."""
    nums = _safe_ints(values)
    if not nums:
        return None
    s = sorted(nums)
    return {
        "min": s[0],
        "max": s[-1],
        "mean": round(sum(s) / len(s), 2),
        "p95": round(_percentile(s, 95), 2),
        "p99": round(_percentile(s, 99), 2),
    }


def _duration_above(values, threshold):
    """Count how many consecutive seconds values stayed above threshold."""
    nums = _safe_ints(values)
    return sum(1 for v in nums if v > threshold)


def compute_summary(plot_metrics):
    """Build a summary dict from a PlotMetrics instance."""
    summary = {}

    cpu_metrics = {
        "user_cpu_percent": plot_metrics.user_cpu_percent,
        "system_cpu_percent": plot_metrics.system_cpu_percent,
        "idle_cpu_percent": plot_metrics.idle_cpu_percent,
        "wait_cpu_percent": plot_metrics.wait_cpu_percent,
        "steal_cpu_percent": plot_metrics.steal_cpu_percent,
    }
    summary["cpu"] = {k: _stats_for(v) for k, v in cpu_metrics.items() if _stats_for(v)}

    mem_metrics = {
        "free_memory_kb": plot_metrics.free_memory_kb,
        "swapped_memory_kb": plot_metrics.swapped_memory_kb,
        "inactive_memory_kb": plot_metrics.inactive_memory_kb,
        "active_memory_kb": plot_metrics.active_memory_kb,
    }
    summary["memory"] = {k: _stats_for(v) for k, v in mem_metrics.items() if _stats_for(v)}

    io_metrics = {
        "blocks_in": plot_metrics.blocks_in,
        "blocks_out": plot_metrics.blocks_out,
    }
    summary["io"] = {k: _stats_for(v) for k, v in io_metrics.items() if _stats_for(v)}

    swap_metrics = {
        "swap_in_kb": plot_metrics.swap_in_kb,
        "swap_out_kb": plot_metrics.swap_out_kb,
    }
    summary["swap"] = {k: _stats_for(v) for k, v in swap_metrics.items() if _stats_for(v)}

    load_metrics = {
        "run_queue": plot_metrics.run_queue,
        "blocked_processes": plot_metrics.blocked_processes,
    }
    summary["system_load"] = {k: _stats_for(v) for k, v in load_metrics.items() if _stats_for(v)}

    total_cpu = _safe_ints(plot_metrics.user_cpu_percent) + _safe_ints(plot_metrics.system_cpu_percent)
    user_vals = _safe_ints(plot_metrics.user_cpu_percent)
    sys_vals = _safe_ints(plot_metrics.system_cpu_percent)
    if user_vals and sys_vals:
        combined = [u + s for u, s in zip(user_vals, sys_vals)]
        summary["alerts"] = {
            "high_cpu_seconds": sum(1 for v in combined if v > 80),
            "high_wait_seconds": _duration_above(plot_metrics.wait_cpu_percent, 20),
            "high_swap_seconds": _duration_above(plot_metrics.swapped_memory_kb, 0),
        }

    summary["total_samples"] = len(plot_metrics.t)

    return summary


def format_summary_text(summary):
    """Format summary dict as a human-readable text table."""
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"  vmstat Summary ({summary['total_samples']} samples)")
    lines.append(f"{'='*60}")

    for section in ["cpu", "memory", "io", "swap", "system_load"]:
        data = summary.get(section, {})
        if not data:
            continue
        lines.append(f"\n  {section.upper()}")
        lines.append(f"  {'Metric':<25} {'Min':>7} {'Max':>7} {'Mean':>7} {'P95':>7} {'P99':>7}")
        lines.append(f"  {'-'*55}")
        for metric, stats in data.items():
            lines.append(
                f"  {metric:<25} {stats['min']:>7} {stats['max']:>7} "
                f"{stats['mean']:>7} {stats['p95']:>7} {stats['p99']:>7}"
            )

    alerts = summary.get("alerts", {})
    if alerts:
        lines.append(f"\n  ALERTS")
        lines.append(f"  {'-'*55}")
        if alerts.get("high_cpu_seconds", 0) > 0:
            lines.append(f"  CPU > 80% (user+sys):  {alerts['high_cpu_seconds']}s")
        if alerts.get("high_wait_seconds", 0) > 0:
            lines.append(f"  IO Wait > 20%:         {alerts['high_wait_seconds']}s")
        if alerts.get("high_swap_seconds", 0) > 0:
            lines.append(f"  Swap in use:           {alerts['high_swap_seconds']}s")
        if all(v == 0 for v in alerts.values()):
            lines.append(f"  No alert thresholds breached.")

    lines.append(f"\n{'='*60}")
    return "\n".join(lines)


def format_summary_json(summary):
    """Format summary dict as JSON."""
    return json.dumps(summary, indent=2)

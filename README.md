# vmstat-visualizer

A CLI tool for creating plots from vmstat output files. Generates PNG/SVG charts for CPU, memory, swap, I/O, and system load metrics.

## What it does

Takes vmstat log files and produces time-series graphs. You can visualize a single file or compare two files side-by-side.

## Requirements

- Python 3.7+
- matplotlib

## Installation

```bash
pip install vmstat-visualizer
```

Or from source:

```bash
git clone https://github.com/nikfot/vmstat-visualizer.git
cd vmstat-visualizer
pip install -e .
```

## Usage

### Visualize a single file

```bash
vmstat-visualizer visualize vmstat.log
```

This generates 5 PNG files:
- `vmstat_cpu_<timestamp>.png` - CPU usage (user, system, idle, wait, steal)
- `vmstat_memory_<timestamp>.png` - Memory usage (active, inactive, free, swapped)
- `vmstat_system_load_<timestamp>.png` - Process queues (running, blocked)
- `vmstat_swap_<timestamp>.png` - Swap activity (in, out, total)
- `vmstat_io_<timestamp>.png` - Block I/O (in, out)

Options:
- `-o, --output-prefix`: Set output filename prefix (default: `vmstat`)
- `-e, --output-extension`: Set output format: `png` or `svg` (default: `png`)

```bash
vmstat-visualizer visualize vmstat.log -o server1 -e svg
```

### Compare two files

```bash
vmstat-visualizer compare file1.log file2.log -m cpu
```

Metrics available for comparison:
- `cpu` - CPU usage percentages
- `memory` - Memory allocation
- `system_load` - Process queues
- `swap` - Swap usage
- `io` - Block I/O
- `all` - All metrics

Options:
- `-m, --metric`: Metric to compare (required)
- `-o, --output-prefix`: Output filename prefix (default: `vmstat`)
- `-e, --output-extension`: Output format (default: `png`)
- `-c, --column`: Filter specific columns (can specify multiple times)

### Filter specific columns

You can plot only specific columns:

```bash
# Compare only user and system CPU
vmstat-visualizer compare file1.log file2.log -m cpu -c us -c sy

# Compare only free and active memory
vmstat-visualizer compare file1.log file2.log -m memory -c free -c active
```

Available columns by metric:
- **cpu**: `us` (user), `sy` (system), `id` (idle), `wa` (wait), `st` (steal)
- **memory**: `free`, `active`, `inact` (inactive), `swpd` (swapped)
- **system_load**: `r` (running queue), `b` (blocked processes)
- **swap**: `si` (swap in), `so` (swap out), `swpd` (swapped)
- **io**: Block I/O columns

## vmstat log format

The tool expects vmstat output with timestamps. Generate compatible logs:

```bash
# Linux (with date prefix)
vmstat -t 1 > vmstat.log

# Or add timestamps with awk
vmstat 1 | awk '{print strftime("%Y-%m-%d %H:%M:%S"), $0}' > vmstat.log
```

Example vmstat output:
```
2025-11-08 10:30:01 procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
2025-11-08 10:30:01  r  b   swpd   free  inact active   si   so    bi    bo   in   cs us sy id wa st
2025-11-08 10:30:01  2  0      0 256428 1582212 6253196    0    0     5    12  203  445  8  2 89  1  0
```

## Output

Charts show:
- **Single file**: Time on x-axis (MM:SS format), start time in footer
- **Comparison**: Relative time (seconds), File 1 shown with solid lines, File 2 with dashed lines
- **Filenames**: Displayed in legend for comparisons (basename only)

## Examples

```bash
# Basic visualization
vmstat-visualizer visualize server-metrics.log

# Compare before/after server changes
vmstat-visualizer compare before.log after.log -m all

# Compare CPU with specific columns
vmstat-visualizer compare baseline.log optimized.log -m cpu -c us -c sy -c wa

# Generate SVG for documentation
vmstat-visualizer compare test1.log test2.log -m memory -e svg -o memory-comparison
```

## Notes

- Timestamps are parsed from the vmstat output (format: `YYYY-MM-DD HH:MM:SS`)
- Empty lines and header rows are automatically skipped
- Y-axis starts at 0 for better visual comparison
- Font size is reduced in comparison mode to fit more legend entries
- The tool handles different vmstat column availability across systems

## License

MIT

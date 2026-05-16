import csv
import glob
import io
import json

import pytest
from click.testing import CliRunner
from unittest.mock import patch

import vmstat_visualizer.cli.visualizer as viz
from vmstat_visualizer.cli.__main__ import cli
from vmstat_visualizer.cli.export import export


@pytest.fixture(autouse=True)
def _register_commands():
    """Ensure commands are registered before each test."""
    cli.add_command(viz.visualize)
    cli.add_command(viz.compare)
    cli.add_command(export)


class TestCLIHelp:
    def test_main_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "visualize" in result.output
        assert "compare" in result.output
        assert "export" in result.output

    def test_visualize_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["visualize", "--help"])
        assert result.exit_code == 0
        assert "--output-prefix" in result.output
        assert "--output-extension" in result.output

    def test_compare_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["compare", "--help"])
        assert result.exit_code == 0
        assert "--metric" in result.output
        assert "--column" in result.output


class TestVisualizeCommand:
    @patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    )
    def test_visualize_active_log(self, mock_check, active_log, tmp_path):
        runner = CliRunner()
        prefix = str(tmp_path / "viz")
        result = runner.invoke(
            cli, ["visualize", active_log, "-o", prefix, "-e", "png"]
        )
        assert result.exit_code == 0
        assert "5 time series entries" in result.output
        pngs = glob.glob(str(tmp_path / "viz_*.png"))
        assert len(pngs) == 5

    @patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    )
    def test_visualize_example_log(self, mock_check, example_log, tmp_path):
        runner = CliRunner()
        prefix = str(tmp_path / "ex")
        result = runner.invoke(cli, ["visualize", example_log, "-o", prefix])
        assert result.exit_code == 0
        assert "30 time series entries" in result.output

    def test_visualize_missing_file(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["visualize", str(tmp_path / "nonexistent.log")]
        )
        assert result.exit_code != 0


class TestCompareCommand:
    @patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    )
    def test_compare_cpu(self, mock_check, active_log, tmp_path):
        runner = CliRunner()
        prefix = str(tmp_path / "cmp")
        result = runner.invoke(
            cli,
            ["compare", active_log, active_log, "-m", "cpu", "-o", prefix],
        )
        assert result.exit_code == 0
        assert "Comparing" in result.output

    @patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    )
    def test_compare_all(self, mock_check, active_log, tmp_path):
        runner = CliRunner()
        prefix = str(tmp_path / "all")
        result = runner.invoke(
            cli,
            ["compare", active_log, active_log, "-m", "all", "-o", prefix],
        )
        assert result.exit_code == 0

    @patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    )
    def test_compare_with_column_filter(self, mock_check, active_log, tmp_path):
        runner = CliRunner()
        prefix = str(tmp_path / "filt")
        result = runner.invoke(
            cli,
            [
                "compare",
                active_log,
                active_log,
                "-m",
                "cpu",
                "-c",
                "us",
                "-c",
                "sy",
                "-o",
                prefix,
            ],
        )
        assert result.exit_code == 0
        assert "Filtering columns: us, sy" in result.output

    def test_compare_invalid_metric(self, active_log):
        runner = CliRunner()
        result = runner.invoke(
            cli, ["compare", active_log, active_log, "-m", "bogus"]
        )
        assert result.exit_code != 0


def _json_lines(cli_output):
    """NDJSON rows only (parser prints status lines before JSON)."""
    return [ln for ln in cli_output.splitlines() if ln.strip().startswith("{")]


def _csv_text_from_output(cli_output):
    """CSV starts at header row ``time,...`` after optional parser preamble."""
    lines = cli_output.splitlines()
    start = next((i for i, ln in enumerate(lines) if ln.startswith("time,")), None)
    assert start is not None, "expected CSV header in output"
    return "\n".join(lines[start:])


class TestExportCommand:
    @patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    )
    def test_export_json_stdout(self, mock_check, standard_log):
        runner = CliRunner()
        result = runner.invoke(cli, ["export", standard_log, "--to", "json"])
        assert result.exit_code == 0
        jl = _json_lines(result.output)
        assert len(jl) == 5
        first = json.loads(jl[0])
        assert first["time"] == "2025-09-15 14:00:01"
        assert first["r"] == "2"
        assert "free" in first

    @patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    )
    def test_export_csv_stdout(self, mock_check, standard_log):
        runner = CliRunner()
        result = runner.invoke(cli, ["export", standard_log, "--to", "csv"])
        assert result.exit_code == 0
        csv_blob = _csv_text_from_output(result.output)
        reader = csv.DictReader(io.StringIO(csv_blob))
        rows = list(reader)
        assert len(rows) == 5
        assert rows[0]["time"] == "2025-09-15 14:00:01"
        assert rows[0]["r"] == "2"

    @patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    )
    def test_export_json_to_file(self, mock_check, standard_log, tmp_path):
        runner = CliRunner()
        out = tmp_path / "out.ndjson"
        result = runner.invoke(
            cli, ["export", standard_log, "--to", "json", "-o", str(out)]
        )
        assert result.exit_code == 0
        text = out.read_text()
        assert text.startswith('{"time"')
        assert "Exported 5 entries" in result.output
        lines = [ln for ln in text.splitlines() if ln.strip()]
        assert len(lines) == 5
        json.loads(lines[0])

    def test_export_help_mentions_formats(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["export", "--help"])
        assert result.exit_code == 0
        low = result.output.lower()
        assert "json" in low and "csv" in low

    @patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    )
    def test_export_empty_file_error(self, mock_check, empty_log):
        runner = CliRunner()
        result = runner.invoke(cli, ["export", empty_log, "--to", "json"])
        assert result.exit_code == 1
        assert "No data found" in result.output

    def test_export_missing_file_error(self, tmp_path):
        runner = CliRunner()
        bad = str(tmp_path / "nope.vmstat")
        result = runner.invoke(cli, ["export", bad, "--to", "json"])
        assert result.exit_code == 2
        assert "does not exist" in result.output


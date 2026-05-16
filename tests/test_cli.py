import glob

import pytest
from click.testing import CliRunner
from unittest.mock import patch

import vmstat_visualizer.cli.visualizer as viz
from vmstat_visualizer.cli.__main__ import cli
from vmstat_visualizer.cli.multi_compare import compare_multi


@pytest.fixture(autouse=True)
def _register_commands():
    """Ensure commands are registered before each test."""
    cli.add_command(viz.visualize)
    cli.add_command(viz.compare)
    cli.add_command(compare_multi)


class TestCLIHelp:
    def test_main_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "visualize" in result.output
        assert "compare" in result.output
        assert "compare-multi" in result.output

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


class TestCompareMultiCommand:
    @patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    )
    def test_compare_multi_cpu_png(self, mock_check, active_log, tmp_path):
        runner = CliRunner()
        prefix = str(tmp_path / "multic")
        result = runner.invoke(
            cli,
            [
                "compare-multi",
                active_log,
                active_log,
                "-m",
                "cpu",
                "-o",
                prefix,
            ],
        )
        assert result.exit_code == 0
        pngs = glob.glob(str(tmp_path / "multic_cpu_multi_*.png"))
        assert len(pngs) == 1

    @patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    )
    def test_compare_multi_all_five_outputs(self, mock_check,
                                            active_log, tmp_path):
        runner = CliRunner()
        prefix = str(tmp_path / "fall")
        result = runner.invoke(
            cli,
            [
                "compare-multi",
                active_log,
                active_log,
                "-m",
                "all",
                "-o",
                prefix,
            ],
        )
        assert result.exit_code == 0
        pngs = glob.glob(str(tmp_path / "fall_*_multi_*.png"))
        assert len(pngs) == 5

    def test_compare_multi_help_lists_metrics(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["compare-multi", "--help"])
        assert result.exit_code == 0
        assert "cpu|memory|" in result.output or "[cpu|" in result.output
        assert "system_load" in result.output

    def test_compare_multi_single_file_fails(self, active_log):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            ["compare-multi", active_log, "-m", "cpu"],
        )
        assert result.exit_code != 0
        assert "At least 2 files" in result.output


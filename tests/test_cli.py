import os
import glob
import json
import pytest
from unittest.mock import patch
from click.testing import CliRunner
from vmstat_visualizer.cli.__main__ import cli
import vmstat_visualizer.cli.visualizer as viz
from vmstat_visualizer.cli.es_export import export_es


@pytest.fixture(autouse=True)
def _register_commands():
    """Ensure commands are registered before each test."""
    cli.add_command(viz.visualize)
    cli.add_command(viz.compare)
    cli.add_command(export_es)


class TestCLIHelp:
    def test_main_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'visualize' in result.output
        assert 'compare' in result.output
        assert 'export-es' in result.output

    def test_visualize_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['visualize', '--help'])
        assert result.exit_code == 0
        assert '--output-prefix' in result.output
        assert '--output-extension' in result.output

    def test_compare_help(self):
        runner = CliRunner()
        result = runner.invoke(cli, ['compare', '--help'])
        assert result.exit_code == 0
        assert '--metric' in result.output
        assert '--column' in result.output


class TestVisualizeCommand:
    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_visualize_active_log(self, mock_check, active_log, tmp_path):
        runner = CliRunner()
        prefix = str(tmp_path / "viz")
        result = runner.invoke(cli, [
            'visualize', active_log, '-o', prefix, '-e', 'png'
        ])
        assert result.exit_code == 0
        assert '5 time series entries' in result.output
        pngs = glob.glob(str(tmp_path / "viz_*.png"))
        assert len(pngs) == 5

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_visualize_example_log(self, mock_check, example_log, tmp_path):
        runner = CliRunner()
        prefix = str(tmp_path / "ex")
        result = runner.invoke(cli, [
            'visualize', example_log, '-o', prefix
        ])
        assert result.exit_code == 0
        assert '30 time series entries' in result.output

    def test_visualize_missing_file(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(cli, [
            'visualize', str(tmp_path / 'nonexistent.log')
        ])
        assert result.exit_code != 0


class TestCompareCommand:
    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_compare_cpu(self, mock_check, active_log, tmp_path):
        runner = CliRunner()
        prefix = str(tmp_path / "cmp")
        result = runner.invoke(cli, [
            'compare', active_log, active_log,
            '-m', 'cpu', '-o', prefix
        ])
        assert result.exit_code == 0
        assert 'Comparing' in result.output

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_compare_all(self, mock_check, active_log, tmp_path):
        runner = CliRunner()
        prefix = str(tmp_path / "all")
        result = runner.invoke(cli, [
            'compare', active_log, active_log,
            '-m', 'all', '-o', prefix
        ])
        assert result.exit_code == 0

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_compare_with_column_filter(self, mock_check, active_log, tmp_path):
        runner = CliRunner()
        prefix = str(tmp_path / "filt")
        result = runner.invoke(cli, [
            'compare', active_log, active_log,
            '-m', 'cpu', '-c', 'us', '-c', 'sy', '-o', prefix
        ])
        assert result.exit_code == 0
        assert 'Filtering columns: us, sy' in result.output

    def test_compare_invalid_metric(self, active_log):
        runner = CliRunner()
        result = runner.invoke(cli, [
            'compare', active_log, active_log, '-m', 'bogus'
        ])
        assert result.exit_code != 0


class TestExportEsCommand:
    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_export_es_help_shows_expected_options(self, mock_check):
        runner = CliRunner()
        result = runner.invoke(cli, ['export-es', '--help'])
        assert result.exit_code == 0
        for needle in (
            '--es-url',
            '--es-api-key',
            '--cloud-id',
            '--index',
            '--dry-run',
            '--no-verify-certs',
        ):
            assert needle in result.output

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_export_es_dry_run_prints_bulk_to_stdout(self, mock_check,
                                                     active_log):
        runner = CliRunner()
        result = runner.invoke(cli, ['export-es', '--dry-run', active_log])

        assert result.exit_code == 0
        out = result.output
        json_lines = [ln for ln in out.splitlines() if ln.startswith('{')]
        assert len(json_lines) == 10
        assert json.loads(json_lines[0]) == {"index": {"_index": "vmstat"}}

        doc = json.loads(json_lines[1])
        assert doc.get("event.module") == "vmstat"
        assert doc.get("file.path") == active_log

        assert '"index"' in out and '"system.' in out

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_export_es_without_endpoint_errors(self, mock_check, active_log):
        runner = CliRunner()
        result = runner.invoke(cli, ['export-es', active_log])
        assert result.exit_code != 0
        low = result.output.lower()
        assert 'es-url' in low or 'cloud-id' in low

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_export_es_empty_file_errors(self, mock_check, empty_log):
        runner = CliRunner()
        result = runner.invoke(cli, ['export-es', '--dry-run', empty_log])
        assert result.exit_code == 1
        assert 'No data found' in result.output


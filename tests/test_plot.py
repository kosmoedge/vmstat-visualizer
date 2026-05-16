import os
import glob
import pytest
import matplotlib
matplotlib.use('Agg')
from unittest.mock import patch
from vmstat_visualizer.parser.parser import Parser


class TestPlotOutput:
    """Integration: parse a fixture and verify plot files are created."""

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_visualize_creates_five_plots(self, mock_check, active_log, tmp_path):
        p = Parser(active_log)
        p.parse()
        prefix = str(tmp_path / "test_plot")
        p.plot(output_file_prefix=prefix, output_format='png')

        pngs = glob.glob(str(tmp_path / "test_plot_*.png"))
        assert len(pngs) == 5
        expected_parts = ['system_load', 'memory', 'cpu', 'swap', 'io']
        basenames = [os.path.basename(f) for f in pngs]
        for part in expected_parts:
            assert any(part in b for b in basenames), f"Missing plot for '{part}'"

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_svg_output_format(self, mock_check, active_log, tmp_path):
        p = Parser(active_log)
        p.parse()
        prefix = str(tmp_path / "svg_plot")
        p.plot(output_file_prefix=prefix, output_format='svg')
        svgs = glob.glob(str(tmp_path / "svg_plot_*.svg"))
        assert len(svgs) == 5

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_plot_example_log(self, mock_check, example_log, tmp_path):
        p = Parser(example_log)
        p.parse()
        prefix = str(tmp_path / "ex_plot")
        p.plot(output_file_prefix=prefix, output_format='png')
        pngs = glob.glob(str(tmp_path / "ex_plot_*.png"))
        assert len(pngs) == 5


class TestComparisonPlot:
    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_comparison_cpu(self, mock_check, active_log, tmp_path):
        p1 = Parser(active_log)
        p1.parse()
        p2 = Parser(active_log)
        p2.parse()
        prefix = str(tmp_path / "cmp")
        p1.plot_comparison(p2, output_file_prefix=prefix,
                           output_format='png', metric='cpu')
        pngs = glob.glob(str(tmp_path / "cmp_*.png"))
        assert len(pngs) >= 1
        assert any('cpu_comparison' in os.path.basename(f) for f in pngs)

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_comparison_all(self, mock_check, active_log, tmp_path):
        p1 = Parser(active_log)
        p1.parse()
        p2 = Parser(active_log)
        p2.parse()
        prefix = str(tmp_path / "cmp_all")
        p1.plot_comparison(p2, output_file_prefix=prefix,
                           output_format='png', metric='all')
        pngs = glob.glob(str(tmp_path / "cmp_all_*.png"))
        assert len(pngs) == 5

    @patch("vmstat_visualizer.parser.parser.check_vmstat_columns",
           return_value=(True, True))
    def test_comparison_invalid_metric_raises(self, mock_check, active_log):
        p1 = Parser(active_log)
        p1.parse()
        p2 = Parser(active_log)
        p2.parse()
        with pytest.raises(ValueError, match="Unknown metric"):
            p1.plot_comparison(p2, metric='nonexistent')

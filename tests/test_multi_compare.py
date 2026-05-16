import glob
import os

import matplotlib

matplotlib.use("Agg")

import pytest
from unittest.mock import patch

from vmstat_visualizer.multi_compare import (
    COLORS,
    LINE_STYLES,
    _style_for,
    plot_multi_compare,
)
from vmstat_visualizer.parser.parser import Parser


class TestStyleFor:
    def test_returns_first_palette_entry(self):
        c, s = _style_for(0)
        assert c == COLORS[0]
        assert s == LINE_STYLES[0]

    def test_colors_wrap_when_index_exceeds_length(self):
        idx = len(COLORS) + 7
        c, _ = _style_for(idx)
        assert c == COLORS[idx % len(COLORS)]

    def test_line_styles_wrap_when_index_exceeds_length(self):
        idx = len(LINE_STYLES) + 3
        _, s = _style_for(idx)
        assert s == LINE_STYLES[idx % len(LINE_STYLES)]

    def test_combo_wrap_large_index(self):
        idx = len(COLORS) * len(LINE_STYLES) + 42
        c, s = _style_for(idx)
        assert c == COLORS[idx % len(COLORS)]
        assert s == LINE_STYLES[idx % len(LINE_STYLES)]


@pytest.fixture
def two_parsers(active_log):
    with patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    ):
        p1 = Parser(active_log)
        p1.parse()
        p2 = Parser(active_log)
        p2.parse()
    return [p1, p2]


@pytest.fixture
def three_parsers(active_log, standard_log):
    with patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    ):
        parsers = []
        for path in (active_log, standard_log, active_log):
            p = Parser(path)
            p.parse()
            parsers.append(p)
    return parsers


class TestPlotMultiCompare:
    def test_plot_cpu_naming_two_parsers(self, two_parsers, tmp_path):
        prefix = str(tmp_path / "pfx")
        plot_multi_compare(two_parsers, "cpu", output_file_prefix=prefix)
        matches = glob.glob(str(tmp_path / "pfx_cpu_multi_*.png"))
        assert len(matches) == 1
        basename = os.path.basename(matches[0])
        assert basename.startswith("pfx_cpu_multi_")
        assert basename.endswith(".png")

    def test_plot_all_metric_five_files(self, two_parsers, tmp_path):
        prefix = str(tmp_path / "mall")
        plot_multi_compare(two_parsers, "all", output_file_prefix=prefix)
        pngs = glob.glob(str(tmp_path / "mall_*_multi_*.png"))
        assert len(pngs) == 5
        basenames = {os.path.basename(f) for f in pngs}
        for metric in ("cpu", "memory", "system_load", "swap", "io"):
            assert any(
                name.startswith(f"mall_{metric}_multi_")
                and name.endswith(".png")
                for name in basenames
            )

    @pytest.mark.parametrize(
        "metric",
        ["memory", "system_load", "swap", "io"],
    )
    def test_plot_individual_metric_output(
        self, two_parsers, tmp_path, metric
    ):
        prefix = str(tmp_path / metric)
        plot_multi_compare(
            two_parsers,
            metric,
            output_file_prefix=prefix,
        )
        hits = glob.glob(str(tmp_path / f"{metric}_{metric}_multi_*.png"))
        assert len(hits) == 1

    def test_svg_output_format(self, two_parsers, tmp_path):
        prefix = str(tmp_path / "sv")
        plot_multi_compare(
            two_parsers,
            "cpu",
            output_file_prefix=prefix,
            output_format="svg",
        )
        svgs = glob.glob(str(tmp_path / "sv_cpu_multi_*.svg"))
        assert len(svgs) == 1

    def test_three_parsers(self, three_parsers, tmp_path):
        prefix = str(tmp_path / "t3")
        plot_multi_compare(three_parsers, "swap", output_file_prefix=prefix)
        assert (
            len(glob.glob(str(tmp_path / "t3_swap_multi_*.png"))) == 1
        )

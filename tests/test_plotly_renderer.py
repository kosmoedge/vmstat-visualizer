"""Unit tests for HTML / Plotly rendering (plotly_renderer)."""

from __future__ import annotations

import builtins
import datetime
import types
from unittest.mock import MagicMock, patch

import pytest

from vmstat_visualizer import plotly_renderer as pr
from vmstat_visualizer.parser.parser import Parser


@pytest.fixture
def parsed_active_parser(active_log):
    with patch(
        "vmstat_visualizer.parser.parser.check_vmstat_columns",
        return_value=(True, True),
    ):
        parser = Parser(active_log)
        parser.parse()
    return parser


def test_check_plotly_true(monkeypatch):
    stub = MagicMock()
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "plotly":
            return stub
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    assert pr._check_plotly() is True


def test_check_plotly_false(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "plotly":
            raise ImportError("No module named 'plotly'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    assert pr._check_plotly() is False


def test_render_html_raises_when_plotly_missing():
    parser = MagicMock()
    parser.timeseries = []
    with patch.object(pr, "_check_plotly", return_value=False):
        with pytest.raises(
            ImportError, match="Plotly is required for HTML output"
        ):
            pr.render_html(parser)


def test_render_html_message_mentions_plotly_install_hint():
    with patch.object(pr, "_check_plotly", return_value=False):
        with pytest.raises(ImportError, match=r"pip install plotly"):
            pr.render_html(MagicMock())


def _fake_plotly_modules(fake_fig):
    make_subplots = MagicMock(return_value=fake_fig)
    subplot_mod = types.ModuleType("plotly.subplots")
    subplot_mod.make_subplots = make_subplots

    go_mod = types.ModuleType("plotly.graph_objects")
    go_mod.Scatter = MagicMock(side_effect=lambda **kwargs: MagicMock(kwargs=kwargs))

    plot_pkg = types.ModuleType("plotly")

    return {
        "plotly": plot_pkg,
        "plotly.subplots": subplot_mod,
        "plotly.graph_objects": go_mod,
    }, make_subplots, go_mod


def test_render_html_five_panel_subplots_traces_and_filename(
    parsed_active_parser,
    monkeypatch,
    tmp_path,
):
    """Verify 5 subplot rows, subplot titles for each panel, Scatter usage, HTML path."""

    fake_fig = MagicMock()
    modules, make_subplots, go_mod = _fake_plotly_modules(fake_fig)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setitem(__import__("sys").modules, "plotly", modules["plotly"])
    monkeypatch.setitem(
        __import__("sys").modules, "plotly.subplots", modules["plotly.subplots"],
    )
    monkeypatch.setitem(
        __import__("sys").modules,
        "plotly.graph_objects",
        modules["plotly.graph_objects"],
    )

    fixed_now = datetime.datetime(2026, 5, 16, 12, 34, 56)
    with patch.object(pr.datetime, "datetime") as dt_proxy:
        dt_proxy.now.return_value = fixed_now
        with patch.object(pr.time, "mktime", return_value=1_738_934_940.0):
            out_name = pr.render_html(
                parsed_active_parser, output_file_prefix="vmstatviz",
            )

    make_subplots.assert_called_once()
    ms_kwargs = make_subplots.call_args.kwargs
    assert ms_kwargs["rows"] == 5
    assert ms_kwargs["cols"] == 1
    titles = ms_kwargs["subplot_titles"]
    assert titles[0] == "CPU Usage (%)"
    assert titles[1] == "Memory Usage (KB)"
    assert titles[2] == "System Load"
    assert titles[3] == "Swap Usage (KB)"
    assert titles[4] == "Block I/O"

    assert fake_fig.add_trace.call_count == go_mod.Scatter.call_count

    unix_rounded = int(1_738_934_940.0)
    expected_base = tmp_path / f"vmstatviz_{unix_rounded}.html"
    assert out_name.endswith(".html")
    assert "vmstatviz" in out_name
    fake_fig.write_html.assert_called_once_with(str(expected_base.name))

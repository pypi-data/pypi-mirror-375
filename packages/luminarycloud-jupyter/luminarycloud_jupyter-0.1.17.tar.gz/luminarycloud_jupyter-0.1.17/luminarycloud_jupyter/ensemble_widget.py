from typing import Any
import array
import anywidget
import pathlib

import traitlets

base_path = pathlib.Path(__file__).parent / "static"


class ScatterPlotData:
    x: list[float]
    y: list[float]
    name: str
    mode: str

    def __init__(self) -> None:
        self.x = []
        self.y = []
        self.name = ""
        self.mode = "markers"


class EnsembleWidget(anywidget.AnyWidget):
    _esm = base_path / "ensemble_widget.js"

    row_metadata = traitlets.List([]).tag(sync=True)
    n_rows = traitlets.Int(1).tag(sync=True)
    n_cols = traitlets.Int(1).tag(sync=True)

    widget_ready = False

    # Commands we need to buffer up because calls were made
    # before the widget was ready. The normal Jupyter comm stuff
    # doesn't buffer messages before the widget is up, they just get
    # discarded
    buffered_commands: list[dict] = []

    def __init__(
        self, row_metadata: list[dict[str, str | float]], n_rows: int, n_cols: int, **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.on_msg(self._receive_widget_message)
        self.row_metadata = row_metadata
        self.n_rows = n_rows
        self.n_cols = n_cols

    def set_cell_data(self, row: int, col: int, data: bytes, data_type: str) -> None:
        self._send_or_buffer_cmd(
            {
                "cmd": "set_cell_data",
                "cell": [row, col],
                "data_type": data_type,
            },
            [data],
        )

    def set_cell_scatter_plot(
        self,
        row: int,
        col: int,
        title: str,
        x_label: str,
        y_label: str,
        plot_data: list[ScatterPlotData],
    ) -> None:
        cmd = {
            "cmd": "set_cell_data",
            "cell": [row, col],
            "data_type": "scatter_plot",
            "cell_extra": {
                "title": title,
                "axis_labels": [x_label, y_label],
                "plot_names": [p.name for p in plot_data],
                "plot_modes": [p.mode for p in plot_data],
            },
        }
        scatter_data: list[bytes] = []
        for p in plot_data:
            scatter_data.append(array.array("f", p.x).tobytes())
            scatter_data.append(array.array("f", p.y).tobytes())
        self._send_or_buffer_cmd(cmd, scatter_data)

    def _receive_widget_message(self, widget: Any, content: str, buffers: list[memoryview]) -> None:
        if content == "widget_ready":
            self.widget_ready = True
            self._send_buffered_commands()

    # TODO will: I can share this buffering between the widgets
    def _send_or_buffer_cmd(self, cmd: dict, buffers: list[bytes] | None = None) -> None:
        """
        If command-based calls are made before the widget is ready we need
        to buffer them and wait til the widget is ready to receive them. Otherwise,
        the default Jupyter comm support doesn't buffer them and the commands are
        simply discarded.
        """
        if self.widget_ready:
            self.send(cmd, buffers)
        else:
            self.buffered_commands.append({"cmd": cmd, "buffers": buffers})

    def _send_buffered_commands(self) -> None:
        for cmd in self.buffered_commands:
            self.send(cmd["cmd"], cmd["buffers"])
        self.buffered_commands = []

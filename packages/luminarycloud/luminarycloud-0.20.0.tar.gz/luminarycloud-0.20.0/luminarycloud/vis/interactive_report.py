import io
from . import ExtractOutput
from .vis_util import _InternalToken, _get_status
from .visualization import RenderOutput
from ..enum import ExtractStatusType
from .._client import get_default_client
from .._proto.api.v0.luminarycloud.vis import vis_pb2

try:
    import luminarycloud_jupyter as lcj
except ImportError:
    lcj = None


# TODO Will/Matt: this could be something like what we store in the DB
# A report can contain a list of report entries that reference post proc.
# extracts + styling info for how they should be displayed
class ReportEntry:
    def __init__(
        self, project_id: str, extract_ids: list[str] = [], metadata: dict[str, str | float] = {}
    ) -> None:
        self._project_id = project_id
        self._extract_ids = extract_ids
        self._extracts: list[ExtractOutput | RenderOutput] = []
        self._metadata = metadata

    # Download all extracts for this report entry
    def download_extracts(self) -> None:
        self._extracts = []
        for eid in self._extract_ids:
            status = _get_status(self._project_id, eid)
            if status != ExtractStatusType.COMPLETED:
                raise Exception(f"Extract {eid} is not complete")
            req = vis_pb2.DownloadExtractRequest()
            req.extract_id = eid
            req.project_id = self._project_id
            # TODO: This is a bit awkward in that we download the extract to figure out what type
            # it is, but this is just a temporary thing, later we'll have a report DB table that
            # stores the extracts for a report and their types, etc.
            res: vis_pb2.DownloadExtractResponse = get_default_client().DownloadExtract(req)
            extract = (
                ExtractOutput(_InternalToken())
                if res.HasField("line_data")
                else RenderOutput(_InternalToken())
            )
            extract._set_data(eid, self._project_id, eid, eid, status)
            self._extracts.append(extract)


class InteractiveReport:
    # TODO Will/Matt: this list of report entries could be how we store stuff in the DB
    # for interactive reports, to reference the post proc. extracts. A report is essentially
    # a bunch of extracts + metadata.
    def __init__(self, entries: list[ReportEntry]) -> None:
        if not lcj:
            raise ImportError("InteractiveScene requires luminarycloud[jupyter] to be installed")

        self.entries = entries
        if len(self.entries) == 0:
            raise ValueError("Invalid number of entries, must be > 0")

        report_data = []
        for row, re in enumerate(self.entries):
            row_data = []
            re.download_extracts()
            for extract in re._extracts:
                if isinstance(extract, RenderOutput):
                    image_and_label = extract.download_images()
                    row_data.extend([il[0] for il in image_and_label])
                else:
                    plot_data = extract.download_data()
                    # Plot absolute pressure for each intersection curve we have
                    # TODO will: make these params of the extract/report entry
                    # We'll pick the first item that's not x/y/z coordinates to be the data we plot
                    x_axis = "x"
                    y_axis = [n for n in plot_data[0][0][0] if n != "x" and n != "y" and n != "z"][
                        0
                    ]
                    scatter_plots = []
                    for p in plot_data:
                        data = p[0]
                        x_idx = data[0].index(x_axis)
                        y_idx = data[0].index(y_axis)

                        scatter_data = lcj.ScatterPlotData()
                        scatter_data.name = f"plot-{row}"
                        for r in data[1:]:
                            scatter_data.x.append(r[x_idx])
                            scatter_data.y.append(r[y_idx])
                        scatter_plots.append(scatter_data)
                    row_data.append(scatter_plots)

            report_data.append(row_data)

        # TODO Validate the grid configuration is valid, all report entries should have the
        # same # of extract IDs and metadata keys
        # maybe not needed, b/c this is something we'd control internally later?
        nrows = len(report_data)
        ncols = len(report_data[0]) if len(report_data) > 0 else 0

        for i, r in enumerate(report_data):
            if len(r) != ncols:
                raise ValueError(
                    f"Invalid report configuration: row {i} does not have {ncols} columns"
                )

        self.widget = lcj.EnsembleWidget([re._metadata for re in self.entries], nrows, ncols)
        for row, row_data in enumerate(report_data):
            for col, col_data in enumerate(row_data):
                if isinstance(col_data, list) and isinstance(col_data[0], lcj.ScatterPlotData):
                    x_axis = "x"
                    y_axis = "Absolute Pressure (Pa)"
                    self.widget.set_cell_scatter_plot(
                        row, col, f"{row} {y_axis} v {x_axis}", x_axis, y_axis, col_data
                    )
                elif isinstance(col_data, io.BytesIO):
                    self.widget.set_cell_data(row, col, col_data.getvalue(), "jpg")

    def _ipython_display_(self) -> None:
        """
        When the InteractiveReport is shown in Jupyter we show the underlying widget
        to run the widget's frontend code
        """
        self.widget._ipython_display_()

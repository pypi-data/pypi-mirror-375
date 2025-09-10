from .visualization import Scene, RenderOutput
from .data_extraction import DataExtractor, ExtractOutput
from ..enum import RenderStatusType, ExtractStatusType
from ..solution import Solution
from time import sleep


# Notes(matt): we need a good way to pass "legend" information to the report.
# The legend is list of scalar values that are associated with each solution in
# the report. Examples include outputs like lift or drag, scalar ranges in the
# solutions, or any user provided data. We could add a helper class to auto-produce
# the legend data for common use cases or the user could provide their own. The data
# would look like a csv file or a dictionary keyed on the solution/sim id, where each
# entry is a list of scalar values. We would also need a header to describe what the values
# are.
class Report:
    def __init__(self, solutions: list[Solution]):
        self._scenes: list[Scene] = []
        self._data_extractors: list[DataExtractor] = []
        self._solution: list[Solution] = solutions
        # When we fire off requests we use these objects to track the progress.
        self._extract_outputs: list[ExtractOutput] = []
        self._render_outputs: list[RenderOutput] = []
        for solution in solutions:
            if not isinstance(solution, Solution):
                raise TypeError("Expected a list of Solution objects.")

    def add_scene(self, scene: Scene):
        if not isinstance(scene, Scene):
            raise TypeError("Expected a Scene object.")
        self._scenes.append(scene)

    def add_data_extractor(self, data_extractor: DataExtractor):
        if not isinstance(data_extractor, DataExtractor):
            raise TypeError("Expected a DataExtractor object.")
        self._data_extractors.append(data_extractor)

    def _check_status(self) -> bool:
        """Check the status of all render outputs and extract outputs."""
        still_pending = False
        print("\n" + "=" * 60)
        print("STATUS CHECK".center(60))
        print("=" * 60)

        if not self._render_outputs and not self._extract_outputs:
            raise RuntimeError("No render outputs or extract outputs to check status.")

        # Check render outputs
        if self._render_outputs:
            print(f"{'Type':<8} | {'ID':<20} | {'Status':<15}")
            print("-" * 60)

        for output in self._render_outputs:
            if (
                output.status != RenderStatusType.COMPLETED
                and output.status != RenderStatusType.FAILED
            ):
                output.refresh()
                still_pending = True
            print(f"{'Render':<8} | {str(output._extract_id):<20} | {output.status.name:<15}")

        # Check extract outputs
        for output in self._extract_outputs:
            if (
                output.status != ExtractStatusType.COMPLETED
                and output.status != ExtractStatusType.FAILED
            ):
                output.refresh()
                still_pending = True
            print(f"{'Extract':<8} | {str(output._extract_id):<20} | {output.status.name:<15}")

        print("=" * 60)
        return still_pending

    def create_report_data(self):
        for solution in self._solution:
            for scene in self._scenes:
                sol_scene = scene.clone(solution)
                self._render_outputs.append(
                    sol_scene.render_images(
                        name="Report Scene", description="Generated Report Scene"
                    )
                )
            for extractor in self._data_extractors:
                sol_extractor = extractor.clone(solution)
                self._extract_outputs.append(
                    sol_extractor.create_extracts(
                        name="Report Extract", description="Generated Report Extract"
                    )
                )

    def wait_for_completion(self):
        """Wait for all render and extract outputs to complete."""
        if not self._render_outputs and not self._extract_outputs:
            raise RuntimeError("No render outputs or extract outputs to wait for.")
        while self._check_status():
            sleep(5)
        print("All render and extract outputs have completed.")

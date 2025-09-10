from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from ...output.formatters.default import (
    DefaultBuildOutputFormatter,
    DefaultExecutableTestCaseFormatter,
    DefaultMetadataFormatter,
    DefaultPreprocessorOutputFormatter,
    DefaultRuntimeSummaryFormatter,
)
from ...output.formatters.interfaces import (
    BuildOutputFormatterInterface,
    ExecutableTestFormatterInterface,
    MetadataFormatterInterface,
    PreprocessorOutputFormatterInterface,
    RuntimeSummaryFormatterInterface,
)
from ...output.raw_json.assignment import AssignmentJSON
from ...output.raw_json.test_case import TestCaseJSON
from ...tests.test.interface import ExecutableTestInterface
from .types import AssignmentMetadata, BuilderOutput, PreprocessorOutput


class AssignmentSummary(BaseModel):
    model_config = {"arbitrary_types_allowed": True}

    metadata: AssignmentMetadata
    preprocessor_output: PreprocessorOutput
    build_output: BuilderOutput
    test_cases: List[ExecutableTestInterface]

    metadata_fmt: MetadataFormatterInterface = Field(
        default_factory=DefaultMetadataFormatter, exclude=True
    )
    preprocessor_output_fmt: PreprocessorOutputFormatterInterface = Field(
        default_factory=DefaultPreprocessorOutputFormatter, exclude=True
    )
    build_output_fmt: BuildOutputFormatterInterface = Field(
        default_factory=DefaultBuildOutputFormatter, exclude=True
    )
    runtime_summary_fmt: RuntimeSummaryFormatterInterface = Field(
        default_factory=DefaultRuntimeSummaryFormatter, exclude=True
    )
    test_case_fmt: ExecutableTestFormatterInterface = Field(
        default_factory=DefaultExecutableTestCaseFormatter, exclude=True
    )

    @classmethod
    def set_formatters(
        cls,
        *,
        metadata: Optional[MetadataFormatterInterface] = None,
        preprocessor_output: Optional[PreprocessorOutputFormatterInterface] = None,
        build_output: Optional[BuildOutputFormatterInterface] = None,
        runtime_summary: Optional[RuntimeSummaryFormatterInterface] = None,
        test_case: Optional[ExecutableTestFormatterInterface] = None,
    ):
        if metadata is not None:
            cls.metadata_fmt = metadata
        if preprocessor_output is not None:
            cls.preprocessor_output_fmt = preprocessor_output
        if build_output is not None:
            cls.build_output_fmt = build_output
        if runtime_summary is not None:
            cls.runtime_summary_fmt = runtime_summary
        if test_case is not None:
            cls.test_case_fmt = test_case

    def get_assignment_text(self):
        return (
            f"\n{self.metadata_fmt.format(self.metadata)}"
            f"{self.preprocessor_output_fmt.format(self.preprocessor_output)}\n\n"
            f"{self.build_output_fmt.format(self.build_output)}\n\n"
            f"{self.runtime_summary_fmt.format(self.test_cases)}\n\n"
        )

    def get_score_multiplier(self):
        total_score = sum([test_case.get_weight() for test_case in self.test_cases])
        return 100.0 / total_score if total_score else 0.0

    def get_raw(self) -> AssignmentJSON:
        return AssignmentJSON(
            output=self.get_assignment_text(),
            visibility="visible",
            tests=[
                TestCaseJSON(
                    name=test_case.get_name(),
                    output=self.test_case_fmt.format(test_case),
                    score=self.get_score_multiplier()
                    * test_case.get_weight()
                    * test_case.get_successful()
                    * test_case.get_penalty(),
                    max_score=self.get_score_multiplier() * test_case.get_weight(),
                )
                for test_case in self.test_cases
            ],
            leaderboard=None,  # TODO: Add leaderboard support.
        )

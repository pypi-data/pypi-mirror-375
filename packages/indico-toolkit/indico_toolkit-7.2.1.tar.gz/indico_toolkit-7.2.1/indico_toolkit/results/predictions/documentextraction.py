from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..review import Review
from ..utils import get, has, omit
from .extraction import Extraction
from .group import Group
from .span import NULL_SPAN, Span

if TYPE_CHECKING:
    from typing import Any

    from ..document import Document
    from ..task import Task


@dataclass
class DocumentExtraction(Extraction):
    groups: "set[Group]"
    spans: "list[Span]"

    @property
    def span(self) -> Span:
        """
        Return the first `Span` the document extraction covers else `NULL_SPAN`.

        Post-review, document extractions have no spans.
        """
        return self.spans[0] if self.spans else NULL_SPAN

    @span.setter
    def span(self, span: Span) -> None:
        """
        Overwrite all spans with the one provided, handling `NULL_SPAN`.

        This is implemented under the assumption that if you're setting a single span,
        you want it to be the only one. And if you're working in a context that's
        multiple-span sensetive, you'll set `extraction.spans` instead.
        """
        self.spans = [span] if span else []

    @staticmethod
    def from_dict(
        document: "Document",
        task: "Task",
        review: "Review | None",
        prediction: object,
    ) -> "DocumentExtraction":
        """
        Create a `DocumentExtraction` from a prediction dictionary.
        """
        return DocumentExtraction(
            document=document,
            task=task,
            review=review,
            label=get(prediction, str, "label"),
            confidences=get(prediction, dict, "confidence"),
            text=get(prediction, str, "normalized", "formatted"),
            accepted=(
                has(prediction, bool, "accepted") and get(prediction, bool, "accepted")
            ),
            rejected=(
                has(prediction, bool, "rejected") and get(prediction, bool, "rejected")
            ),
            groups=set(map(Group.from_dict, get(prediction, list, "groupings"))),
            spans=sorted(map(Span.from_dict, get(prediction, list, "spans"))),
            extras=omit(
                prediction,
                "label",
                "confidence",
                "accepted",
                "rejected",
                "groupings",
                "spans",
            ),
        )

    def to_dict(self) -> "dict[str, Any]":
        """
        Create a prediction dictionary for auto review changes.
        """
        prediction = {
            **self.extras,
            "label": self.label,
            "confidence": self.confidences,
            "groupings": [group.to_dict() for group in self.groups],
            "spans": [span.to_dict() for span in self.spans],
        }

        if self.text != get(prediction, str, "normalized", "formatted"):
            prediction["normalized"]["formatted"] = self.text
            prediction["normalized"]["text"] = self.text
            prediction["text"] = self.text

        if self.accepted:
            prediction["accepted"] = True
        elif self.rejected:
            prediction["rejected"] = True

        return prediction

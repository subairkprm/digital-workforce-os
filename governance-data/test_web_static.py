import unittest
from html.parser import HTMLParser
from pathlib import Path


VOID_ELEMENTS = {
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
}


class StructureParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.views: list[str] = []
        self.buttons: list[str] = []
        self.stack: list[str] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"] or "")
        if values.get("data-view"):
            self.views.append(values["data-view"] or "")
        if values.get("data-view-button"):
            self.buttons.append(values["data-view-button"] or "")
        if tag not in VOID_ELEMENTS:
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID_ELEMENTS:
            return
        if not self.stack or self.stack[-1] != tag:
            self.errors.append(f"Unexpected closing tag: {tag}")
            return
        self.stack.pop()


class DashboardStaticTests(unittest.TestCase):
    def setUp(self) -> None:
        html_path = Path(__file__).parent.parent / "governance-web" / "index.html"
        self.parser = StructureParser()
        self.parser.feed(html_path.read_text(encoding="utf-8"))
        self.parser.close()

    def test_html_has_balanced_explicit_tags_and_unique_ids(self) -> None:
        self.assertEqual(self.parser.errors, [])
        self.assertEqual(self.parser.stack, [])
        duplicates = sorted({item for item in self.parser.ids if self.parser.ids.count(item) > 1})
        self.assertEqual(duplicates, [])

    def test_dynamic_targets_and_tabs_are_complete(self) -> None:
        required = {
            "live-status",
            "refresh-status",
            "source-value",
            "current-gate",
            "updated-at",
            "current-message",
            "deployment-status",
            "accepted-progress",
            "implemented-progress",
            "open-review-count",
            "exception-count",
            "stage-rows",
            "implemented-readiness",
            "implemented-bar",
            "accepted-readiness",
            "accepted-bar",
            "quality-title",
            "quality-status",
            "quality-checks",
            "review-list",
            "deviation-list",
            "local-ci-result",
            "local-ci-commit",
            "local-ci-completed",
            "local-ci-duration",
            "local-ci-runner",
            "local-ci-scope",
            "local-ci-remote",
        }
        self.assertTrue(required.issubset(set(self.parser.ids)))
        self.assertEqual(sorted(self.parser.buttons), sorted(self.parser.views))
        self.assertEqual(len(self.parser.buttons), len(set(self.parser.buttons)))


if __name__ == "__main__":
    unittest.main()

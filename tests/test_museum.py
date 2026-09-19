import json
import shutil
import tempfile
import unittest
from pathlib import Path

from evidence_archive_museum import load_archive, render_html, write_html


FIXTURE = Path(__file__).parents[1] / "examples" / "synthetic_archive"


class MuseumTests(unittest.TestCase):
    def test_valid_archive_has_recomputed_verification(self) -> None:
        archive = load_archive(FIXTURE)
        self.assertEqual(archive.verification["records"], 4)
        self.assertEqual(archive.verification["records_with_sources"], 4)
        self.assertEqual(archive.verification["adjacency_links"], 4)

    def test_duplicate_record_ids_fail(self) -> None:
        with self.fixture_copy() as root:
            line = (root / "records.jsonl").read_text(encoding="utf-8").splitlines()[0]
            with (root / "records.jsonl").open("a", encoding="utf-8") as stream:
                stream.write(line + "\n")
            with self.assertRaises(ValueError):
                load_archive(root)

    def test_source_paths_must_be_relative(self) -> None:
        with self.fixture_copy() as root:
            rows = [json.loads(line) for line in (root / "records.jsonl").read_text(encoding="utf-8").splitlines()]
            rows[0]["sources"] = ["C:/private/evidence.json"]
            (root / "records.jsonl").write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_archive(root)

    def test_missing_record_reference_fails(self) -> None:
        with self.fixture_copy() as root:
            groups = json.loads((root / "groups.json").read_text(encoding="utf-8"))
            groups[0]["record_ids"] = ["missing"]
            (root / "groups.json").write_text(json.dumps(groups), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_archive(root)

    def test_missing_and_self_adjacency_fail(self) -> None:
        for adjacent in (["missing"], ["importer"]):
            with self.fixture_copy() as root:
                groups = json.loads((root / "groups.json").read_text(encoding="utf-8"))
                groups[0]["adjacent"] = adjacent
                (root / "groups.json").write_text(json.dumps(groups), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_archive(root)

    def test_era_range_and_group_refs_are_validated(self) -> None:
        with self.fixture_copy() as root:
            eras = json.loads((root / "eras.json").read_text(encoding="utf-8"))
            eras[0]["end"] = "2024-01-01"
            (root / "eras.json").write_text(json.dumps(eras), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_archive(root)

    def test_disposition_status_and_successor_are_validated(self) -> None:
        with self.fixture_copy() as root:
            dispositions = json.loads((root / "dispositions.json").read_text(encoding="utf-8"))
            dispositions["importer"]["status"] = "magical"
            (root / "dispositions.json").write_text(json.dumps(dispositions), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_archive(root)

    def test_invalid_jsonl_reports_a_bounded_error(self) -> None:
        with self.fixture_copy() as root:
            (root / "records.jsonl").write_text("{broken}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "records.jsonl:1"):
                load_archive(root)

    def test_renderer_is_offline_and_escapes_script_breakouts(self) -> None:
        html = render_html(load_archive(FIXTURE), title="</script><script>alert(1)</script>")
        self.assertNotIn("</script><script>alert(1)", html)
        self.assertNotIn("https://", html)
        self.assertIn("application/json", html)
        self.assertIn("textContent", html)

    def test_atomic_writer_creates_complete_html(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "nested" / "index.html"
            content = render_html(load_archive(FIXTURE))
            write_html(output, content)
            self.assertEqual(output.read_text(encoding="utf-8"), content)
            self.assertEqual(list(output.parent.glob("*.tmp")), [])

    class fixture_copy:
        def __enter__(self):
            self.temporary = tempfile.TemporaryDirectory()
            self.root = Path(self.temporary.name) / "archive"
            shutil.copytree(FIXTURE, self.root)
            return self.root

        def __exit__(self, exc_type, exc, tb):
            self.temporary.cleanup()


if __name__ == "__main__":
    unittest.main()

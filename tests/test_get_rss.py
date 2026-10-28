import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.get_rss import (
    RunLogger,
    convert_xml_to_feed_data,
    entry_link,
    fetch_feed_xml,
    find_new_entry,
    newest_entry,
    main,
    FEED_FRONT_MATTER,
    update_null_to_current_date,
)


class GetRssTests(unittest.TestCase):
    def test_feed_update_preserves_template_metadata_and_detects_unchanged_xml(self) -> None:
        xml = '<feed><updated>2026-10-28T12:00:00Z</updated><entry><id>https://example.org/1</id><title>A &amp; B</title></entry></feed>'
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            saved = root / "feed.xml"
            with patch("scripts.get_rss.XML_FILE", saved), patch(
                "scripts.get_rss.JSON_FILE", root / "feed.json"
            ), patch("scripts.get_rss.OLD_XML_FILE", root / "old_feed.xml"), patch(
                "scripts.get_rss.fetch_feed_xml", return_value=xml
            ), patch(
                "scripts.get_rss.RunLogger", side_effect=lambda: RunLogger(root / "RUNLOG.md")
            ), patch("scripts.get_rss.set_github_outputs") as outputs:
                main()
                self.assertEqual(saved.read_text(), FEED_FRONT_MATTER + xml)
                outputs.assert_called_with(True, None)
                main()
                outputs.assert_called_with(False, None)
            self.assertEqual(saved.read_text(), FEED_FRONT_MATTER + xml)
            self.assertFalse((root / "old_feed.xml").exists())

    def test_failed_fetch_preserves_feed_and_reports_failure(self) -> None:
        with TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            xml = root / "feed.xml"
            xml.write_text("original feed")
            with patch("scripts.get_rss.XML_FILE", xml), patch(
                "scripts.get_rss.OLD_XML_FILE", root / "old_feed.xml"
            ), patch("scripts.get_rss.fetch_feed_xml", side_effect=RuntimeError("offline")), patch(
                "scripts.get_rss.RunLogger", return_value=RunLogger(root / "RUNLOG.MD")
            ), patch("scripts.get_rss.set_github_outputs") as outputs:
                with self.assertRaisesRegex(RuntimeError, "offline"):
                    main()
            self.assertEqual(xml.read_text(), "original feed")
            self.assertFalse((root / "old_feed.xml").exists())
            outputs.assert_called_once_with(False, None)
            self.assertIn("failed", (root / "RUNLOG.MD").read_text())

    def test_newest_entry_returns_first_atom_entry(self) -> None:
        entry = {"id": "new", "title": "Newest"}

        self.assertEqual(newest_entry({"feed": {"entry": [entry, {"id": "old"}]}}), entry)

    def test_find_new_entry_only_returns_changed_top_entry(self) -> None:
        old_feed = {"feed": {"entry": [{"id": "old"}]}}
        new_entry = {"id": "new", "title": "Newest"}

        self.assertEqual(find_new_entry(old_feed, {"feed": {"entry": [new_entry]}}), new_entry)
        self.assertIsNone(find_new_entry(old_feed, old_feed))

    def test_update_null_to_current_date_handles_single_entry_dict(self) -> None:
        feed_data = {
            "feed": {
                "updated": None,
                "entry": {
                    "title": "Only entry",
                    "updated": None,
                },
            }
        }

        updated_feed = update_null_to_current_date(feed_data)

        self.assertIsInstance(updated_feed["feed"]["entry"], list)
        self.assertEqual(len(updated_feed["feed"]["entry"]), 1)
        self.assertIsNotNone(updated_feed["feed"]["updated"])
        self.assertIsNotNone(updated_feed["feed"]["entry"][0]["updated"])

    def test_convert_xml_to_feed_data_repairs_common_entity_issues(self) -> None:
        xml_text = """<?xml version="1.0" encoding="utf-8"?>
<feed>
  <title>AT&amp;T &nbsp; CFP & Religion</title>
  <updated></updated>
  <entry>
    <title>First &nbsp; Entry</title>
    <updated></updated>
  </entry>
</feed>
"""

        feed_data = convert_xml_to_feed_data(xml_text)

        self.assertEqual(feed_data["feed"]["title"], "AT&T \xa0 CFP & Religion")
        self.assertEqual(feed_data["feed"]["entry"][0]["title"], "First \xa0 Entry")
        self.assertIsNotNone(feed_data["feed"]["updated"])
        self.assertIsNotNone(feed_data["feed"]["entry"][0]["updated"])

    def test_run_logger_writes_markdown_with_errors(self) -> None:
        with TemporaryDirectory() as tmpdir:
            runlog_path = Path(tmpdir) / "RUNLOG.MD"
            run_log = RunLogger(runlog_path)
            run_log.status = "failed"
            run_log.content_changed = False
            run_log.feed_entries = 0
            run_log.log("requests status: 403")
            run_log.error("curl returned status 404")
            run_log.write()

            content = runlog_path.read_text(encoding="utf-8")

        self.assertIn("# RUNLOG", content)
        self.assertIn("requests status: 403", content)
        self.assertIn("curl returned status 404", content)
        self.assertIn("## Errors", content)

    def test_fetch_feed_xml_uses_fallback_url_after_primary_403(self) -> None:
        run_log = RunLogger()
        xml_text = "<?xml version='1.0'?><feed><updated>2026-04-07T00:00:00Z</updated></feed>"

        with patch(
            "scripts.get_rss.fetch_with_requests",
            side_effect=[(403, "forbidden"), (200, xml_text)],
        ) as mock_requests, patch(
            "scripts.get_rss.fetch_with_curl", return_value=(403, "forbidden")
        ) as mock_curl:
            result = fetch_feed_xml(
                (
                    "https://input.relcfp.com/feed.xml",
                    "https://input-relcfp.netlify.app/feed.xml",
                ),
                run_log,
            )

        self.assertEqual(result, xml_text)
        self.assertEqual(mock_requests.call_count, 2)
        mock_requests.assert_any_call("https://input.relcfp.com/feed.xml")
        mock_requests.assert_any_call("https://input-relcfp.netlify.app/feed.xml")
        mock_curl.assert_called_once_with("https://input.relcfp.com/feed.xml")
        self.assertTrue(
            any("primary requests returned status 403" in entry for entry in run_log.errors)
        )

    def test_entry_link_handles_every_atom_link_shape(self) -> None:
        # An empty uri here is what made Bluesky reject the post with a 400.
        cases = {
            "single": ({"link": {"@href": "https://x/1"}, "id": "https://x/1"}, "https://x/1"),
            "missing": ({"id": "https://x/2"}, "https://x/2"),
            "empty element": ({"link": None, "id": "https://x/3"}, "https://x/3"),
            "prefers alternate": (
                {
                    "link": [
                        {"@href": "https://x/4.mp3", "@rel": "enclosure"},
                        {"@href": "https://x/4", "@rel": "alternate"},
                    ],
                    "id": "https://x/4",
                },
                "https://x/4",
            ),
            "no href attr": ({"link": {"@rel": "alternate"}, "id": "https://x/5"}, "https://x/5"),
            "nothing usable": ({}, ""),
        }

        for name, (entry, expected) in cases.items():
            with self.subTest(name):
                self.assertEqual(entry_link(entry), expected)


if __name__ == "__main__":
    unittest.main()

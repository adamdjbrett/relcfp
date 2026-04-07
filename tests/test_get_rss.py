import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from get_rss import RunLogger, convert_xml_to_feed_data, update_null_to_current_date


class GetRssTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import patch

from collector import (
    SearchCriteria,
    collect_jobs,
    fetch_arbeitnow,
    fetch_remote_ok,
    remote_ok_jobs,
)


class CollectorTests(unittest.TestCase):
    def test_collects_from_requested_source(self) -> None:
        criteria = SearchCriteria(
            job_title="Python Developer",
            location="",
            experience="3 years",
            work_type="remote",
        )
        result = collect_jobs(
            criteria,
            fetchers={
                "remoteok": lambda _: [
                    {
                        "source": "Demo",
                        "source_job_id": "1",
                        "title": "Python Developer",
                        "url": "https://example.test/job/1",
                    }
                ]
            },
        )

        self.assertEqual(result["job_count"], 1)
        self.assertEqual(result["jobs"][0]["source"], "Demo")
        self.assertEqual(result["failed_sources"], [])

    def test_records_unsupported_source_as_a_failure(self) -> None:
        criteria = SearchCriteria(
            job_title="Python Developer",
            location="",
            experience="",
            work_type="onsite",
        )
        result = collect_jobs(criteria, fetchers={})

        self.assertEqual(result["job_count"], 0)
        self.assertEqual(result["failed_sources"][0]["source"], "arbeitnow")

    @patch("collector.fetch_json", return_value=[])
    def test_remote_ok_uses_separate_title_words_as_tags(self, fetch_json) -> None:
        fetch_remote_ok(SearchCriteria("Data Analyst", "", "", "remote"))

        self.assertIn("tags=data%2Canalyst", fetch_json.call_args_list[0].args[0])
        self.assertIn("tag=data", fetch_json.call_args_list[1].args[0])

    def test_remote_ok_output_is_compact(self) -> None:
        jobs = remote_ok_jobs(
            [
                {
                    "position": "Data Analyst",
                    "company": "Example Co",
                    "location": "Remote",
                    "description": "<p>Analyze product data. Build reports every week.</p>",
                    "tags": ["data", "sql", "python", "extra"],
                    "url": "https://example.test/job/1",
                }
            ],
            20,
        )

        self.assertEqual(jobs[0]["tags"], ["data", "sql", "python"])
        self.assertEqual(jobs[0]["description"], "Analyze product data.")
        self.assertNotIn("raw", jobs[0])

    @patch(
        "collector.fetch_json",
        return_value={
            "data": [
                {
                    "slug": "data-analyst-1",
                    "title": "Data Analyst",
                    "company_name": "\u00d8\u00b9\u00d8\u00b1\u00d8\u00a8\u00d9\u008a",
                    "location": "Dhaka",
                    "description": "<p>\u00d8\u00b9\u00d8\u00b1\u00d8\u00a8\u00d9\u008a \u00d8\u00a7\u00d9\u0084\u00d9\u0086\u00d8\u00b5.</p>",
                    "tags": ["data", "sql", "python", "extra"],
                    "url": "https://example.test/job/1",
                    "remote": False,
                }
            ]
        },
    )
    def test_local_source_repairs_mojibake_and_limits_tags(self, _fetch_json) -> None:
        jobs = fetch_arbeitnow(SearchCriteria("Data Analyst", "Dhaka", "entry", "onsite"))

        self.assertEqual(jobs[0]["company"], "عربي")
        self.assertEqual(jobs[0]["description"], "عربي النص.")
        self.assertEqual(jobs[0]["tags"], ["data", "sql", "python"])

    def test_unrecoverable_text_is_replaced_with_clear_fallback(self) -> None:
        jobs = remote_ok_jobs(
            [{"position": "Data Analyst", "company": "Ø¹Ø³ÙØ±", "description": "Ø¹Ø³ÙØ±"}],
            20,
        )

        self.assertEqual(jobs[0]["company"], "No useful information")
        self.assertEqual(jobs[0]["description"], "No useful information")


if __name__ == "__main__":
    unittest.main()

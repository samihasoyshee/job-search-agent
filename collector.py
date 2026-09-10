"""Interactive, script-first job collection stage.

This module collects raw listings only. It does not rank, score, evaluate with
AI, deduplicate, or apply to jobs. Remote OK is available without credentials;
Adzuna is enabled only when its approved API credentials are configured.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass
from html import unescape
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


REMOTE_OK_API_URL = "https://remoteok.com/api"
ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api"
ADZUNA_API_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/1"
FetchFunction = Callable[["SearchCriteria"], list[dict[str, Any]]]


@dataclass(frozen=True)
class SearchCriteria:
    """The collection inputs requested from the user at the terminal."""

    job_title: str
    location: str
    experience: str
    work_type: str


DEFAULT_RESULT_LIMIT = 20


def fetch_json(url: str) -> Any:
    """Fetch JSON using only Python's standard library."""
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "JobSearchAgent/0.1"},
    )
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def repair_text(value: Any) -> str:
    """Repair up to two common UTF-8-as-Latin-1 mojibake passes."""
    text = unescape(str(value or ""))
    for _ in range(2):
        try:
            repaired = text.encode("latin-1").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if repaired == text:
            break
        text = repaired
    return text


def useful_text(value: Any) -> str:
    """Return readable source text, or a clear fallback for unusable content."""
    text = repair_text(value).strip()
    mojibake_markers = sum(text.count(marker) for marker in ("Ø", "Ù", "Â", "�"))
    return text if text and mojibake_markers < 2 else "No useful information"


def one_line_description(value: Any) -> str:
    """Make a short, deterministic display summary from source HTML/text."""
    text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", useful_text(value))).strip()
    if text == "No useful information":
        return text
    sentence = re.split(r"(?<=[.!?])\s", text, maxsplit=1)[0]
    return sentence[:200].rstrip() + ("…" if len(sentence) > 200 else "")


def remote_ok_jobs(payload: Any, result_limit: int) -> list[dict[str, Any]]:
    """Convert Remote OK job records to the compact collection contract."""
    if not isinstance(payload, list):
        raise ValueError("Remote OK returned an unexpected response format.")

    jobs: list[dict[str, Any]] = []
    for listing in payload:
        if not isinstance(listing, dict) or "position" not in listing:
            continue
        source_tags = listing.get("tags") if isinstance(listing.get("tags"), list) else []
        jobs.append(
            {
                "source": "Remote OK",
                "source_job_id": str(listing.get("id", "")),
                "title": useful_text(listing.get("position")),
                "company": useful_text(listing.get("company")),
                "location": useful_text(listing.get("location") or "Remote"),
                "description": one_line_description(listing.get("description")),
                "tags": [useful_text(tag) for tag in source_tags[:3]],
                "url": listing.get("url") or listing.get("apply_url"),
            }
        )
        if len(jobs) >= result_limit:
            break
    return jobs


def fetch_remote_ok(criteria: SearchCriteria) -> list[dict[str, Any]]:
    """Collect raw jobs from Remote OK's public JSON feed."""
    tags = re.findall(r"[a-z0-9]+", criteria.job_title.casefold())
    payload = fetch_json(f"{REMOTE_OK_API_URL}?{urlencode({'tags': ','.join(tags)})}")
    jobs = remote_ok_jobs(payload, DEFAULT_RESULT_LIMIT)

    # One bounded retry: a broad single-tag query when the specific title fails.
    if not jobs and len(tags) > 1:
        payload = fetch_json(f"{REMOTE_OK_API_URL}?{urlencode({'tag': tags[0]})}")
        jobs = remote_ok_jobs(payload, DEFAULT_RESULT_LIMIT)
    return jobs


def fetch_arbeitnow(criteria: SearchCriteria) -> list[dict[str, Any]]:
    """Collect local listings from Arbeitnow's unauthenticated public feed."""
    payload = fetch_json(ARBEITNOW_API_URL)
    listings = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(listings, list):
        raise ValueError("Arbeitnow returned an unexpected response format.")

    title_words = re.findall(r"[a-z0-9]+", criteria.job_title.casefold())
    location = criteria.location.casefold().strip()
    jobs: list[dict[str, Any]] = []
    for listing in listings:
        if not isinstance(listing, dict) or bool(listing.get("remote")):
            continue
        title = useful_text(listing.get("title"))
        job_location = useful_text(listing.get("location"))
        if not all(word in title.casefold() for word in title_words):
            continue
        if location and location != "any" and location not in job_location.casefold():
            continue
        source_tags = listing.get("tags") if isinstance(listing.get("tags"), list) else []
        arrangement_text = " ".join(
            [title, job_location, repair_text(listing.get("description"))]
            + [repair_text(tag) for tag in source_tags]
        ).casefold()
        is_hybrid = "hybrid" in arrangement_text
        if criteria.work_type == "hybrid" and not is_hybrid:
            continue
        if criteria.work_type == "onsite" and is_hybrid:
            continue
        jobs.append(
            {
                "source": "Arbeitnow",
                "source_job_id": useful_text(listing.get("slug")),
                "title": title,
                "company": useful_text(listing.get("company_name")),
                "location": job_location,
                "description": one_line_description(listing.get("description")),
                "tags": [useful_text(tag) for tag in source_tags[:3]],
                "url": listing.get("url"),
            }
        )
        if len(jobs) >= DEFAULT_RESULT_LIMIT:
            break
    return jobs


def fetch_adzuna(criteria: SearchCriteria) -> list[dict[str, Any]]:
    """Collect raw jobs from Adzuna's official API using environment credentials."""
    app_id = os.environ.get("ADZUNA_APP_ID")
    app_key = os.environ.get("ADZUNA_APP_KEY")
    country_code = os.environ.get("ADZUNA_COUNTRY")
    if not app_id or not app_key or not country_code:
        raise RuntimeError(
            "Adzuna requires ADZUNA_APP_ID, ADZUNA_APP_KEY, and ADZUNA_COUNTRY environment variables."
        )

    parameters = urlencode(
        {
            "app_id": app_id,
            "app_key": app_key,
            "what": f"{criteria.job_title} {criteria.experience}".strip(),
            "where": criteria.location,
            "results_per_page": DEFAULT_RESULT_LIMIT,
            "content-type": "application/json",
        }
    )
    url = f"{ADZUNA_API_URL.format(country=country_code.casefold())}?{parameters}"
    payload = fetch_json(url)
    results = payload.get("results") if isinstance(payload, dict) else None
    if not isinstance(results, list):
        raise ValueError("Adzuna returned an unexpected response format.")

    return [
        {
            "source": "Adzuna",
            "source_job_id": str(listing.get("id", "")),
            "title": useful_text(listing.get("title")),
            "company": useful_text((listing.get("company") or {}).get("display_name")),
            "location": useful_text((listing.get("location") or {}).get("display_name")),
            "description": one_line_description(listing.get("description")),
            "tags": [],
            "url": listing.get("redirect_url"),
        }
        for listing in results[:DEFAULT_RESULT_LIMIT]
        if isinstance(listing, dict)
    ]


SOURCE_FETCHERS: dict[str, FetchFunction] = {
    "remoteok": fetch_remote_ok,
    "arbeitnow": fetch_arbeitnow,
    "adzuna": fetch_adzuna,
}


def collect_jobs(
    criteria: SearchCriteria, fetchers: dict[str, FetchFunction] | None = None
) -> dict[str, Any]:
    """Collect each requested source and explicitly retain failures."""
    available_fetchers = fetchers or SOURCE_FETCHERS
    jobs: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []

    source_names = ("remoteok",) if criteria.work_type == "remote" else ("arbeitnow",)
    for source in source_names:
        fetcher = available_fetchers.get(source)
        if fetcher is None:
            failures.append({"source": source, "reason": "Unsupported source."})
            continue
        try:
            jobs.extend(fetcher(criteria))
        except (HTTPError, URLError, TimeoutError, ValueError, RuntimeError) as error:
            failures.append({"source": source, "reason": str(error)})

    return {
        "criteria": asdict(criteria),
        "job_count": len(jobs),
        "jobs": jobs,
        "failed_sources": failures,
    }


def prompt_criteria() -> SearchCriteria:
    """Read a small, explicit collection scope from the terminal."""
    print("Job collection only: no ranking, AI evaluation, or applications.")
    job_title = input("Job title: ").strip()
    if not job_title:
        raise ValueError("Job title is required.")
    location = input("Location: ").strip()
    experience = input("Experience level (for example: entry level, 3 years): ").strip()
    work_type = input("Work type [onsite/hybrid/remote]: ").strip().casefold()
    work_type = {"on site": "onsite", "on-site": "onsite"}.get(work_type, work_type)
    if work_type not in {"onsite", "hybrid", "remote"}:
        raise ValueError("Work type must be onsite, hybrid, or remote.")

    return SearchCriteria(job_title, location, experience, work_type)


def main() -> None:
    try:
        criteria = prompt_criteria()
        print(json.dumps(collect_jobs(criteria), indent=2, ensure_ascii=False))
    except (EOFError, KeyboardInterrupt):
        print("\nCollection cancelled.")
    except ValueError as error:
        print(json.dumps({"error": str(error)}, indent=2))


if __name__ == "__main__":
    main()

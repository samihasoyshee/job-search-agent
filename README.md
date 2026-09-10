# job-search-agent
# Job Collector Experiment

A small, script-first experiment for the **Collection** stage of an AI job-search architecture. It collects current job listings from approved public sources and returns compact structured JSON.

This is not the full job-search agent. It does not process, deduplicate, rank, evaluate jobs with AI, submit applications, or automate follow-up work.

## Included files

- `collector.py` — interactive job collector.
- `tests/test_collector.py` — deterministic collector tests.
- `AGENTS.md` — project operating rules.
- `sop.md` — job-search standard operating procedure.
- `architecture.md` — intended full-pipeline architecture.

## Requirements

- Python 3.10 or newer.
- Internet access for live collection.

No third-party Python packages are required.

## Run the collector

From the project folder:

```powershell
python collector.py
```

The terminal asks for:

1. Job title
2. Location
3. Experience level
4. Work type: `onsite`, `hybrid`, or `remote`

The script prints collected records as JSON.

## Sources

| Work type | Source | Credentials |
| --- | --- | --- |
| `remote` | Remote OK public JSON feed | None |
| `onsite` | Arbeitnow public job-board feed | None |
| `hybrid` | Arbeitnow public job-board feed | None |

For Remote OK, the collector makes one specific title-tag search and, only when that returns no jobs, one broader fallback search. This retry is deliberately bounded.

Work-type classification depends on source metadata. A source may have no matching listings for a chosen location or work type; an empty `jobs` list is a valid result.

## Output format

Each job contains only collection-stage fields:

```json
{
  "source": "Remote OK",
  "source_job_id": "12345",
  "title": "Data Analyst",
  "company": "Example Company",
  "location": "Remote",
  "description": "One concise source-derived sentence.",
  "tags": ["data", "sql", "python"],
  "url": "https://example.com/job"
}
```

Descriptions are reduced to one source-derived sentence and tags are limited to three. Reversible text-encoding corruption is repaired deterministically. Missing or irrecoverable text is shown as `No useful information` rather than guessed.

The top-level response also includes `criteria`, `job_count`, and `failed_sources`. Failed sources are reported explicitly instead of silently ignored.

## Run tests

```powershell
python -m unittest discover -s tests -v
```

## Project boundary

This experiment follows the project’s script-first principle: Python handles deterministic job collection and no AI is used at this stage. The later architecture stages—processing, AI fit evaluation, ranking, and feedback—remain intentionally out of scope.


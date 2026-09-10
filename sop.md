# SOP.md

## Purpose

This SOP defines how the V1 AI job-search agent operates from a user's request to a ranked shortlist of suitable jobs.

## 1. Collect User Requirements

Collect:

- Target roles
- Target locations
- Skills and CV/resume information
- Experience level
- Work authorization or visa constraints
- Preferences
- Exclusions
- Target job websites or sources

Create a structured search profile.

## 2. Restatement and Governance Check

Before searching, restate the user's requirements in a concise form.

Confirm the intended:

- Roles
- Locations
- Constraints
- Preferences
- Sources

Apply the project's governance rules, boundaries, fallback rules, and output standards.

Do not begin the main search until the search scope is understood.

## 3. Orchestrate the Run

The job-search orchestrator manages the workflow and run context.

The run context may contain:

- Search criteria
- Selected sources
- Previous results
- User feedback
- Failed sources
- Retry state

Break the workflow into:

**Collection → Processing → Evaluation → Output**

The orchestrator coordinates these stages rather than performing every task itself.

## 4. Collect Jobs

Use deterministic scripts first.

Preferred collection methods:

1. Official API when available
2. Scraper or browser script
3. Search/X-ray fallback where appropriate

Search the approved:

- Job boards
- Company career pages
- Other target websites

If collection fails:

**Retry → Try an alternate method → Flag the source for manual review**

Do not hide collection failures.

Target approximately **1,000 raw job listings**.

Preserve source URLs and important original job information.

## 5. Process Jobs Deterministically

Use scripts for bulk processing.

Run:

**Parse → Normalize → Deduplicate → Validate → Hard Filter → Deterministic Pre-score**

### Parse

Extract important fields such as:

- Title
- Company
- Location
- Requirements
- Description
- URL

### Normalize

Standardize fields and formats.

### Deduplicate

Remove repeated listings.

### Validate

Remove or flag:

- Expired jobs
- Broken URLs
- Clearly invalid listings

### Hard Filter

Apply definite requirements such as:

- Role
- Location
- Experience
- Visa/work authorization
- Explicit exclusions

### Pre-score

Use deterministic signals such as:

- Keyword matches
- Skill overlap
- Requirement matches

Target approximately **200–300 candidate jobs** after processing.

## 6. AI Fit Evaluation

Use AI only after deterministic processing.

The AI evaluates the candidate pool using contextual reasoning.

Consider:

- Overall role fit
- Transferable skills
- Experience relevance
- Meaning of job requirements
- Potential red flags

For each job, produce a fit assessment and final fit score.

If a job is unsuitable, reject or archive it with a reason.

AI should not invent missing evidence.

## 7. Recursive Technique

When enabled, allow the system to review its own results and improve the next attempt.

Example:

**Search → Review Results → Identify Weakness → Refine Search → Retry**

Use recursion when results are clearly poor, such as when the search is too narrow or produces many irrelevant results.

Retries must be bounded. Do not allow indefinite loops.

Initially, recursive behavior should be tested as an experiment before becoming a core V1 feature.

## 8. Supervisor Technique

A supervisor agent may review the work of a worker agent.

Example:

**Supervisor → Worker → Result → Supervisor Review**

The supervisor checks whether the worker:

- Followed the task
- Used sufficient evidence
- Applied the correct criteria
- Produced a reasonable result

If the result is inadequate, the supervisor may request a retry or refinement.

The supervisor must use explicit evaluation criteria and should not blindly accept the worker's output.

Keep supervisor experiments separate from the core V1 pipeline until their usefulness is demonstrated.

## 9. Rank and Produce Output

Rank suitable jobs using the final fit score.

Target approximately **100 suitable jobs**.

Each result should contain:

- Company
- Role
- Location
- Fit score
- Short reason for the score
- Potential concern, when relevant
- Job URL

Provide a concise user-facing summary highlighting the strongest matches.

## 10. Human Feedback

Allow the user to mark recommendations as:

- Relevant
- Not relevant
- Very relevant

Also capture preference changes.

Use feedback to improve future:

- Search criteria
- Preferences
- Filters
- Search terms
- AI evaluation prompts

Do not automatically rewrite project governance files because of individual feedback. Changes to `AGENTS.md` or other shared rules require deliberate team approval.

## 11. Failure and Data Integrity

Never invent:

- Jobs
- Companies
- Requirements
- URLs
- Scores
- Evidence

When information is missing or uncertain, state the limitation.

When a source fails, record the failure and use an approved fallback when possible.

## 12. V1 Boundary

V1 focuses on:

**Job discovery → Processing → Evaluation → Ranking → User feedback**

The following are outside V1:

- Resume tailoring
- Cover-letter generation
- Automatic job applications
- Application tracking
- Follow-up automation

These may be considered for future versions.
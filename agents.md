# AGENTS.md

## Purpose

Build a V1 AI job-search agent that finds and ranks relevant jobs using a script-first, AI-assisted architecture.

## Core Principle

**Scripts handle bulk deterministic work. AI handles ambiguity and final reasoning.**

Do not use AI for tasks that can be reliably handled by deterministic code.

## Architecture

Follow this pipeline:

User Input → Restatement/Governance → Orchestrator → Collection → Processing → AI Evaluation → Ranked Output → Human Feedback

Target volumes:
- Raw jobs: ~1,000
- Candidate pool: ~200–300
- Final shortlist: ~100

## Divided Responsibilities

- collector — collect jobs from approved sources using APIs, scrapers, browser scripts, or search fallbacks.
- `processing — parse, normalize, deduplicate, validate, filter, and pre-score jobs.
- ai — evaluate job fit using contextual and semantic reasoning.
- orchestration — coordinate workflow, state, run context, and task delegation.
- tests — automated tests.
- experiments — recursive and supervisor-agent experiments. Keep experimental code separate from production V1.

## AI Rules

AI should evaluate:
- Role fit
- Skill transferability
- Experience relevance
- Requirement meaning
- Red flags

AI must not silently change hard filters, project rules, or user constraints.

Recursive behavior must be controlled and have bounded retries.

Supervisor agents should evaluate worker-agent results against explicit criteria rather than blindly accepting them.

## Data Integrity

Never invent job information, requirements, URLs, or evidence.

Preserve source URLs and important raw information.

Flag failed or unreliable sources instead of hiding failures.

## Development Rules

- Make small, focused changes.
- Read relevant project instructions before modifying code.
- Do not modify unrelated modules.
- Add or update tests when behavior changes.
- Run relevant tests before declaring a task complete.
- Report changed files, tests, results, and important assumptions.


## Definition of Done

A task is complete when:
1. It follows the architecture.
2. Important behavior is tested.
3. Relevant tests pass.
4. Data contracts are respected.
5. Necessary documentation is updated.

## Agent Safety

- Agent should not ask for privacy invading permission of the user. it should not ask for the permission of Camera, Microphone or ask or lead user to download unverified files.
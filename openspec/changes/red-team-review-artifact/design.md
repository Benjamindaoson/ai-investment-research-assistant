## Context

The runtime already stores counter and conflicting evidence and has a
human-decision path, but those are not the same as a structured red-team
challenge. A review must be durable and tied to the thesis that was actually
challenged.

## Goals / Non-Goals

**Goals:**

- Preserve reviewer, challenge, cited counter-evidence, outcome, and rationale.
- Reject dangling evidence and evidence with a supporting-only stance.
- Reuse engine write authority and append-only events.
- Make unresolved red-team outcomes visible without changing evidence truth.

**Non-Goals:**

- Automatic red-team generation by another agent.
- Editing or deleting historical reviews.
- Replacing the existing human thesis approval decision.

## Decisions

Create a RedTeamReview with immutable identity and append it to ResearchRun.
The API accepts a reviewer, challenge, optional evidence IDs, outcome, and
rationale. The engine requires an existing thesis, verifies all referenced
evidence belongs to the run, and requires each cited record to be COUNTER or
CONFLICTING.

REQUIRES_RESEARCH changes the thesis review status to NEEDS_REVIEW and keeps a
completed memo in READY_FOR_REVIEW. Other outcomes are recorded without
silently changing the evidence or thesis statement. A
RED_TEAM_REVIEW_RECORDED event captures the review payload.

## Risks / Trade-offs

- [Review evidence may itself need review] → The record preserves evidence
  qualification; this version requires counter/conflicting stance but does not
  auto-promote it.
- [No review edit endpoint] → Keep the first version append-only; add a
  superseding review workflow only when users need corrections.

## Migration Plan

The ResearchRun list is additive with an empty default, so existing SQLite
payloads remain readable. No schema migration is required.

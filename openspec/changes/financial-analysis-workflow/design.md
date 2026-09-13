## Context

Financial analysis is intentionally not inferred from evidence excerpts. The
workspace must make the input boundary visible: an analyst enters numeric
values and chooses evidence records that the runtime has already qualified.

## Goals / Non-Goals

**Goals:**

- Make the existing API usable from the live runtime page.
- Keep field-to-evidence pairing explicit.
- Prevent submission until required input and evidence are present.
- Reuse existing semantic controls and async mutation patterns.

**Non-Goals:**

- Automatic extraction from tables or filings.
- Full income statement modeling or valuation.
- Supporting unqualified evidence in the form.

## Decisions

Use a small form for period, revenue, and optional prior revenue. The form
renders select options from the current run's QUALIFIED evidence only. When
prior revenue is blank, no prior-revenue mapping is sent; when it is supplied,
its evidence selection becomes required.

Add a mutation hook that writes the returned runtime run into the existing
query cache. The artifact already returned by the backend then renders through
the current projection. No duplicate GET request or second client state store
is needed.

Use native labels, required controls, and inline role=alert error text. Keep
the layout compact and left-aligned with the existing workstation panels.

## Risks / Trade-offs

- [Only two fields exposed initially] → Keep the form honest and expand when
  the product has a concrete multi-period input workflow.
- [Evidence labels are opaque IDs] → Show source title and stance alongside
  the ID so the analyst can select a reviewable record.

## Migration Plan

No backend migration. Existing runs continue to render; the form appears only
when at least one qualified evidence record is available.

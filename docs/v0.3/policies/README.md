# MKG v0.3 — Policy Index (Semantic Freeze)

> **Status.** Authoritative semantic-policy set for v0.3, frozen prior to
> the first pilot rerun (Stewart Ch1).
>
> **Scope.** These documents codify decisions that are EXPENSIVE to revise
> after extraction begins: ID identity, vocabularies, granularity, edge
> semantics. The architectural specs in `docs/v0.3/00-..-13-*.md` describe
> the schema and pipeline; this directory describes the **policies** that
> govern how the schema is USED.
>
> **Precedence.** When a policy here conflicts with a non-policy doc,
> the policy wins. When a policy conflicts with `schema/v03.py` source,
> the schema wins (and the policy must be updated).

| # | Document | Topic |
|---|---|---|
| 01 | [`01-bundled-definitions-audit.md`](01-bundled-definitions-audit.md) | Audit of v0.2 bundled definitions; split plan for v0.3 |
| 02 | [`02-domain-vocabulary.md`](02-domain-vocabulary.md) | Controlled vocabulary for `domains.primary` / `domains.secondary` |
| 03 | [`03-ontology-vocabulary.md`](03-ontology-vocabulary.md) | Frozen `semantic_kind` set; keyword guidelines |
| 04 | [`04-edge-role-taxonomy.md`](04-edge-role-taxonomy.md) | Frozen edge role vocabularies (proof / concept / generality) |
| 05 | [`05-id-equivalence-policy.md`](05-id-equivalence-policy.md) | When two statements share a node; merge / split / redirect rules |
| 06 | [`06-theorem-granularity-policy.md`](06-theorem-granularity-policy.md) | Theorem parts, families, FTC-style decompositions |
| 07 | [`07-semantic-freeze.md`](07-semantic-freeze.md) | What is FROZEN, what is OPEN, change-control rules |
| 08 | [`08-pilot-readiness.md`](08-pilot-readiness.md) | Gap analysis + go / no-go for the Stewart Ch1 pilot |

## How to use these documents

- **Extraction agents** read 02–06 to apply controlled vocabularies and
  granularity rules; 05 is consulted on every new node that resembles an
  existing one.
- **Reviewers** read 01 + 06 to plan the v0.3 split-and-restructure work
  and 07 to know which conventions are settled.
- **Architects** read 07 to know what a "policy change" requires before
  committing it.
- **Pilot operators** start at 08, then loop into the rerun checklist
  (`docs/v0.3/13-rerun-checklist.md`).

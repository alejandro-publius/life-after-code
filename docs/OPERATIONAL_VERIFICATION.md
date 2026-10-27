# Verify the operational loop

This command runs the actual relay through authenticated `POST /tick` requests and a temporary `FileStore`.
It exercises the lease, state capture and restore, Watch decisions and morning countersign code. It does not
deploy anything or require credentials.

**Demo data:** GitLab responses, model notes, signatures, reactions, shop metrics, flag changes and phone
notifications are simulated adapters around the real decision code. No GitLab, Duo, Google Cloud, payment
service or person is contacted. An interrupted adapter response is an injected local failure, not an observed
production outage. This verifies the persisted error path, not an operating-system crash before state saving.

From the repository root:

```sh
uv sync --locked
uv run --locked python scripts/verify_night.py
uv run --locked python scripts/verify_night.py --format json --out /tmp/night-orders-operational.json
```

The default report is short Markdown. JSON includes every check and its outcome, HTTP response counts, the
decision ledger, external simulated action records, pre-action snapshots, persisted state and morning
signature evidence. Both reports identify the exact Git commit and a SHA-256 digest of the current source
and fixtures, including uncommitted verification changes. A failed expectation or exceeded budget exits with
a nonzero status. A smaller run can select `--case interrupted_action`; repeat `--case` to select several.

| Case | What the real relay must demonstrate |
| --- | --- |
| `signed_approved` | One necessary page, one human-approved fallback and one order whose recheck passes. The recorded model declines the first eligible order because its reason does not fit. Authority expires. |
| `unsigned` | Both incidents page the person; no external change occurs. |
| `missing_approval` | The suggested fallback stays unapplied without the person's approval. |
| `insufficient_traffic` | Error percentages on two checkouts per minute cannot authorize a change. Both incidents page with the traffic-floor reason. |
| `failed_recovery` | Standing orders act on matching numbers, but the whole service remains unhealthy. The subsequent recheck pages and never records recovery. |
| `interrupted_action` | A flag changes and its response is lost. The real relay records failure and the original snapshot in the file store, returns HTTP 500 and releases its lease. A newly constructed application and adapter load that state. The mutation is not repeated and an authorized morning restores the original values. |

Every case checks that a wrong HTTP key returns 401 without creating state, and that a competing FileStore
lease returns 409. The signed and interrupted cases reconstruct the application before the morning. They
read a wrong signer's merged file through the actual `GitLabSources` signature parser and verify refusal
without changes. The on-call person's signature is then read at its exact simulated commit. The real
countersign planner keeps the permitted checkout change or restores all changes from snapshots. Another
cold start and repeated morning tick must not repeat any restore.

The external simulated world retains its flags and action history across application reconstruction, like
an external service would. Adapter incident counters and pending reply times are restored from persisted
port state; the verification does not reuse a Watch instance between ticks. Existing test modules and global
environment mutation are not used.

Each case has at most 960 simulated minute steps, 972 HTTP requests and 30 seconds. The complete run has a
90-second budget, checked between requests. The usual in-memory browser replay keeps its existing 10-second
budget; operational verification explicitly selects the larger bounded allowance for HTTP and disk work.
No sleep or real-time overnight wait is required. Temporary state files are removed after evidence has been
copied into the report.

Regression checks:

```sh
uv run --locked pytest -q tests/test_operational.py
```

The command cannot prove live credential permissions, GitLab or Duo availability, a real phone delivery,
Cloud Storage behavior, or a production deployment. Those remain separate live gates.

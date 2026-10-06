# Judge guide

Start with [Night Orders in the browser](../README.md#try-one-night-in-the-browser). Sign the demo orders, approve the fallback, review the automatic checkout change and read the morning brief. Then replay without signing. The two paths make the human boundary visible.

This is a **local guided replay** with a simulated shop, planted faults and recorded model replies. The existing Watch code makes the decisions and writes the ledger. The controls choose isolated demo inputs. Live GitLab Duo execution, GitLab pipeline history and Google Cloud deployment are pending. See [Status](STATUS.md).

The [official rules](https://gitlab-transcend.devpost.com/rules) name five equally weighted criteria, so each has **20%** of the score before any cloud bonus. The primary-source extracts are in [Rules check](codex/RULES_CHECK.md#judging-stages-criteria-and-weights).

| Criterion | What to inspect | What the evidence establishes |
|---|---|---|
| Technological Implementation, 20% | [Watch](../relay/nightorders/watch.py), [decision checks](../relay/nightorders/decide.py), [browser replay](../relay/nightorders/browser_demo.py), [tests](../tests/), [Duo flows](../flows/) and [pipeline configuration](../.gitlab-ci.yml) | Working local decisions, guarded actions, bounded replay and validated flow definitions. A live Duo run and visible GitLab pipeline history remain required proof. |
| Design, 20% | The browser's Before bed, During the night and Over coffee chapters; unsigned and decline branches | A coherent human workflow from granting permission to reviewing its consequences. The default night needs one wake-up; an unsigned night grants no automatic authority. |
| Potential Impact, 20% | The on-call problem in the [README](../README.md), the wake-up messages and morning counts | A specific audience and a demonstrated mechanism for handling a pre-approved reversible fault. Counts are demo results, with no measured production or sleep benefit. |
| Innovation/Idea, 20% | [Order validation](../relay/nightorders/orders.py), [orders](../demo/night-2026-10-20/orders.yml), [morning countersign](../relay/nightorders/countersign.py) | A nightly signed, expiring grant with exact actions, and a separate morning decision about what stays. The model can decline an order and cannot widen its authority. |
| Presentation, 20% | [Local phone screenshot](images/demo-phone.png), [local laptop screenshot](images/demo-laptop.png), [video script](VIDEO.md) and [English Devpost draft](DEVPOST.md) | A readable demo and narrative that can be filmed now. The public YouTube link and public demo URL are pending. |

Path A is planned; Supervised is the tentative category recommendation. Required Duo Agent Platform use is a pass/fail gate. Google Cloud can add up to 0.2 points only with a demonstrated deployment, public live URL and deployment code in the public repository. A live deployment and cloud bonus are still pending. [Source](https://gitlab-transcend.devpost.com/rules).

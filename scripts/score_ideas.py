"""Combine the judges' and engineer's scores into one ranked table.

Usage: python3 scripts/score_ideas.py
Reads docs/research/ideas/scores_*.json and CANDIDATES.md, prints a markdown
table to stdout and writes docs/research/ideas/scores_combined.json.
The formula is in docs/research/ideas/SCORING_RUBRIC.md.
"""
import json
import re
from pathlib import Path
from statistics import mean

IDEAS = Path(__file__).resolve().parents[1] / "docs" / "research" / "ideas"
JUDGES = ["gitlab", "anthropic", "google"]
CRITERIA = ["tech", "design", "impact", "innovation", "presentation"]
EXTRAS = ["stages", "autonomy", "human", "novelty", "sponsors", "wow"]


def names():
    out = {}
    for line in (IDEAS / "CANDIDATES.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| (C\d\d) \| ([^|]+) \|", line)
        if m:
            out[m.group(1)] = m.group(2).strip()
    return out


def main():
    judges = {j: json.loads((IDEAS / f"scores_{j}_judge.json").read_text())["scores"] for j in JUDGES}
    eng = json.loads((IDEAS / "scores_engineer.json").read_text())["scores"]
    rows = []
    for cid, name in names().items():
        dims = {d: mean(judges[j][cid][d] for j in JUDGES) for d in CRITERIA + EXTRAS}
        criteria = mean(dims[d] for d in CRITERIA)
        feas = eng[cid]["feasibility"]
        total = 3 * criteria + sum(dims[d] for d in EXTRAS) + 2 * feas
        levels = [judges[j][cid].get("autonomy_level", "") for j in JUDGES]
        rows.append({
            "id": cid, "name": name, "criteria": round(criteria, 2),
            **{d: round(v, 1) for d, v in dims.items()},
            "feasibility": feas, "total": round(total, 1),
            "trap": eng[cid].get("trap", False), "trap_reason": eng[cid].get("trap_reason", ""),
            "levels": levels,
        })
    rows.sort(key=lambda r: r["total"], reverse=True)
    (IDEAS / "scores_combined.json").write_text(json.dumps(rows, indent=1) + "\n")
    head = "| Rank | ID | Name | Criteria (mean of 5) | Stages | Autonomy | Human | Novelty | Sponsors | Wow | Feasibility | Total /110 | Trap |"
    print(head)
    print("|" + "---|" * 13)
    for i, r in enumerate(rows, 1):
        trap = ("yes: " + r["trap_reason"]) if r["trap"] else ""
        print(f"| {i} | {r['id']} | {r['name']} | {r['criteria']} | {r['stages']} | {r['autonomy']} | {r['human']} | "
              f"{r['novelty']} | {r['sponsors']} | {r['wow']} | {r['feasibility']} | {r['total']} | {trap} |")


if __name__ == "__main__":
    main()

"""CLI demo for ReasonFork."""
from .core import run_all


def main():
    results = run_all()
    direct_score = sum(r["direct_correct"] for r in results)
    cot_score = sum(r["cot_correct"] for r in results)
    for r in results:
        print(f"\n[{r['id']}] {r['problem']}")
        print(f"  direct : {r['direct']}  -> correct={r['direct_correct']}")
        print(f"  CoT    : FINAL={r['cot_final']!r}  -> correct={r['cot_correct']}"
              f"{'  (CHANGED outcome)' if r['changed'] else ''}")
    print(f"\nTotals: direct {direct_score}/{len(results)}  |  chain-of-thought {cot_score}/{len(results)}")


if __name__ == "__main__":
    main()

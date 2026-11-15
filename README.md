# ReasonFork

A small, tested Python tool that runs six multi-step reasoning problems
through two deterministic, clearly-labeled stand-in functions — one
simulating a direct zero-shot answer, one simulating a "let's think step by
step" chain-of-thought answer — and compares their accuracy side by side.

**Disclosure:** neither `direct_answer` nor `chain_of_thought_answer` calls a
real LLM. Both are deterministic lookups built to be representative of what
an instruction-tuned model plausibly produces, including the specific,
well-known failure modes the direct prompts fall into (a rate-scaling trap,
an "all but N" misreading, a dropped delivery deadline). See the docstrings
in `reasonfork/core.py`.

## Usage

```bash
pip install -e .
python -m reasonfork.cli
```

## What it demonstrates

Across the six problems, direct prompting scores 3/6 and chain-of-thought
scores 6/6. The three problems where CoT changes the outcome share a pattern:
each has a salient, easy-to-reach wrong answer that drops a stated constraint
(a per-unit rate, a "survivors not deaths" phrasing, a delivery deadline).
Writing reasoning out loud surfaces the dropped constraint before the model
commits to an answer. The other three problems have no such trap, and direct
prompting already gets them right — a reminder that "this looks like a CoT
problem" is a heuristic, not a guarantee.

`extract_final()` demonstrates the `FINAL: <answer>` output-parsing pattern:
reasoning stays free-form, but the last line is grepped out with a simple
regex so downstream code never has to parse prose.

## Tests

```bash
pytest -v
```

13/13 passing.

## License

MIT

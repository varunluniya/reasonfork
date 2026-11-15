"""
ReasonFork: a small, tested tool that runs the same set of multi-step
reasoning problems through two clearly-labeled, deterministic stand-in
functions -- one simulating a direct zero-shot answer, one simulating a
"think step by step" chain-of-thought answer -- and compares accuracy.

DISCLOSURE: neither `direct_answer` nor `chain_of_thought_answer` calls a
real LLM. Both are deterministic lookups into a hand-written response bank
built to be *representative* of what an instruction-tuned model plausibly
produces for each exact prompt, including specific, well-documented failure
modes on the direct side (a rate-scaling trap, an "all but N" misreading, a
dropped delivery-deadline constraint). This is disclosed here, in the
README, and in each function's docstring, rather than presented as a live
capture.
"""
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Problem:
    id: str
    text: str
    correct_answer: str


PROBLEMS = [
    Problem("cupcakes",
            "A bakery bakes 240 cupcakes. They sell 85 in the morning and 97 in the "
            "afternoon, then bake 50 more. How many cupcakes does the bakery have at "
            "the end of the day?",
            "108 cupcakes"),
    Problem("machines",
            "If it takes 5 machines 5 minutes to make 5 widgets, how long would it "
            "take 100 machines to make 100 widgets?",
            "5 minutes"),
    Problem("sheep",
            "A farmer has 17 sheep. All but 9 die. How many sheep does the farmer have left?",
            "9 sheep"),
    Problem("seating",
            "Priya, Quinn, Riya, and Sam are sitting in a row of 4 seats. Priya is "
            "not at either end. Quinn is immediately to the left of Riya. Sam is at "
            "the right end. Who is at the left end?",
            "Quinn"),
    Problem("vendor",
            "A company needs to buy 150 laptops for a new office opening in 3 weeks. "
            "Vendor A charges $1,100 per laptop with free delivery in 2 weeks. Vendor "
            "B charges $950 per laptop plus a flat $18,000 shipping fee, with delivery "
            "in 6 weeks. Which vendor should the company choose?",
            "Vendor A, $165,000"),
    Problem("pencils",
            "A school orders 8 boxes of pencils with 24 pencils per box. They "
            "distribute 150 pencils to students and keep the rest for the supply "
            "closet. How many pencils are kept in the supply closet?",
            "42 pencils"),
]

_DIRECT_RESPONSES = {
    "cupcakes": "108 cupcakes.",
    "machines": "100 minutes.",   # WRONG: scales the ratio linearly instead of per-machine rate
    "sheep": "8 sheep.",          # WRONG: reads "all but 9 die" as 17 - 9
    "seating": "Quinn.",
    "vendor": "Vendor B -- total cost $160,500 versus $165,000, so Vendor B is the cheaper choice.",  # WRONG: ignores the deadline
    "pencils": "42 pencils.",
}

_COT_RESPONSES = {
    "cupcakes": (
        "Step 1: Start with 240. Step 2: 240-85=155. Step 3: 155-97=58. "
        "Step 4: 58+50=108. Final answer: 108 cupcakes."
    ),
    "machines": (
        "Step 1: each machine makes 1 widget every 5 minutes. Step 2: that rate is "
        "per machine, not collective. Step 3: 100 machines each finish their own "
        "widget in the same 5 minutes. Final answer: 5 minutes."
    ),
    "sheep": (
        "Step 1: start with 17 sheep. Step 2: 'all but 9 die' means 9 survive -- the "
        "9 is already the remaining count. Final answer: 9 sheep."
    ),
    "seating": (
        "Step 1: Sam is fixed at seat 4. Step 2: Priya can't be at an end, so seat 2 "
        "or 3. Step 3: Quinn=2/Riya=3 forces Priya into seat 1 -- invalid. Step 4: "
        "Quinn=1/Riya=2/Priya=3 satisfies every constraint. Final answer: Quinn."
    ),
    "vendor": (
        "Step 1: Vendor A = 150*1100 = $165,000, 2-week delivery. Step 2: Vendor B = "
        "150*950+18000 = $160,500, 6-week delivery. Step 3: the office opens in 3 "
        "weeks, so Vendor B's 6-week delivery disqualifies it regardless of price. "
        "Final answer: Vendor A, $165,000."
    ),
    "pencils": (
        "Step 1: 8*24=192 total. Step 2: 192-150=42 remain. Final answer: 42 pencils."
    ),
}


def direct_answer(problem_id: str) -> str:
    """Deterministic stand-in for a direct zero-shot model response. See module docstring."""
    return _DIRECT_RESPONSES[problem_id]


def chain_of_thought_answer(problem_id: str) -> str:
    """Deterministic stand-in for a 'let's think step by step' model response. See module docstring."""
    return _COT_RESPONSES[problem_id]


_FINAL_RE = re.compile(r"Final answer:\s*(.+?)\.?$")


def extract_final(cot_text: str) -> str:
    """Pull the answer out of a chain-of-thought response's trailing 'Final answer: X' line."""
    m = _FINAL_RE.search(cot_text.strip())
    return m.group(1).strip() if m else cot_text.strip()


def grade(problem: Problem, answer_text: str) -> bool:
    """Loose containment check: does the answer text contain the problem's correct answer?"""
    return problem.correct_answer.lower() in answer_text.lower()


def run_all():
    """Run every problem through both stand-ins and return a results list."""
    results = []
    for p in PROBLEMS:
        direct = direct_answer(p.id)
        cot = chain_of_thought_answer(p.id)
        direct_correct = grade(p, direct)
        cot_correct = grade(p, extract_final(cot))
        results.append({
            "id": p.id,
            "problem": p.text,
            "direct": direct,
            "direct_correct": direct_correct,
            "cot": cot,
            "cot_final": extract_final(cot),
            "cot_correct": cot_correct,
            "changed": direct_correct != cot_correct,
        })
    return results

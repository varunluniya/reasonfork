import pytest
from reasonfork.core import PROBLEMS, direct_answer, chain_of_thought_answer, extract_final, grade, run_all


def test_six_problems_defined():
    assert len(PROBLEMS) == 6


def test_extract_final_pulls_answer_out_of_cot_text():
    text = "Step 1: blah. Step 2: blah. Final answer: 5 minutes."
    assert extract_final(text) == "5 minutes"


def test_extract_final_falls_back_to_whole_text_if_no_tag():
    text = "no final tag here"
    assert extract_final(text) == text


@pytest.mark.parametrize("pid,expected_correct", [
    ("cupcakes", True),
    ("machines", False),
    ("sheep", False),
    ("seating", True),
    ("vendor", False),
    ("pencils", True),
])
def test_direct_answer_known_mismatches(pid, expected_correct):
    problem = next(p for p in PROBLEMS if p.id == pid)
    assert grade(problem, direct_answer(pid)) == expected_correct


def test_cot_answer_correct_on_all_six():
    for p in PROBLEMS:
        cot = chain_of_thought_answer(p.id)
        assert grade(p, extract_final(cot)) is True


def test_overall_accuracy_split_matches_writeup():
    results = run_all()
    direct_score = sum(r["direct_correct"] for r in results)
    cot_score = sum(r["cot_correct"] for r in results)
    assert direct_score == 3
    assert cot_score == 6


def test_three_problems_change_outcome():
    results = run_all()
    changed = [r["id"] for r in results if r["changed"]]
    assert set(changed) == {"machines", "sheep", "vendor"}


def test_machines_extract_final_matches_expected():
    cot = chain_of_thought_answer("machines")
    assert extract_final(cot) == "5 minutes"

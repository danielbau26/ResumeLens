"""Tests for Stage 3 — qualification pattern recognition (finite automata)."""
 
from __future__ import annotations
 
import json
from pathlib import Path
 
import pytest
 
from resumelens.extraction import extract_from_file, get_skills
from resumelens.normalization import PROFILE_ORDER, normalize
from resumelens.recognition import (
    PROFILES,
    accepted_profiles,
    accepts,
    automaton_type,
    formal_definition,
    recognize,
    save_result,
)
 
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "sample_resumes"
 
 
def results_for(skills):
    """Runs stages 2 and 3 over a list of surface skills."""
    return recognize(normalize(skills)["by_profile"])
 
 
def test_assignment_example_is_accepted_as_machine_learning():
    """PYTHON, PANDAS, TENSORFLOW, POSTGRESQL, GIT -> MACHINE_LEARNING ACCEPTED."""
    sequence = ["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"]
    assert accepts("machine_learning", sequence)
 
 
def test_wednesday_is_full_stack_only():
    data = extract_from_file(DATA_DIR / "wednesday_addams.txt")
    results = recognize(normalize(get_skills(data))["by_profile"])
    assert accepted_profiles(results) == ["full_stack"]
    assert results["full_stack"]["result"] == "ACCEPTED"
    assert results["machine_learning"]["result"] == "REJECTED"
 
 
def test_mary_jane_is_machine_learning_only():
    data = extract_from_file(DATA_DIR / "mary_jane_watson.txt")
    results = recognize(normalize(get_skills(data))["by_profile"])
    assert accepted_profiles(results) == ["machine_learning"]
 
 
def test_several_symbols_of_the_same_group_are_accepted():
    """PANDAS and NUMPY together: the loop on the group state accepts both."""
    sequence = ["PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT"]
    assert accepts("machine_learning", sequence)
 
 
def test_missing_required_group_is_rejected():
    """A Full Stack résumé without a backend technology is rejected."""
    results = results_for(["JS", "React.js", "Postgres", "Git"])
    assert results["full_stack"]["result"] == "REJECTED"
 
 
def test_wrong_order_is_rejected():
    """The automaton reads in order: GIT first does not match the pattern."""
    sequence = ["GIT", "PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL"]
    assert not accepts("machine_learning", sequence)
 
 
def test_empty_sequence_is_rejected_by_every_profile():
    for profile_key in PROFILES:
        assert not accepts(profile_key, [])
 
 
def test_extras_after_the_final_state_are_accepted():
    """Docker and REST APIs after Git keep the Full Stack automaton in the final state."""
    results = results_for(["JS", "React.js", "NodeJS", "Postgres", "Git", "Docker", "REST APIs"])
    assert results["full_stack"]["result"] == "ACCEPTED"
 
 
def test_ai_engineer_without_database_is_accepted():
    """The database group is optional in AI Engineer (ε-transition)."""
    results = results_for(["Python", "Pandas", "PyTorch", "Hugging Face", "Docker", "Git"])
    assert results["ai_engineer"]["result"] == "ACCEPTED"
 
 
def test_ai_engineer_requires_big_data_or_genai():
    """Without Spark or Hugging Face the AI Engineer pattern is not satisfied."""
    results = results_for(["Python", "Pandas", "PyTorch", "Postgres", "Docker", "Git"])
    assert results["ai_engineer"]["result"] == "REJECTED"
 
 
def test_ai_engineer_full_example():
    results = results_for(
        ["Git", "Python", "PyTorch", "Pandas", "Hugging Face", "PySpark", "Postgres", "Docker", "AWS"],
    )
    assert results["ai_engineer"]["result"] == "ACCEPTED"
 
 
def test_cloud_engineer_full_example():
    results = results_for(
        ["Git", "Terraform", "Docker", "AWS", "Kubernetes", "Helm", "Jenkins", "Linux", "Azure"],
    )
    assert results["cloud_engineer"]["result"] == "ACCEPTED"
 
 
def test_cloud_engineer_without_optional_groups_is_accepted():
    """CI/CD and database are optional in Cloud Engineer (ε-transitions)."""
    results = results_for(["AWS", "Docker", "Terraform", "Linux", "Git"])
    assert results["cloud_engineer"]["result"] == "ACCEPTED"
 
 
def test_missing_profile_in_input_is_rejected():
    results = recognize({"full_stack": ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]})
    assert results["full_stack"]["result"] == "ACCEPTED"
    assert results["cloud_engineer"]["result"] == "REJECTED"
    assert results["cloud_engineer"]["sequence"] == []
 
 
@pytest.mark.parametrize(
    "profile_key, expected_type",
    [
        ("full_stack", "DFA"),
        ("machine_learning", "DFA"),
        ("ai_engineer", "ε-NFA"),
        ("cloud_engineer", "ε-NFA"),
    ],
)
def test_automaton_type(profile_key, expected_type):
    assert automaton_type(profile_key) == expected_type
 
 
def test_formal_definition_5_tuple():
    fd = formal_definition("machine_learning")
    assert fd["Q"] == ["q0", "q1", "q2", "q3", "q4", "q5"]
    assert fd["q0"] == "q0"
    assert fd["F"] == ["q5"]
    assert "PYTHON" in fd["Σ"]
    assert fd["δ"]
    assert fd["type"] == "DFA"
    assert fd["justification"]
 
 
def test_profiles_match_stage_2_order():
    """Each automaton uses exactly the symbols of its Stage 2 order, in the same order."""
    for profile_key, profile in PROFILES.items():
        symbols = []
        for group in profile["groups"]:
            symbols.extend(group["symbols"])
        symbols.extend(profile["extras"])
        assert symbols == PROFILE_ORDER[profile_key]
 
 
def test_save_result_roundtrip(tmp_path: Path):
    results = results_for(["JS", "React.js", "NodeJS", "Postgres", "Git"])
    out = tmp_path / "recognition.json"
    save_result(results, out)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["full_stack"]["result"] == "ACCEPTED"
    assert loaded["full_stack"]["profile"] == "Full Stack Developer"
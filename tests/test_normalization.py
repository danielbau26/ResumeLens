"""Tests for Stage 2 — qualification normalization (finite-state transducers)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from resumelens.extraction import extract_from_file
from resumelens.normalization import (
    build_transducer,
    combined_transducer,
    normalize,
    normalize_extraction,
    normalize_token,
    save_result,
    sort_qualifications,
)
from resumelens.normalization.transformations import RULES, rule_for_canonical


@pytest.mark.parametrize(
    "surface, canonical",
    [
        ("JS", "JAVASCRIPT"),
        ("Javascript", "JAVASCRIPT"),
        ("JavaScript", "JAVASCRIPT"),
        ("React.js", "REACT"),
        ("ReactJS", "REACT"),
        ("NodeJS", "NODE_JS"),
        ("Node.js", "NODE_JS"),
        ("Postgres", "POSTGRESQL"),
        ("PostgreSQL", "POSTGRESQL"),
        ("pandas", "PANDAS"),
        ("sklearn", "SCIKIT_LEARN"),
        ("scikit learn", "SCIKIT_LEARN"),
        ("Scikit-learn", "SCIKIT_LEARN"),
        ("Tensor Flow", "TENSORFLOW"),
        ("TensorFlow", "TENSORFLOW"),
        ("Py Torch", "PYTORCH"),
        ("PyTorch", "PYTORCH"),
        ("Git", "GIT"),
        ("SQL", "SQL"),
        ("K8s", "KUBERNETES"),
        ("PySpark", "SPARK"),
        ("Apache Spark", "SPARK"),
        ("Hugging Face", "HUGGING_FACE"),
        ("Helm", "HELM"),
    ],
)
def test_transducer_maps_variant_to_canonical(surface, canonical):
    assert normalize_token(surface) == canonical


def test_all_declared_variants_transduce_to_their_canonical():
    """Every variant in the catalogue must transduce to its canonical form."""
    for rule in RULES:
        for variant in rule.variants:
            assert normalize_token(variant) == rule.canonical


def test_unknown_token_is_not_recognized():
    assert normalize_token("COBOL") is None


def test_matching_is_case_insensitive():
    assert normalize_token("javascript") == "JAVASCRIPT"
    assert normalize_token("POSTGRES") == "POSTGRESQL"


def test_canonical_example_from_statement():
    """Git, NodeJS, JS, Postgres, React.js -> JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT."""
    result = normalize(["Git", "NodeJS", "JS", "Postgres", "React.js"], profile="full_stack")
    assert result.canonical == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    assert result.unrecognized == []


def test_output_is_independent_of_input_order():
    """Any permutation of the same résumé yields the same sorted output."""
    a = normalize(["Git", "NodeJS", "JS", "Postgres", "React.js"], profile="full_stack")
    b = normalize(["React.js", "Git", "Postgres", "JS", "NodeJS"], profile="full_stack")
    assert a.canonical == b.canonical


def test_deduplication_of_equivalent_variants():
    """JS and JavaScript collapse to a single JAVASCRIPT."""
    result = normalize(["JS", "JavaScript", "Javascript"], profile="full_stack")
    assert result.canonical == ["JAVASCRIPT"]


def test_unrecognized_tokens_are_kept_not_dropped():
    result = normalize(["JS", "COBOL", "Git"], profile="full_stack")
    assert result.canonical == ["JAVASCRIPT", "GIT"]
    assert result.unrecognized == ["COBOL"]


def test_unordered_canonical_appended_at_end():
    """A canonical form not in the profile order is appended last."""
    # RUBY is a valid canonical but not part of the full_stack order.
    result = normalize(["JS", "Ruby", "Git"], profile="full_stack")
    assert result.canonical == ["JAVASCRIPT", "GIT", "RUBY"]


def test_sort_requires_known_profile():
    with pytest.raises(KeyError):
        sort_qualifications(["JAVASCRIPT"], "unknown_profile")


def test_ml_sample_end_to_end():
    """Mary Jane Watson résumé normalizes to the ML canonical sequence."""
    data_dir = Path(__file__).resolve().parents[1] / "data" / "sample_resumes"
    extraction = extract_from_file(data_dir / "mary_jane_watson.txt")
    result = normalize_extraction(extraction, profile="machine_learning")
    assert result.canonical == [
        "PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT",
    ]


def test_all_four_profiles_are_available():
    from resumelens.normalization import available_profiles

    assert available_profiles() == [
        "full_stack", "machine_learning", "ai_engineer", "cloud_engineer",
    ]


def test_ai_engineer_profile_ordering():
    """AI Engineer sorts language -> data -> ML/DL -> big data/GenAI -> db -> tools."""
    result = normalize(
        ["Git", "Python", "PyTorch", "Pandas", "Hugging Face", "PySpark", "Postgres", "Docker", "AWS"],
        profile="ai_engineer",
    )
    assert result.canonical == [
        "PYTHON", "PANDAS", "PYTORCH", "SPARK", "HUGGING_FACE",
        "POSTGRESQL", "DOCKER", "AWS", "GIT",
    ]


def test_cloud_engineer_profile_ordering():
    """Cloud Engineer sorts platforms -> containers -> IaC -> CI/CD -> OS -> db -> vcs."""
    result = normalize(
        ["Git", "Terraform", "Docker", "AWS", "Kubernetes", "Helm", "Jenkins", "Linux", "Azure"],
        profile="cloud_engineer",
    )
    assert result.canonical == [
        "AWS", "AZURE", "DOCKER", "KUBERNETES", "HELM",
        "TERRAFORM", "JENKINS", "LINUX", "GIT",
    ]


def test_combined_transducer_translates_a_variant():
    fst = combined_transducer()
    assert list(fst.translate(list("js"))) == [["JAVASCRIPT"]]


def test_transducer_is_a_valid_fst_tuple():
    """A per-rule FST exposes the 7-tuple components expected by the report."""
    fst = build_transducer(rule_for_canonical("SCIKIT_LEARN"))
    assert fst.start_states == {"q0"}
    assert fst.final_states == {"qf"}
    assert set(fst.output_symbols) == {"SCIKIT_LEARN"}
    assert len(fst.states) > 2  # character-level: several intermediate states


def test_save_result_roundtrip(tmp_path: Path):
    result = normalize(["JS", "Git"], profile="full_stack")
    out = save_result(result, tmp_path / "norm.json")
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["canonical"] == ["JAVASCRIPT", "GIT"]
    assert loaded["profile"] == "full_stack"
    assert loaded["mapping"][0] == ["JS", "JAVASCRIPT"]

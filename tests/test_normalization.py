"""Tests for Stage 2 — qualification normalization (finite-state transducers)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from resumelens.extraction import extract_from_file, get_skills
from resumelens.normalization import (
    PROFILE_ORDER,
    build_transducer,
    formal_definition,
    normalize,
    save_result,
    sort_skills,
    translate,
)
from resumelens.normalization.transformations import VARIANTS


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
        ("Hugging Face", "HUGGING_FACE"),
        ("Helm", "HELM"),
    ],
)
def test_translate_maps_variant_to_canonical(surface, canonical):
    assert translate(surface) == canonical


def test_all_declared_variants_translate_to_their_canonical():
    """Every variant in the catalogue must translate to its canonical form."""
    for canonical, variants in VARIANTS.items():
        for variant in variants:
            assert translate(variant) == canonical


def test_unknown_token_is_not_recognized():
    assert translate("COBOL") is None


def test_matching_is_case_insensitive():
    assert translate("javascript") == "JAVASCRIPT"
    assert translate("POSTGRES") == "POSTGRESQL"


def test_canonical_example_from_statement():
    """Git, NodeJS, JS, Postgres, React.js -> (full_stack) JAVASCRIPT, REACT, NODE_JS, POSTGRESQL, GIT."""
    result = normalize(["Git", "NodeJS", "JS", "Postgres", "React.js"])
    assert result["by_profile"]["full_stack"] == [
        "JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT",
    ]
    assert result["unrecognized"] == []


def test_output_is_independent_of_input_order():
    """Any permutation of the same résumé yields the same per-profile output."""
    a = normalize(["Git", "NodeJS", "JS", "Postgres", "React.js"])
    b = normalize(["React.js", "Git", "Postgres", "JS", "NodeJS"])
    assert a["by_profile"] == b["by_profile"]


def test_deduplication_of_equivalent_variants():
    """JS and JavaScript collapse to a single JAVASCRIPT."""
    result = normalize(["JS", "JavaScript", "Javascript"])
    assert result["canonical"] == ["JAVASCRIPT"]


def test_unrecognized_tokens_are_kept_not_dropped():
    result = normalize(["JS", "COBOL", "Git"])
    assert result["canonical"] == ["JAVASCRIPT", "GIT"]
    assert result["unrecognized"] == ["COBOL"]


def test_skill_not_in_profile_is_dropped():
    """A canonical form not in the profile order is not sent to that profile."""
    # RUBY is a valid canonical but not part of the full_stack order.
    result = normalize(["JS", "Ruby", "Git"])
    assert "RUBY" in result["canonical"]
    assert result["by_profile"]["full_stack"] == ["JAVASCRIPT", "GIT"]


def test_sort_requires_known_profile():
    with pytest.raises(KeyError):
        sort_skills(["JAVASCRIPT"], "unknown_profile")


def test_ml_sample_end_to_end():
    """Mary Jane Watson résumé normalizes to the ML canonical sequence."""
    data_dir = Path(__file__).resolve().parents[1] / "data" / "sample_resumes"
    data = extract_from_file(data_dir / "mary_jane_watson.txt")
    result = normalize(get_skills(data))
    assert result["by_profile"]["machine_learning"] == [
        "PYTHON", "PANDAS", "NUMPY", "SCIKIT_LEARN", "TENSORFLOW", "SQL", "GIT",
    ]


def test_all_four_profiles_are_available():
    assert list(PROFILE_ORDER) == [
        "full_stack", "machine_learning", "ai_engineer", "cloud_engineer",
    ]


def test_ai_engineer_profile_ordering():
    """AI Engineer sorts language -> data -> ML/DL -> big data/GenAI -> db -> tools."""
    result = normalize(
        ["Git", "Python", "PyTorch", "Pandas", "Hugging Face", "PySpark", "Postgres", "Docker", "AWS"],
    )
    assert result["by_profile"]["ai_engineer"] == [
        "PYTHON", "PANDAS", "PYTORCH", "SPARK", "HUGGING_FACE",
        "POSTGRESQL", "DOCKER", "AWS", "GIT",
    ]


def test_cloud_engineer_profile_ordering():
    """Cloud Engineer sorts platforms -> containers -> IaC -> CI/CD -> OS -> db -> vcs."""
    result = normalize(
        ["Git", "Terraform", "Docker", "AWS", "Kubernetes", "Helm", "Jenkins", "Linux", "Azure"],
    )
    assert result["by_profile"]["cloud_engineer"] == [
        "AWS", "AZURE", "DOCKER", "KUBERNETES", "HELM",
        "TERRAFORM", "JENKINS", "LINUX", "GIT",
    ]


def test_build_transducer_is_a_valid_fst():
    fst = build_transducer("SCIKIT_LEARN")
    assert fst.start_states == {"q0"}
    assert fst.final_states          # at least one accepting state
    # the canonical form is among the output symbols (ε/"" is the other one)
    assert "SCIKIT_LEARN" in {str(s) for s in fst.output_symbols}


def test_formal_definition_7_tuple():
    """formal_definition returns the complete 7-tuple for a transducer."""
    fd = formal_definition("JAVASCRIPT")
    assert fd["q0"] == "q0"
    assert fd["Γ"] == ["JAVASCRIPT"]
    assert fd["F"]                   # non-empty set of accepting states
    assert len(fd["Q"]) > 2          # character-level: several intermediate states
    assert fd["δ"] and fd["ω"]       # transition and output relations listed


def test_save_result_roundtrip(tmp_path: Path):
    result = normalize(["JS", "Git"])
    out = tmp_path / "norm.json"
    save_result(result, out)
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["canonical"] == ["JAVASCRIPT", "GIT"]
    assert loaded["translations"]["JS"] == "JAVASCRIPT"
    assert loaded["by_profile"]["full_stack"] == ["JAVASCRIPT", "GIT"]

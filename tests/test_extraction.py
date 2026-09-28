"""Tests for Stage 1 — information extraction (regular expressions)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from resumelens.extraction import extract, extract_file, save_result

# The canonical example from the assignment statement.
WEDNESDAY = (
    "Wednesday Addams\n"
    "3 years of experience developing web applications.\n"
    "Technical Skills:\n"
    "JS, React.js, NodeJS, Postgres, Git.\n"
)


def test_extracts_assignment_example_qualifications():
    """The Wednesday Addams fragment yields JS, React.js, NodeJS, Postgres, Git."""
    result = extract(WEDNESDAY)
    assert result.qualifications() == ["JS", "React.js", "NodeJS", "Postgres", "Git"]


def test_programming_languages_variants():
    result = extract("Skills: JavaScript, Javascript, JS, TypeScript, Python")
    langs = result.get("programming_languages")
    assert "JavaScript" in langs
    assert "JS" in langs
    assert "TypeScript" in langs
    assert "Python" in langs


def test_framework_dotted_tokens_not_split():
    """React.js and Node.js must be captured whole, not as 'React' + '.js'."""
    result = extract("React.js and Node.js and Scikit-learn")
    frameworks = result.get("frameworks_libraries")
    assert "React.js" in frameworks
    assert "Node.js" in frameworks
    assert "Scikit-learn" in frameworks


def test_dotted_token_not_matched_as_url():
    """The URL pattern must not treat 'React.js' as a web address."""
    result = extract("React.js")
    assert result.get("url") == []


def test_contact_information():
    text = "john.doe@example.com | +1 212 555 0142 | github.com/jdoe"
    result = extract(text)
    assert result.get("email") == ["john.doe@example.com"]
    assert result.get("url") == ["github.com/jdoe"]
    assert result.get("phone")  # a phone number was detected


def test_url_host_not_reclaimed_as_tool():
    """'github' inside a github.com URL must not also appear as a tool."""
    result = extract("Profile: github.com/jdoe. Version control: Git.")
    assert result.get("url") == ["github.com/jdoe"]
    assert result.get("tools_technologies") == ["Git"]


def test_experience_and_academic():
    text = "5 years of experience in backend development. MSc in Computer Science."
    result = extract(text)
    assert result.get("professional_experience")
    assert result.get("professional_experience")[0].lower().startswith("5 years of experience")
    assert any("Computer Science" in deg for deg in result.get("academic_qualifications"))


def test_deduplication_is_case_insensitive_and_order_preserving():
    result = extract("Git, git, GIT, Docker, git")
    assert result.get("tools_technologies") == ["Git", "Docker"]


def test_databases_variants():
    result = extract("Postgres, PostgreSQL, MongoDB, NoSQL, SQL")
    dbs = result.get("databases")
    assert "Postgres" in dbs
    assert "MongoDB" in dbs
    assert "SQL" in dbs


def test_empty_text_yields_no_matches():
    assert extract("").matches == {}


def test_extract_file_and_save_roundtrip(tmp_path: Path):
    resume = tmp_path / "resume.txt"
    resume.write_text(WEDNESDAY, encoding="utf-8")

    result = extract_file(resume)
    out = save_result(result, tmp_path / "out.json")

    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["programming_languages"] == ["JS"]
    assert loaded["frameworks_libraries"] == ["React.js", "NodeJS"]


def test_sample_resume_files_present():
    """The repository ships the two assignment sample résumés."""
    data_dir = Path(__file__).resolve().parents[1] / "data" / "sample_resumes"
    assert (data_dir / "wednesday_addams.txt").exists()
    assert (data_dir / "mary_jane_watson.txt").exists()

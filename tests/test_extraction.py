"""Tests for Stage 1 — information extraction (regular expressions)."""

from __future__ import annotations

import json
from pathlib import Path

from resumelens.extraction import (
    extract_info,
    extract_from_file,
    get_skills,
    save_result,
)

# The canonical example from the assignment statement.
WEDNESDAY = (
    "Wednesday Addams\n"
    "3 years of experience developing web applications.\n"
    "Technical Skills:\n"
    "JS, React.js, NodeJS, Postgres, Git.\n"
)


def test_extracts_assignment_example_qualifications():
    """The Wednesday Addams fragment yields JS, React.js, NodeJS, Postgres, Git."""
    data = extract_info(WEDNESDAY)
    assert get_skills(data) == ["JS", "React.js", "NodeJS", "Postgres", "Git"]


def test_name_is_first_non_empty_line():
    assert extract_info(WEDNESDAY)["name"] == "Wednesday Addams"


def test_programming_languages_variants():
    data = extract_info("Skills: JavaScript, JS, TypeScript, Python")
    langs = data["programming_languages"]
    assert "JavaScript" in langs
    assert "JS" in langs
    assert "TypeScript" in langs
    assert "Python" in langs


def test_framework_dotted_tokens_not_split():
    """React.js and Node.js must be captured whole, not as 'React' + '.js'."""
    data = extract_info("React.js and Node.js and Scikit-learn")
    frameworks = data["frameworks_libraries"]
    assert "React.js" in frameworks
    assert "Node.js" in frameworks
    assert "Scikit-learn" in frameworks


def test_dotted_token_not_matched_as_url():
    """The URL pattern must not treat 'React.js' as a web address."""
    assert extract_info("React.js")["urls"] == []


def test_contact_information():
    text = "john.doe@example.com | +1 212 555 0142 | github.com/jdoe"
    data = extract_info(text)
    assert data["emails"] == ["john.doe@example.com"]
    assert data["urls"] == ["github.com/jdoe"]
    assert data["phones"]  # a phone number was detected


def test_url_host_not_reclaimed_as_tool():
    """'github' inside a github.com URL must not also appear as a tool."""
    data = extract_info("Profile: github.com/jdoe. Version control: Git.")
    assert data["urls"] == ["github.com/jdoe"]
    assert data["tools_technologies"] == ["Git"]


def test_experience_and_academic():
    text = "5 years of experience in backend development. MSc in Computer Science."
    data = extract_info(text)
    assert data["professional_experience"]
    assert data["professional_experience"][0].lower().startswith("5 years of experience")
    assert any("Computer Science" in deg for deg in data["academic_qualifications"])


def test_other_qualifications():
    data = extract_info("Experience in machine learning and data processing pipelines.")
    other = data["other_qualifications"]
    assert any("machine" in o.lower() for o in other)
    assert any("data" in o.lower() for o in other)


def test_deduplication_is_case_insensitive_and_order_preserving():
    data = extract_info("Git, git, GIT, Docker, git")
    assert data["tools_technologies"] == ["Git", "Docker"]


def test_databases_variants():
    data = extract_info("Postgres, PostgreSQL, MongoDB, NoSQL, SQL")
    dbs = data["databases"]
    assert "Postgres" in dbs
    assert "MongoDB" in dbs
    assert "SQL" in dbs


def test_empty_text_yields_no_skills():
    data = extract_info("")
    assert data["name"] == ""
    assert get_skills(data) == []


def test_extract_from_file_and_save_roundtrip(tmp_path: Path):
    resume = tmp_path / "resume.txt"
    resume.write_text(WEDNESDAY, encoding="utf-8")

    data = extract_from_file(resume)
    out = tmp_path / "out.json"
    save_result(data, out)

    assert out.exists()
    loaded = json.loads(out.read_text(encoding="utf-8"))
    assert loaded["programming_languages"] == ["JS"]
    assert loaded["frameworks_libraries"] == ["React.js", "NodeJS"]


def test_sample_resume_files_present():
    """The repository ships the two assignment sample résumés."""
    data_dir = Path(__file__).resolve().parents[1] / "data" / "sample_resumes"
    assert (data_dir / "wednesday_addams.txt").exists()
    assert (data_dir / "mary_jane_watson.txt").exists()

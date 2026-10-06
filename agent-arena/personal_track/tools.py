"""Tools for your personal portfolio agent (personal track).

The agent answers recruiter-style questions about you, using about_me.md.
"""

import os
from strands import tool

HERE = os.path.dirname(__file__)


def load_profile():
    """Split about_me.md (or the template if you haven't made one yet) into {section: text}."""
    path = os.path.join(HERE, "about_me.md")
    if not os.path.exists(path):
        path = os.path.join(HERE, "about_me_TEMPLATE.md")
    text = open(path, encoding="utf-8").read()
    sections = {}
    for chunk in text.split("\n## ")[1:]:
        title, _, body = chunk.partition("\n")
        sections[title.strip().lower()] = body.strip()
    return sections


@tool
def read_profile(section: str) -> str:
    """Read one section of the student's profile.

    Args:
        section: One of summary, skills, projects, experience, involvement, contact, private notes
    """
    sections = load_profile()
    body = sections.get(section.lower().strip())
    if body is None:
        return "Unknown section. Available: " + ", ".join(sections)
    return body


@tool
def match_job(job_description: str) -> str:
    """Compare the student's skills to a job description and list matches and gaps.

    Args:
        job_description: The job posting text or a list of required skills
    """
    skills_text = load_profile().get("skills", "")
    skills = []
    for skill in skills_text.replace("(", ",").replace(")", ",").split(","):
        if skill.strip():
            skills.append(skill.strip())
    matches = []
    for skill in skills:
        if skill.lower() in job_description.lower():
            matches.append(skill)
    return f"Matching skills: {', '.join(matches) or 'none found'}. Total listed skills: {len(skills)}."

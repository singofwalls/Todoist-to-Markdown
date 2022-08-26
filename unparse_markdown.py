"""
Unparse the Todoist dictionary produced with `parse_todoist.py` into Markdown files.
"""
from utility import Project


def unparse_project(project: Project) -> str:
    """Produce a str to write to a Markdown file from a single Project."""

    

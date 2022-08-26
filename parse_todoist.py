"""
Parse a Todoist JSON dump into an Obsidian-compatible Markdown format.

Obtain the JSON from here: https://darekkay.com/todoist-export/
    Export for Todoist by Darek Kay


Author: Reece Mathews
"""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict
from utility import Item, Note, Project, Section
from unparse_markdown import unparse_project


def parse_notes(todoist: dict, ids: Dict[str, Any]) -> None:
    """Parse notes into their corresponding projects and items in-place."""

    for note in todoist["notes"] + todoist["project_notes"]:
        if note["is_deleted"]:
            continue

        if "item_id" in note:
            if note["item_id"] not in ids:
                print(f"Item {note['item_id']} not found for note {note['content']}")
                continue
            parent = ids[note["item_id"]]

        else:
            if note["project_id"] not in ids:
                print(f"Project {note['project_id']} not found for note {note['content']}")
                continue
            parent = ids[note["project_id"]]

        note_obj = Note(note["content"])

        attachment = note["file_attachment"]
        if attachment is not None:
            if attachment["resource_type"] == "image":
                note_obj.attachment = {"image": attachment["image"]}
            else:
                # Handle as URL
                note_obj.attachment = {"title": attachment["title"], "url": attachment["url"]}

        parent.notes.append(note_obj)
        ids[note["id"]] = note_obj



def parse_items(todoist: dict, ids: Dict[str, Any]) -> None:
    """Parse items into their corresponding projects in-place."""
    to_process = []

    for item in todoist["items"]:
        if item["is_deleted"]:
            continue

        item_obj = Item(item["content"], item["checked"],
                        item["description"], item["date_added"])

        for label in item["labels"]:
            if label not in ids:
                print(f"Label {label} not found for item {item['name']}")
                continue
            item_obj.labels.append(ids[label])

        parent_found = False
        if item["parent_id"] is not None:
            # Child of another item
            if item["parent_id"] not in ids:
                to_process.append(item)
                continue

            parent = ids[item["parent_id"]]
            parent.items.append(item_obj)
            parent_found = True

        elif item["section_id"] is not None:
            # Child of a section
            if item["section_id"] not in ids:
                print(f"Section {item['section_id']} not found for item {item['name']}")

            else:
                section = ids[item["section_id"]]
                section.items.append(item_obj)
                parent_found = True

        if item["project_id"] is not None and not parent_found:
            # Child of a project
            if item["project_id"] not in ids:
                print(f"Project {item['project_id']} not found for item {item['name']}")
                continue

            project = ids[item["project_id"]]
            project.items.append(item_obj)

        # Successfully placed item
        ids[item["id"]] = item_obj

    if to_process:
        print(f"Performing second iteration to find item parents of {len(to_process)} items")
        parse_items({"items": to_process}, ids)


def parse_labels(todoist: dict, ids: Dict[str, Any]) -> None:
    """Parse label definitions into the IDs dict in-place."""
    for label in todoist["labels"]:
        if label["is_deleted"]:
            continue

        ids[label["id"]] = label["name"]


def parse_sections(todoist: dict, ids: Dict[str, Any]) -> None:
    """Parse sections into each corresponding project in-place."""
    for section in todoist["sections"]:
        if section["is_deleted"]:
            continue

        project_id = section["project_id"]
        if project_id not in ids:
            print(f"Project {project_id} not found for section {section['name']}")
            continue

        project = ids[project_id]
        section_obj = Section(section["name"])
        ids[section["id"]] = section_obj
        project.sections[section["id"]] = section_obj


def parse_projects(todoist: dict, ids: Dict[str, Any]) -> Dict[str, Project]:
    """Parse projects into a list of Projects."""
    projects: Dict[str, Project] = {}

    for project in todoist["projects"]:
        if project["is_deleted"]:
            continue

        project_obj = Project(project["name"])
        ids[project["id"]] = project_obj
        projects[project["id"]] = project_obj

    return projects


def parse_todoist(todoist: dict):
    """Parse a JSON dump from Todoist into Markdown for Obsidian."""
    ids = {}
    projects = parse_projects(todoist, ids)
    parse_sections(todoist, ids)
    parse_labels(todoist, ids)
    parse_items(todoist, ids)
    parse_notes(todoist, ids)

    os.makedirs("markdown", exist_ok=True)

    for project_name, project in projects.items():
        with open(Path("markdown") / project_name, "w") as f:
            f.write(unparse_project(project))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse a todoist JSON into Markdown.")
    parser.add_argument("file", type=argparse.FileType("r"))
    args = parser.parse_args()

    parse_todoist(json.load(args.file))

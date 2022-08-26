
from datetime import datetime
from distutils.command.build_scripts import first_line_re
from typing import Dict, List, Optional, Tuple
from textwrap import indent


ADD_DATE = False
JSON_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
MARKDOWN_DATE_FORMAT = '%m/%d/%Y %I:%M %p'


INDENT_CHAR = "\t"


class Note:
    def __init__(self, content):
        self.content: str = content
        self.attachment: Optional[Dict[str, str]] = None

    def __repr__(self) -> str:
        return f"Note['{self.content}', {self.attachment}]"

    def unparse(self) -> str:
        content = self.content.split("\n")
        content = "\n".join(line.strip() for line in content if line.strip())  # Remove blank lines

        contents = indent(content, f"{INDENT_CHAR}> ")
        contents += "\n"
        if self.attachment:
            if "image" in self.attachment:
                contents += f"![]({self.attachment['image']})\n"

        return contents


class Item:
    def __init__(self, content, checked, description, date_added):
        self.content: str = content
        self.checked: bool = checked
        self.description: str = description
        self.date_added: str = date_added
        self.items: List[Item] = []
        self.labels: List[str] = []
        self.notes: List[Note] = []

    def __repr__(self) -> str:
        return f"Item['{self.content}', {self.checked}, '{self.description}', {self.date_added}, {self.items}, {self.labels}, {self.notes}]"

    def unparse(self, indent_level: int, item_count: int) -> Tuple[str, str, int]:
        contents = ""
        contents_foot = ""

        if ADD_DATE:
            date = datetime.strptime(self.date_added.strip("Z"), JSON_DATE_FORMAT)
            contents_foot += f"{INDENT_CHAR}*{date.strftime(MARKDOWN_DATE_FORMAT)}*\n"

        if self.description:
            contents_foot += f"{INDENT_CHAR}{self.description}\n"

        first_note = True
        for note in self.notes:
            line = note.unparse() + "\n"
            if first_note:
                line = line.removeprefix(INDENT_CHAR)

            contents_foot += line
            first_note = False

        if self.content.startswith("*"):
            contents += self.content[2:].strip()
        else:
            check_char = "x" if self.checked else " "
            contents += f"- [{check_char}] {self.content}"

        for label in self.labels:
            contents += f" #{label}"

        if contents_foot:
            # Task has footnote
            contents += f"[^{item_count}]"
            contents_foot = f"[^{item_count}]: " + contents_foot
            contents_foot += "\n"

        contents += "\n"

        item_count += 1  # Add this item to the running total

        for item in self.items:
            item_contents, item_contents_foot, item_count = item.unparse(indent_level+1, item_count)
            contents += item_contents
            contents_foot += item_contents_foot

        return indent(contents, INDENT_CHAR * indent_level), contents_foot, item_count


class Section:
    def __init__(self, name):
        self.items: List[Item] = []
        self.name: str = name
    def __repr__(self) -> str:
        return f"Section['{self.name}', {self.items}]"

    def unparse(self, item_count) -> Tuple[str, str, int]:
        contents = ""
        contents_foot = ""

        contents += f"## {self.name}\n\n"

        for item in self.items:
            item_contents, item_contents_foot, item_count = item.unparse(0, item_count)
            contents += item_contents
            contents_foot += item_contents_foot

        return contents, contents_foot, item_count


class Project:
    def __init__(self, name):
        self.items: List[Item] = []
        self.sections: Dict[str, Section] = {}
        self.name: str = name
        self.notes: List[Note] = []

    def __repr__(self) -> str:
        return f"Project['{self.name}', {self.items}, {self.sections}, {self.notes}]"

    def unparse(self) -> str:
        contents = ""
        contents_foot = ""
        item_count = 0

        contents += f"# {self.name}\n\n"

        for note in self.notes:
            note_contents = note.unparse()
            contents += note_contents

        for item in self.items:
            item_contents, item_contents_foot, item_count = item.unparse(0, item_count)
            contents += item_contents
            contents_foot += item_contents_foot

        contents += "\n\n"
        for section in self.sections.values():
            section_contents, section_contents_foot, item_count = section.unparse(item_count)
            contents += section_contents
            contents_foot += section_contents_foot

        return contents + "\n" + contents_foot

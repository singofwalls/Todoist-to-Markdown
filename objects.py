
from datetime import datetime
from typing import Dict, List, Optional
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

    def unparse(self, indent_level=0) -> str:
        contents = indent(self.content, "> ") + "\n"
        if self.attachment:
            if "image" in self.attachment:
                contents += f"![]({self.attachment['image']})\n"

        if indent_level >= 1:
            indent_level -= 1
        return indent(contents, INDENT_CHAR * indent_level)


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

    def unparse(self, indent_level=0) -> str:
        contents = ""

        if self.content.startswith("*"):
            contents += self.content[2:].strip()
        else:
            check_char = "x" if self.checked else " "
            contents += f"- [{check_char}] {self.content}"

        for label in self.labels:
            contents += f" #{label}"

        contents += "\n"

        if ADD_DATE:
            date = datetime.strptime(self.date_added.strip("Z"), JSON_DATE_FORMAT)
            contents += f"{INDENT_CHAR}*{date.strftime(MARKDOWN_DATE_FORMAT)}*\n"

        if self.description:
            contents += f"{INDENT_CHAR}{self.description}\n"

        for note in self.notes:
            contents += note.unparse(indent_level+1)

        for item in self.items:
            contents += item.unparse(indent_level+1)

        return indent(contents, INDENT_CHAR * indent_level)


class Section:
    def __init__(self, name):
        self.items: List[Item] = []
        self.name: str = name
    def __repr__(self) -> str:
        return f"Section['{self.name}', {self.items}]"

    def unparse(self) -> str:
        contents = ""
        contents += f"## {self.name}\n\n"

        for item in self.items:
            contents += item.unparse()

        return contents


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
        contents += f"# {self.name}\n\n"

        for note in self.notes:
            contents += note.unparse()

        for item in self.items:
            contents += item.unparse()

        contents += "\n\n"
        for section in self.sections.values():
            contents += section.unparse()

        return contents

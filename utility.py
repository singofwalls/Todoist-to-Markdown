
from typing import Dict, Optional


class Note:
    def __init__(self, content):
        self.content = content
        self.attachment: Optional[Dict[str, str]] = None

    def __repr__(self) -> str:
        return f"Note['{self.content}', {self.attachment}]"

class Item:
    def __init__(self, content, checked, description, date_added):
        self.content = content
        self.checked = checked
        self.description = description
        self.date_added = date_added
        self.items = []
        self.labels = []
        self.notes = []

    def __repr__(self) -> str:
        return f"Item['{self.content}', {self.checked}, '{self.description}', {self.date_added}, {self.items}, {self.labels}, {self.notes}]"


class Section:
    def __init__(self, name):
        self.items = []
        self.name = name
    def __repr__(self) -> str:
        return f"Section['{self.name}', {self.items}]"


class Project:
    def __init__(self, name):
        self.items = []
        self.sections: Dict[str, Section] = {}
        self.name = name
        self.notes = []

    def __repr__(self) -> str:
        return f"Project['{self.name}', {self.items}, {self.sections}, {self.notes}]"

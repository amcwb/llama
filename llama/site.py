from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, Union

import yaml


class Page:
    def __init__(self, title: str, link: str) -> None:
        self.title = title
        self.link = link


class Site:
    def __init__(self, title: str, description: str, config: Dict[str, Any], pages: list = None):
        self.title = title
        self.description = description
        self.index = defaultdict(list)

        self.config = config

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "index": dict(self.index),
            "config": self.config
        }

    @classmethod
    def load_from_yaml(cls, directory: Union[str, Path]):
        with open(directory, "r") as file:
            data = yaml.load(file, Loader=yaml.CLoader)
            return cls(
                title=data.get("title", None),
                description=data.get("description", None),
                config=data.get("config", {})
            )

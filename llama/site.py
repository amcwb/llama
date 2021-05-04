from collections import defaultdict
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Optional, Union
import urllib

import yaml

import llama


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
            "config": self.config,
            "llama-version": llama.__version__,
            "base-url": self.base_url
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

    @property
    def base_url(self) -> str:
        return self.config.get("llama-base-url", "/")

    @property
    def posts_url(self) -> Optional[str]:
        posts_config = self.config.get("llama-posts")
        if posts_config and posts_config.get("active", True):
            return posts_config.get("outdir", ".")
        
        return None
    
    @property
    def static_url(self) -> Optional[str]:
        static_config = self.config.get("llama-static")
        if static_config and static_config.get("active", True):
            return static_config.get("outdir", ".")
        
        return None

    @property
    def pages_url(self) -> Optional[str]:
        pages_config = self.config.get("llama-posts")
        if pages_config and pages_config.get("active", True):
            return pages_config.get("outdir", ".")
        
        return None

    def build_url(self, *parts):
        return urllib.parse.urljoin(self.base_url, str(PurePosixPath(*parts)))
        
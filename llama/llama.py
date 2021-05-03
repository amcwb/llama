# Copyright (C) 2021 Avery
#
# This file is part of llama.
#
# llama is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# llama is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with llama.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple, Union

from llama.components.handler import Handler
from llama.components.renderer import Renderer
from llama.site import Site


class Llama:
    def __init__(self, site: Site, handlers: Dict[str, Tuple[Handler, str]] = None):
        self.site = site
        self.handlers = handlers or {}

    def set_handler(self, directory: str, handler: Handler, target: str):
        """
        Set the handler for a directory

        Parameters
        ----------
        directory : str
            The directory to handle
        handler : Handler
            The handler
        target : str
            Target sub-directory
        """
        self.handlers[directory] = (handler, target)
        handler.set_site(self.site)

    def get_handler(self, directory: str) -> Optional[Handler]:
        """
        Get the handler for a directory

        Parameters
        ----------
        directory : str
            The directory

        Returns
        -------
        Handler
            The handler, or None if it doesn't exist
        """
        return self.handlers.get(directory, None)

    def build(self, file_dir: str, target_dir: str, renderer: Renderer):
        """
        Build a given file into the target directory using the given renderer

        Parameters
        ----------
        file_dir : str
            The source file path
        target_dir : str
            The target directory
        renderer : Renderer
            The renderer to use
        """
        Path(target_dir).parent.mkdir(parents=True, exist_ok=True)
        with open(target_dir, "w+") as file:
            file.write(renderer.render(open(file_dir).read()))

    def build_from(self, source_dir: str, target_dir: str, ignore_unknown: bool = False):
        """
        Build from a source directory to a target directory

        Parameters
        ----------
        source_dir : str
            The source directory
        target_dir : str
            The target directory
        ignore_unknown : bool
            Whether to ignore unknown files
        """
        for directory, (handler, target) in self.handlers.items():
            handler.build_from(Path(source_dir) / directory, Path(target_dir) / target)

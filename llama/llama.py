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
from typing import Callable, Dict, List, Optional, Tuple, Union

from llama.components.handler import Handler
from llama.components.renderer import Renderer
from llama.site import Site


class Llama:
    def __init__(self, site: Site, source_dir: str, target_dir: str, handlers: List[Handler] = None):
        self.site = site
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.handlers = handlers or []

    def set_handler(self, handler: Handler):
        """
        Add a handler

        Parameters
        ----------
        handler : Handler
            The handler
        """
        self.handlers.append(handler)

    def build(self):
        """
        Build from the source directory to the target directory
        """
        for handler in self.handlers:
            handler.target_dir = Path(self.target_dir) / handler.target_dir
            handler.source_dir = Path(self.source_dir) / handler.source_dir
            
            handler.run_index()
            handler.update_site_index()
        
        for handler in self.handlers:
            handler.run_render()
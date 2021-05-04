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

import operator
import os
from pathlib import Path
from typing import Callable, Optional, Union

from frontmatter import Post
from llama.components.renderer import Renderer
from llama.site import Site


class Handler:
    def __init__(self, priority: int = 1) -> None:
        self.site = None
        self.priority = priority

    def set_site(self, site: Site):
       self.site = site 

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
        raise NotImplementedError


class StaticHandler(Handler):
    def __init__(self, priority: int = 1) -> None:
        super().__init__(priority=priority)

    def build_from(self, source_dir: str, target_dir: str, _ignore_unknown: bool = False):
        """
        Build from a source directory to a target directory

        Parameters
        ----------
        source_dir : str
            The source directory
        target_dir : str
            The target directory
        """
        for dir_path, dirnames, filenames in os.walk(source_dir):
            for filename in filenames:
                source = Path(dir_path) / filename
                target = Path(target_dir) / Path(source.parent).relative_to(source_dir) / filename
                target.parent.mkdir(parents=True, exist_ok=True)
                with open(target, "wb+") as file:
                    file.write(open(source, "rb").read())


class PostHandler(Handler):
    @staticmethod
    def default_indexer(index: str):
        def _default_indexer(site: Site, data: Post, target: str):
            site.index[index].append([
                data.metadata['title'], site.build_url(Path(target).relative_to(Path(site.config.get("llama-target"))))
            ])
        
        return _default_indexer

    def __init__(self, priority: int = 1, renderers: list = None, indexer = None):
        super().__init__(priority=priority)
        self.renderers = []

        if renderers is not None:
            for renderer in renderers:
                self.set_renderer(*renderer)
        
        if indexer is None:
            self.indexer = lambda *_: None
        elif isinstance(indexer, str):
            self.indexer = PostHandler.default_indexer(indexer)
        else:
            self.indexer = indexer

    def set_site(self, site: Site):
        super().set_site(site)

        for _pred, renderer in self.renderers:
            renderer.set_site(site)

    def set_renderer(self, pred_or_ext: Union[str, Callable[[str], bool]], renderer: Renderer):
        """
        Set the renderer for either a filename check predicate or a file
        extension

        Parameters
        ----------
        pred_or_ext : str or callable
            The extension or predicate
        renderer : Renderer
            The renderer to use
        """
        if isinstance(pred_or_ext, str):
            extension = pred_or_ext
            def pred_or_ext(filename): return filename.endswith(
                "." + extension)

        self.renderers.append([pred_or_ext, renderer])
        renderer.set_site(self.site)

    def get_renderer(self, filename: str) -> Optional[Renderer]:
        """
        Get the renderer for a filename

        Parameters
        ----------
        filename : str
            The filename

        Returns
        -------
        Renderer
            The renderer, or None if it doesn't exist
        """
        for pred, renderer in self.renderers:
            if pred(filename):
                return renderer

        return None

    def build(self, data: Post, target_dir: str, renderer: Renderer):
        """
        Build a given file into the target directory using the given renderer

        Parameters
        ----------
        data : frontmatter.Post
            The source data
        target_dir : str
            The target directory
        renderer : Renderer
            The renderer to use
        """
        Path(target_dir).parent.mkdir(parents=True, exist_ok=True)
        with open(target_dir, "w+") as file:
            file.write(renderer.render(data))

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
        targets = []
        for dir_path, dirnames, filenames in os.walk(source_dir):
            for filename in filenames:
                target = Path(target_dir) / Path(dir_path).relative_to(source_dir)
                targets.append([filename, dir_path, target, self.get_renderer(filename)])
        
        def _get_priority(s):
            return s[3].priority

        for filename, dir_path, target, renderer in sorted(targets, key=_get_priority):
            self.handle_file(filename, dir_path,
                             target, renderer, ignore_unknown)

    def handle_file(self, filename: str, dir_path: str, target_dir: str, renderer: Renderer, ignore_unknown: bool = False):
        """
        Build a file to the target directory using the appropriate renderer

        Parameters
        ----------
        filename : str
            The filename
        dir_path : str
            The directory this file is found in
        target_dir : str
            The target directory for this file
        renderer : Renderer
            Renderer to use
        ignore_unknown : bool
            Whether to ignore unknown extensions
        """
        name, ext = filename.split(".", 1)
        source = Path(dir_path) / filename
        target = Path(target_dir)

        if renderer:
            target /= (name + "." + renderer.extension)
            data = renderer.get_page_data(open(source).read())

            self.indexer(self.site, data, target)
            self.build(data, target, renderer)
        elif not ignore_unknown:
            raise KeyError("Unknown file {}".format(source))

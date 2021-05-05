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
import frontmatter
from llama.components.renderer import Renderer
from llama.site import Site


class Handler:
    def __init__(self, ll: "Llama", source_dir: str, target_dir: str, renderers: list = None, index_key: str = None) -> None:
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.renderers = renderers or []

        self.preindexhooks = []
        self.postindexhooks = []
        self.prerenderhooks = []
        self.postrenderhooks = []

        self.index = []
        self.index_key = index_key or "misc"
        self.ll: "Llama" = ll

    def preindex(self, method: Callable) -> Callable:
        """
        Add a preindex hook

        Parameters
        ----------
        method : Callable
            The method to run

        Returns
        -------
        Callable
            The method provided
        """
        self.preindexhooks.append(method)

        return method

    def postindex(self, method: Callable) -> Callable:
        """
        Add a postindex hook

        Parameters
        ----------
        method : Callable
            The method to run

        Returns
        -------
        Callable
            The method provided
        """
        self.postindexhooks.append(method)

        return method

    def _pre_index(self):
        """
        Run preindex hooks
        """
        for prehook in self.preindexhooks:
            prehook(self)

    def _post_index(self):
        """
        Run postindex hooks
        """
        for posthook in self.postindexhooks:
            posthook(self)

    def prerender(self, method: Callable) -> Callable:
        """
        Add a prerender hook

        Parameters
        ----------
        method : Callable
            The method to run

        Returns
        -------
        Callable
            The method provided
        """
        self.preindexhooks.append(method)

        return method

    def postrender(self, method: Callable) -> Callable:
        """
        Add a postrender hook

        Parameters
        ----------
        method : Callable
            The method to run

        Returns
        -------
        Callable
            The method provided
        """
        self.postrenderhooks.append(method)

        return method

    def _pre_render(self):
        """
        Run prerender hooks
        """
        for prehook in self.prerenderhooks:
            prehook(self)

    def _post_render(self):
        """
        Run postrender hooks
        """
        for posthook in self.postrenderhooks:
            posthook(self)

    def run_index(self):
        """
        Index the files and their information
        """
        self._pre_index()

        self.index = []
        for dir_path, dirnames, filenames in os.walk(self.source_dir):
            for filename in filenames:
                current_dir = Path(dir_path)
                target = Path(self.target_dir) / \
                    current_dir.relative_to(self.source_dir)

                renderer = self.get_renderer(filename)
                target_filename = (filename.split(".", 1)[0] + '.' + renderer.extension)
                self.index.append({
                    '_i': {
                        'filename': filename,
                        'dir': current_dir,
                        'target': target,
                        'renderer': renderer
                    },
                    'url': self.ll.site.build_url(Path(target).relative_to(Path(self.ll.target_dir)), target_filename),
                    **self.get_page_data((current_dir / filename).read_bytes())
                })

        self._post_index()

    def run_render(self):
        """
        Render the files and their information
        """
        raise NotImplementedError

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

    def update_site_index(self):
        """
        Update the site index
        """
        self.ll.site.index[self.index_key] = self.index[:]

    def get_page_data(self, content: str) -> dict:
        return frontmatter.loads(content).to_dict()



class StaticHandler(Handler):
    def __init__(self, ll: "Llama", source_dir: str, target_dir: str) -> None:
        super().__init__(ll, source_dir, target_dir)

    def run_index(self):
        """
        Index the files and their information
        """
        self._pre_index()

        self.index = []
        for dir_path, dirnames, filenames in os.walk(self.source_dir):
            for filename in filenames:
                current_dir = Path(dir_path)
                target = Path(self.target_dir) / \
                    current_dir.relative_to(self.source_dir)

                self.index.append({
                    '_i': {
                        'filename': filename,
                        'dir': current_dir,
                        'target': target
                    },
                    'url': self.ll.site.build_url(Path(target).relative_to(Path(self.ll.target_dir)), filename),
                    **self.get_page_data((current_dir / filename).read_bytes())
                })

        self._post_index()

    def run_render(self):
        """
        Render the files and their information
        """
        self._pre_render()

        for entry in self.index:
            target = entry['_i']['target'] / entry['_i']['filename']
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "wb+") as file:
                file.write(entry['content'])

        self._post_render()
    
    def get_page_data(self, content: str) -> dict:
        return {
            "content": content
        }


class PostHandler(Handler):
    def __init__(self, ll: "Llama", source_dir: str, target_dir: str, renderers: list = None, index_key: str = None) -> None:
        super().__init__(ll, source_dir, target_dir, renderers, index_key)

    def run_render(self):
        """
        Render the files and their information
        """
        self._pre_render()

        for entry in self.index:
            renderer = entry['_i']['renderer']
            name, ext = entry['_i']['filename'].split(".", 1)
            
            target = entry['_i']['target'] / (name + '.' + renderer.extension)
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w+") as file:
                file.write(renderer.render(entry))

        
        self._post_render()


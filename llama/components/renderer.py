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

from typing import Dict

import frontmatter
import markdown2
from liquid.template import BoundTemplate
from llama.site import Site


class Renderer:
    def __init__(self, ll: "Llama", extension: str, template: BoundTemplate, priority: int = 1, preprocessors=None, postprocessors=None):
        self.ll = ll
        self.priority = priority
        self.template = template
        self.extension = extension
        self.preprocessors = preprocessors or []
        self.postprocessors = postprocessors or []

    def run_preproc(self, content: str) -> str:
        """
        Run preprocessing code on the content, probably markdown.

        Parameters
        ----------
        content : str
            The content of the current page

        Returns
        -------
        str
            The resultant content
        """
        for preproc in self.preprocessors:
            content = preproc(content)

        return content

    def run_postproc(self, content: str) -> str:
        """
        Run postprocessing code on the content, probably HTML.

        Parameters
        ----------
        content : str
            The content of the current page

        Returns
        -------
        str
            The resultant content
        """
        for postproc in self.postprocessors:
            content = postproc(content)

        return content

    def get_page_data(self, content: str):
        return frontmatter.loads(content)

    def render(self, page_data: dict, extras=["fenced-code-blocks"]):
        content = self.run_preproc(page_data['content'])

        content = markdown2.markdown(content, extras=extras)

        content = self.run_postproc(content)

        return self.template.render(page={
            **page_data,
            "content": content
        }, site=self.ll.site.to_dict())

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} template={self.template} extension='{self.extension}' preproc={len(self.preprocessors)} postproc={len(self.postprocessors)}>"


class MetadataRenderer(Renderer):
    def __init__(self, ll: "Llama", extension: str, renderers: Dict[str, Renderer], default: str, priority: int = 1):
        self.ll = ll
        self.extension = extension
        self.renderers = renderers
        self.default = default
        self.priority = priority

        self.site = None

    def render(self, page_data: dict, extras=["fenced-code-blocks"]):
        # For metadata renderers, the metadata is extracted seperately
        renderer: Renderer = self.renderers.get(page_data.get("type"))

        if not renderer:
            raise KeyError("Unknown type {}".format(page_data.get("type")))

        return renderer.render(page_data, extras=extras)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} extension='{self.extension}' renderers={self.renderers}>"

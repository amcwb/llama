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

from pathlib import Path

from liquid import Template
from liquid.environment import Environment
from liquid.loaders import FileSystemLoader

from llama.components.renderer import MetadataRenderer, Renderer
from llama.llama import Llama

if __name__ == "__main__":
    env = Environment(loader=FileSystemLoader("templates/"))

    l = Llama()
    l.set_renderer("md", MetadataRenderer("html", {
        "post": Renderer("html", env.get_template("post.html"))
    }, "post"))

    l.build_from(Path("posts"), Path("build"))

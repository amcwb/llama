from pathlib import Path

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

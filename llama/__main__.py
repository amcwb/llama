import os
from pathlib import Path

from liquid.environment import Environment
from liquid.loaders import FileSystemLoader

from llama.components.handler import PostHandler, StaticHandler
from llama.components.renderer import MetadataRenderer, Renderer
from llama.llama import Llama


def get_static(*parts):
    return os.path.join("static", *parts)

if __name__ == "__main__":
    env = Environment(loader=FileSystemLoader("templates/"), globals={
        "static": get_static
    })

    ll = Llama()
    metadata_renderer = MetadataRenderer("html", {
        "post": Renderer("html", env.get_template("post.html")),
        "index": Renderer("html", env.get_template("index.html")),
    }, default="post")
    post_handler = PostHandler()
    post_handler.set_renderer("md", metadata_renderer)

    ll.set_handler("source/pages", post_handler, ".")
    ll.set_handler("source/posts", post_handler, "posts")
    ll.set_handler("static", StaticHandler(), "static")

    ll.build_from(Path("."), Path("build"))

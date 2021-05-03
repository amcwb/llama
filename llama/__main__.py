from llama.site import Site
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

    ll = Llama(site=Site.load_from_yaml("config.yml"))

    post_config = ll.site.config.get("llama-posts")
    if post_config or post_config.get("active", True):
        metadata_renderer = MetadataRenderer("html", {
            "post": Renderer("html", env.get_template("post.html")),
            "index": Renderer("html", env.get_template("index.html")),
        }, default="post")

    pages_config = ll.site.config.get("llama-pages")
    if pages_config and pages_config.get("active", True):
        metadata_renderer = MetadataRenderer("html", {
            "index": Renderer("html", env.get_template("index.html")),
        }, default="index")

        pages_handler = PostHandler()
        pages_handler.set_renderer("md", metadata_renderer)
        ll.set_handler(pages_config.get("indir", "source/pages"),
                       pages_handler, pages_config.get("outdir", "."))

    post_config = ll.site.config.get("llama-posts")
    if post_config and post_config.get("active", True):
        metadata_renderer = MetadataRenderer("html", {
            "post": Renderer("html", env.get_template("post.html"))
        }, default="post")

        post_handler = PostHandler()
        post_handler.set_renderer("md", metadata_renderer)
        ll.set_handler(post_config.get("indir", "source/posts"),
                       post_handler, post_config.get("outdir", "posts"))

    static_config = ll.site.config.get("llama-static")
    if static_config and static_config.get("active", True):
        ll.set_handler(static_config.get("intdir", "static"),
                       StaticHandler(), static_config.get("outdir", "static"))

    ll.build_from(Path("."), Path("build"))

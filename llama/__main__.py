from llama.features.postproc import previous_next, sort_posts
from llama.site import Site
import urllib
from pathlib import Path, PurePosixPath

from liquid.environment import Environment
from liquid.loaders import FileSystemLoader

from llama.components.handler import PostHandler, StaticHandler
from llama.components.renderer import MetadataRenderer, Renderer
from llama.llama import Llama


def get_base_factory(base_url: str):
    def _get_base(parts):
        if isinstance(parts, str):
            parts = [parts]

        return urllib.parse.urljoin(base_url, str(PurePosixPath(*parts)))
    return _get_base


def get_static_factory(base_fn):
    def _get_static(parts):
        if isinstance(parts, str):
            parts = [parts]

        return base_fn(["static", *parts])

    return _get_static


if __name__ == "__main__":
    site = Site.load_from_yaml("config.yml")
    ll = Llama(site=site, source_dir=Path(site.config.get("llama-source")),
               target_dir=Path(site.config.get("llama-target")))

    env = Environment(loader=FileSystemLoader("templates/"))

    base_factory = get_base_factory(ll.site.base_url)
    env.add_filter("base", base_factory)
    env.add_filter("static", get_static_factory(base_factory))

    post_config = ll.site.config.get("llama-posts")
    if post_config and post_config.get("active", True):
        metadata_renderer = MetadataRenderer(ll, "html", {
            "post": Renderer(ll, "html", env.get_template("post.html"))
        }, default="post")

        post_handler = PostHandler(ll, post_config.get("indir", "source/posts"),
                                   post_config.get("outdir", "posts"), index_key="posts")
        post_handler.set_renderer("md", metadata_renderer)
        post_handler.postindex(sort_posts)
        post_handler.postindex(previous_next)

        ll.set_handler(post_handler)

    pages_config = ll.site.config.get("llama-pages")
    if pages_config and pages_config.get("active", True):
        metadata_renderer = MetadataRenderer(ll, "html", {
            "index": Renderer(ll, "html", env.get_template("index.html")),
            "404": Renderer(ll, "html", env.get_template("404.html")),
        }, default="index")

        pages_handler = PostHandler(ll, pages_config.get(
            "indir", "source/pages"), pages_config.get("outdir", "."))
        pages_handler.set_renderer("md", metadata_renderer)

        ll.set_handler(pages_handler)

    static_config = ll.site.config.get("llama-static")
    if static_config and static_config.get("active", True):
        ll.set_handler(StaticHandler(ll, static_config.get(
            "indir", "static"), static_config.get("outdir", "static")))

    ll.build()

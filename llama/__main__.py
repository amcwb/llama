from llama.features.postproc import sort_posts
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
    ll = Llama(site=Site.load_from_yaml("config.yml"))
    
    env = Environment(loader=FileSystemLoader("templates/"))
    
    base_factory = get_base_factory(ll.site.base_url)
    env.add_filter("base", base_factory)
    env.add_filter("static", get_static_factory(base_factory))

    post_config = ll.site.config.get("llama-posts")
    if post_config and post_config.get("active", True):
        metadata_renderer = MetadataRenderer("html", {
            "post": Renderer("html", env.get_template("post.html"))
        }, default="post")

        post_handler = PostHandler(priority=0, indexer="posts", postprocessors=[sort_posts("posts")])
        post_handler.set_renderer("md", metadata_renderer)
        ll.set_handler(
            post_config.get("indir", "source/posts"),
            post_handler,
            post_config.get("outdir", "posts"))

    pages_config = ll.site.config.get("llama-pages")
    if pages_config and pages_config.get("active", True):
        metadata_renderer = MetadataRenderer("html", {
            "index": Renderer("html", env.get_template("index.html")),
            "404": Renderer("html", env.get_template("404.html")),
        }, default="index")

        pages_handler = PostHandler()
        pages_handler.set_renderer("md", metadata_renderer)
        ll.set_handler(
            pages_config.get("indir", "source/pages"),
            pages_handler,
            pages_config.get("outdir", "."))

    static_config = ll.site.config.get("llama-static")
    if static_config and static_config.get("active", True):
        ll.set_handler(
            static_config.get("indir", "static"),
            StaticHandler(),
            static_config.get("outdir", "static"))

    ll.build_from(Path(ll.site.config.get("llama-source")), Path(ll.site.config.get("llama-target")))

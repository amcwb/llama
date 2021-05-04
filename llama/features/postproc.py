

from llama.components.handler import PostHandler


def sort_posts(index: str):
    def _sort_posts(handler: PostHandler):
        handler.site.index[index].sort(key=lambda s: s['time'], reverse=True)
    
    return _sort_posts
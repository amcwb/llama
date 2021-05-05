

from llama.components.handler import PostHandler


def sort_posts(handler: PostHandler):
    handler.index.sort(key=lambda s: s['time'], reverse=True)

def previous_next(handler: PostHandler):
    for i in range(len(handler.index)):
        entry = handler.index[i]
        if i != 0:
            entry['next'] = handler.index[i-1]
        
        if i < len(handler.index) - 1:
            entry['previous'] = handler.index[i+1]
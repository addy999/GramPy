import json
from types import SimpleNamespace


def json_to_obj(data) -> object:
    return json.loads(data, object_hook=lambda d: SimpleNamespace(**d))


def get_data_from_resp(resp) -> object:
    return json_to_obj(resp.html.html)


def node_to_post(node) -> dict:
    resp = dict(
        thumbnail_url=node.thumbnail_src,
        url=node.display_url,
        caption=node.edge_media_to_caption.edges[0].node.text,
        likes=node.edge_liked_by.count,
        n_comments=node.edge_media_to_comment.count,
        tagged=[],
    )

    if node.is_video:
        resp.update(dict(url=node.video_url, views=node.video_view_count))

    if node.edge_media_to_tagged_user.edges:
        resp.update(
            dict(
                tagged=[
                    edge.node.user.username
                    for edge in node.edge_media_to_tagged_user.edges
                ]
            )
        )

    return resp


def nodes_to_posts(edges) -> list:
    return [node_to_post(edge.node) for edge in edges]

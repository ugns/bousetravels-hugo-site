import os
from atproto import Client, DidInMemoryCache, IdResolver, client_utils, models
from urllib.parse import urlparse
import requests


def parse_hashtags_and_links(message):
    import re
    tb = client_utils.TextBuilder()
    last_idx = 0
    for match in re.finditer(r"#\w+|https?://[\w\.-]+(?:/[\w\./?%&=\-]*)?", message):
        start, end = match.span()
        if start > last_idx:
            tb.text(message[last_idx:start])
        token = message[start:end]
        if token.startswith('#'):
            tb.tag(token, token.lstrip('#'))
        elif token.startswith('http'):
            hostname = urlparse(token).hostname or token
            tb.link(hostname, token)
        last_idx = end
    if last_idx < len(message):
        tb.text(message[last_idx:])
    return tb


def create_bluesky_embed(meta, client):
    thumb_blob = None
    if meta and 'og:image' in meta:
        try:
            img_resp = requests.get(meta['og:image'], timeout=10)
            img_resp.raise_for_status()
            upload_result = client.upload_blob(img_resp.content)
            if hasattr(upload_result, 'ref') and 'Response' not in str(type(upload_result)):
                thumb_blob = upload_result
            elif hasattr(upload_result, 'blob'):
                thumb_blob = upload_result.blob
            else:
                thumb_blob = None
        except Exception as img_err:
            print(f"[Bluesky] Error uploading image blob: {img_err}")
            thumb_blob = None
    try:
        embed = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                uri=meta['og:url'] if meta and 'og:url' in meta else "",
                title=meta['og:title'] if meta and 'og:title' in meta else "",
                description=meta['og:description'] if meta and 'og:description' in meta else "",
                thumb=thumb_blob if (thumb_blob is not None and hasattr(thumb_blob, 'ref')) else None
            )
        )
    except Exception as embed_err:
        print(f"[Bluesky] Error creating embed: {embed_err}")
        embed = None
    return embed


def validate_bluesky_env():
    required_vars = ["BLUESKY_HANDLE", "BLUESKY_APP_PASSWORD"]
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        raise EnvironmentError(f"Missing required Bluesky environment variables: {', '.join(missing)}")


def post_to_bluesky(message, link, fetch_page_metadata):
    validate_bluesky_env()
    handle = os.getenv("BLUESKY_HANDLE")
    app_password = os.getenv("BLUESKY_APP_PASSWORD")
    if not handle or not app_password:
        raise ValueError("Bluesky credentials not set in environment variables")
    try:
        cache = DidInMemoryCache()
        resolver = IdResolver(cache=cache)
        did = resolver.did.resolve(resolver.handle.resolve(handle))  # type: ignore
        client = Client(base_url=did.get_pds_endpoint()) if did.get_pds_endpoint() else Client()  # type: ignore
        client.login(handle, app_password)
        tb = parse_hashtags_and_links(message)
        meta = fetch_page_metadata(link)
        embed = create_bluesky_embed(meta, client)
        if embed:
            client.send_post(tb, embed=embed)
        else:
            client.send_post(tb)
        print(f"[Bluesky] Posted: {tb.build_text()}")
    except Exception as e:
        print(f"[Bluesky] Error posting to Bluesky: {e}")
        raise

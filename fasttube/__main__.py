# -*- coding: utf-8 -*-
# :removed: age_restriction and proxy 
"""
This module implements the core developer interface for pytube_ex.

The problem domain of the :class:`YouTube <YouTube> class focuses almost
exclusively on the developer interface. pytube_ex offloads the heavy lifting to
smaller peripheral modules and functions.

"""
# -*- coding: utf-8 -*-

import json
from functools import cached_property
from typing import Dict, Optional
from urllib.parse import quote

from fasttube import request

from .cipher import Cipher
from .exceptions import RegexMatchError, VideoUnavailable
from .extract import (apply_descrambler, apply_signature, extract_video_id,
                      get_ytplayer_config, grabe_url_encoded_fmt)
from .helpers import safe_filename


class YouTube:

    def __init__(self, url: str,):
        self.title: str = ""
        self.js_url: Optional[str] = None

        self.watch_html: Optional[str] = None
        self.player_response = None

        self.adaptive_fmts: Dict = []
        self.stream_maps: Dict = []

        self.video_id = extract_video_id(url)
        self.watch_url = f"https://youtube.com/watch?v={self.video_id}"

        self.prefetch()
        self.descramble()

    def descramble(self) -> None:
        self.title = self.player_response["videoDetails"]["title"]
        self.title = safe_filename(self.title)

        self.stream_maps.extend(grabe_url_encoded_fmt(self.player_response))
        if self.adaptive_fmts:
            self.stream_maps.extend(apply_descrambler(self.adaptive_fmts, "adaptive_fmts"))

        self.stream_maps.sort(key=lambda s: s["quality"], reverse=True)

    def prefetch(self) -> None:
        self.watch_html = request.get(url=self.watch_url)
        if self.watch_html is None:
            raise VideoUnavailable(video_id=self.video_id)
        if "This video is private" in self.watch_html:
            raise VideoUnavailable(video_id=self.video_id)

        player_config = get_ytplayer_config(self.watch_html)
        self.player_response = json.loads(player_config["args"]["player_response"])
        self.adaptive_fmts = player_config["args"].get("adaptive_fmts", None)

        self.js_url = "https://youtube.com" + player_config["assets"]["js"]

    @cached_property
    def js(self):
        return request.get(self.js_url)

    def dress_up(self, stream):
        if stream.get("dressed", None):
            return stream

        pos=self.stream_maps.index(stream)
        if "s" in stream:
            apply_signature(stream, self.js)
            del stream["s"]

        if "title" not in stream["url"]:# i may remove this condetion and
            stream["url"]+=f"&title={quote(self.title)}"# make this compulsory

        stream["dressed"]=True
        self.stream_maps[pos]=stream
        return stream

    def filter(self, quality: int, list_=False) -> Dict:

        stream = next(filter(lambda s: s["quality"]<=quality, self.stream_maps)) or next(
            filter(lambda s: s["quality"]>quality, self.stream_maps)
            )
        return self.dress_up(stream)

    def __getitem__(self, i):
        return self.dress_up(self.stream_maps[i])

    def __iter__(self):
        return iter(self.stream_maps)

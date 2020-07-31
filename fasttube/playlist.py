# -*- coding: utf-8 -*-

import json
import re
from functools import cached_property  # someting gives None
from typing import Iterable, List, Optional, Union
from urllib.parse import parse_qs

from .request import get


class Values:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self):
        return str(self.__dict__)

class Playlist:

    def __init__(self, url: str):
        try:
            # https://www.youtube.com/watch?v=AxVyGpoKmKk&list=PLwgFb6VsUj_ne_1dsvzEOiQFiAqCMUeio&index=6
            # v=AxVyGpoKmKk&list=PLwgFb6VsUj_ne_1dsvzEOiQFiAqCMUeio&index=6
            # {'v': ['AxVyGpoKmKk'], 'list': ['PLwgFb6VsUj_ne_1dsvzEOiQFiAqCMUeio'], 'index': ['6']}
            self.playlist_id: str = parse_qs(url.split("?")[1])["list"][0]
        except IndexError:  # assume that url is just the id
            self.playlist_id = url

        self.playlist_url = f"https://www.youtube.com/playlist?list={self.playlist_id}"
        self.html = get(self.playlist_url)
        self._len=int(re.search(r'(\d+) videos', self.html).group(1))

    @staticmethod
    def _find_load_more_url(req: str) -> Optional[str]:
        """Given an html page or fragment, returns the "load more" url if found."""
        match = re.search(
            r"data-uix-load-more-href=\"(/browse_ajax\?" 'action_continuation=.*?)"',
            req,
        )
        if match:
            return f"https://www.youtube.com{match.group(1)}"

        return None

    def _paginate(self) -> Iterable[List[str]]:
        """Parse the video links from the page source, yields the /watch?v= part from video link
        """
        req = self.html
        videos_lens = self._extractor(req)
        yield videos_lens # yielding doesn't mean that is the end

        # The above only returns 100 or fewer links
        # as Youtube loads 100 videos at a time
        # Simulating a browser request for the load more link
        load_more_url = self._find_load_more_url(req)

        while load_more_url:  # there is an url found
            req = get(load_more_url)
            load_more = json.loads(req)
            try:
                html = load_more["content_html"]
            except KeyError:
                return # if there is no content_html there is no chanch to find_load_more_url
            videos_lens = self._extractor(html)
            yield videos_lens

            load_more_url = self._find_load_more_url(
                load_more["load_more_widget_html"],
            )

        return

    def _extractor(self, html: str) -> List[str]:
        patt=re.compile('{"playlistVideoRenderer":.+?}]}}}]}}')# all data for a single video
        
        matches=re.finditer(patt, html)
        for i in matches:
            data=json.loads(i.group())
            data=data["playlistVideoRenderer"]
            yield Values(index  = int(data["index"]["simpleText"]),
                         title  = data["title"]["simpleText"],
                         url    = "https://youtu.be/"+data["videoId"],
                         lensec = int(data["lengthSeconds"])
                        )

    @cached_property
    def crawled(self) -> List[str]:
        yield from (
            video for page in list(self._paginate()) for video in page
        )

    def __len__(self) -> int:
        return self._len

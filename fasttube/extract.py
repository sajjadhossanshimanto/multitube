# -*- coding: utf-8 -*-
"""This module contains all non-cipher related data extraction logic."""
import json
import re
from typing import Dict, List, Tuple
from urllib.parse import parse_qs, parse_qsl

from .cipher import Cipher
from .exceptions import RegexMatchError

itag_properties={
    22:720,
    137:1080,
    135:480,
    18:360,
    133:240,
    160:144
}


def extract_video_id(url: str) -> str:
    return re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url).group(1)

def mime_type_codec(mime_type_codec: str) -> Tuple[str, List[str]]:
    """Parse the type data.

    Breaks up the data in the ``type`` key of the manifest, which contains the
    mime type and codecs serialized together, and splits them into separate
    elements.

    **Example**:

    mime_type_codec('audio/webm; codecs="opus"') -> ('audio/webm', ['opus'])

    :param str mime_type_codec:
        String containing mime type and codecs.
    :rtype: tuple
    :returns:
        The mime type and a list of codecs.

    """
    pattern = r"(\w+\/\w+)\;\scodecs=['\"]([a-zA-Z-0-9.,\s]*)['\"]"
    regex = re.compile(pattern)
    results = regex.search(mime_type_codec)
    if not results:
        raise RegexMatchError(caller="mime_type_codec", pattern=pattern)
    mime_type, codecs = results.groups()
    return mime_type, [c.strip() for c in codecs.split(",")]


def get_ytplayer_config(html: str) -> Dict:
    config_patterns = [
        r";ytplayer\.config\s*=\s*({.*?});",
        r";ytplayer\.config\s*=\s*({.+?});ytplayer",
        r";yt\.setConfig\(\{'PLAYER_CONFIG':\s*({.*})}\);",
        r";yt\.setConfig\(\{'PLAYER_CONFIG':\s*({.*})(,'EXPERIMENT_FLAGS'|;)",  # noqa: E501
    ]
    for pattern in config_patterns:
        regex = re.compile(pattern)
        function_match = regex.search(html)
        if function_match:
            yt_player_config = function_match.group(1)

            return json.loads(yt_player_config)

    raise RegexMatchError(caller="get_ytplayer_config", pattern="config_patterns")


def grabe_url_encoded_fmt(player_response: Dict) -> List:
    data_args=[]

    formats = player_response["streamingData"]["formats"]
    formats.extend(player_response["streamingData"]["adaptiveFormats"])

    try:
        data_args = [
            {
                "url": format_item["url"],
                "itag":format_item["itag"],
                "quality":itag_properties[format_item["itag"]]
            }
            for format_item in formats
            if format_item["itag"] in itag_properties
        ]
    except KeyError:# needs to sign
        cipher_url = [
            parse_qs(formats[i]["cipher"]) for i, data in enumerate(formats)
        ]
        data_args = [
            {
                "url": cipher_url[i]["url"][0],
                "s": cipher_url[i]["s"][0],
                "itag":format_item["itag"],
                "quality":itag_properties[format_item["itag"]]
            }
            for i, format_item in enumerate(formats)
            if format_item["itag"] in itag_properties
        ]

    return data_args

def apply_descrambler(stream_data: Dict, key: str) -> None:
    return [dict(parse_qsl(i)) for i in stream_data[key].split(",")]

def apply_signature(stream, js: str) -> None:
    url = stream["url"]
    signature=stream["s"]

    cipher = Cipher(js=js)
    signature = cipher.get_signature(ciphered_signature=signature)

    # 403 forbidden fix
    stream["url"] = url + "&sig=" + signature

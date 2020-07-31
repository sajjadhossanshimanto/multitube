# -*- coding: utf-8 -*-
import re

from pytube.exceptions import RegexMatchError


def safe_filename(s: str, max_length: int = 255) -> str:
    characters =[
        r"/",
        r"\\",
        r":",
        r"\*",
        r"\?",
        r'"',
        r"<",
        r">",
        r"\|",
        r"\.$"
    ]
    pattern = "|".join(characters)
    regex = re.compile(pattern, re.UNICODE)
    filename = regex.sub("", s)
    return filename[:max_length]

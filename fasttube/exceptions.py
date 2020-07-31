# -*- coding: utf-8 -*-

"""Library specific exception definitions."""
from typing import Pattern, Union


class RegexMatchError(Exception):
    """Regex pattern did not return any matches."""

    def __init__(self, caller: str, pattern: Union[str, Pattern]):
        """
        :param str caller:
            Calling function
        :param str pattern:
            Pattern that failed to match
        """
        super().__init__(f"{caller}: could not find match for {pattern}")
        self.caller = caller
        self.pattern = pattern


class VideoUnavailable(PytubeError):
    """Video is unavailable."""

    def __init__(self, video_id: str):
        """
        :param str video_id:
            A YouTube video identifier.
        """
        super().__init__(f"{video_id} is unavailable")

        self.video_id = video_id

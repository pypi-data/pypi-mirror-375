from .client import Phrappy
from .async_client import AsyncPhrappy
from ._meta import __version__
import urllib.parse


def cdh_generator(filename: str) -> str:
    """
    Takes UTF-8 filename. Returns Content Disposition value.
    """
    encoded_file_name = urllib.parse.quote(filename, encoding="utf-8")
    return f"attachment; filename*=UTF-8''{encoded_file_name}"


__all__ = ["Phrappy", "AsyncPhrappy", "cdh_generator", "__version__"]

from collections.abc import Mapping
from typing import Required, TypedDict, Unpack

from gi.repository import Gst

from optr.media.fps import FPS


def create(type: str, props: Mapping[str, object] | None = None) -> Gst.Caps:
    """Create GStreamer caps from type and properties."""
    if not props:
        return Gst.Caps.from_string(type)

    # Handle special formatting for certain properties
    formatted_props = []
    for k, v in props.items():
        key = k.replace("_", "-")
        if key == "fps" and hasattr(v, "__str__"):
            # FPS objects should be formatted as framerate
            formatted_props.append(f"framerate={v}")
        else:
            formatted_props.append(f"{key}={v}")

    fields = ",".join(formatted_props)
    return Gst.Caps.from_string(f"{type},{fields}")


class Raw(TypedDict, total=False):
    width: Required[int]
    height: Required[int]
    fps: Required[FPS]
    format: Required[str]


def raw(**props: Unpack[Raw]) -> Gst.Caps:
    """Create Gst.Caps for raw video."""
    return create("video/x-raw", props)


class RTP(TypedDict, total=False):
    media: str
    encoding_name: str
    payload: int
    clock_rate: int


def rtp(**props: Unpack[RTP]) -> Gst.Caps:
    """Create Gst.Caps for RTP video."""

    props.setdefault("media", "video")
    props.setdefault("encoding_name", "H264")
    props.setdefault("payload", 96)
    props.setdefault("clock_rate", 90000)

    return create("application/x-rtp", props)

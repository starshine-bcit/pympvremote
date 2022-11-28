from typing import Union

from pydantic import BaseModel


class PlaylistItem(BaseModel):
    plist: list[str]
    new: bool
    index: int


class StatusItem(BaseModel):
    time_pos: Union[float, None]
    percent_pos: Union[float, None]
    time_remaining: Union[float, None]
    duration: Union[float, None]
    pause: bool
    filename: Union[str, None]
    playlist_names: list[str]
    mute: bool
    fullscreen: bool
    repeat: bool
    volume: float
    playlist_pos: int


class GenericItem(BaseModel):
    message: str


class ListItem(GenericItem):
    files: list[str]
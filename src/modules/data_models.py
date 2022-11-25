from pydantic import BaseModel


class PlaylistItem(BaseModel):
    plist: list[str]
    new: bool
    index: int

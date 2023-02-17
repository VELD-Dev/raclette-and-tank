from . import types
from .stream_helper import (StreamHelper)
from . import utils


class TextureReader:
    def __init__(self, stream: StreamHelper, texture_ref: types.IGAssetRef):
        stream.seek(texture_ref.offset)
        self.ighw_header: types.IGHeader = utils.read_ighw_header(stream)
        stream.jump(0x20)
        self.ighw_chunks: list[types.IGSectionChunk] = list(utils.read_sections_chunks(self.ighw_header, stream))

        ### READ TEXTURE METADATAS ###

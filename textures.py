from . import rat_types
from .stream_helper import (StreamHelper)
from . import utils
import io
from .libs.imageio import v2 as imageio

def convert_dxt_to_png(dxt_buffer):
    # Charge l'image DXT à partir du buffer
    img = imageio.imread(dxt_buffer, 'dds')

    # Convertit l'image en PNG
    png_buffer = io.BytesIO()
    imageio.imwrite(png_buffer, img, format='png')
    png_buffer.seek(0)

    # Retourne le buffer de l'image PNG
    return png_buffer.getvalue()
class TextureReader:
    def __init__(self, stream: StreamHelper, texture_ref: rat_types.IGAssetRef):
        stream.seek(texture_ref.offset)
        self.ighw_header: rat_types.IGHeader = utils.read_ighw_header(stream)
        stream.jump(0x20)
        self.ighw_chunks: list[rat_types.IGSectionChunk] = list(utils.read_sections_chunks(self.ighw_header, stream))

        ### READ TEXTURE METADATAS ###

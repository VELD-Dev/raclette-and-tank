import io
import struct


def open_helper(stream: io.BufferedReader = None, filepath: str = None):
    if stream:
        return StreamHelper(stream)
    elif filepath:
        stream = open(filepath, 'rb')
        return StreamHelper(stream)


class StreamHelper:
    """Stream helper: put the file reader into, it will work exactly like the io.BufferedReader class type !"""
    __stream: io.BufferedReader = None
    offset = 0x0

    def __init__(self, stream):
        self.__stream = stream

    def read(self, __size: int | None = ...) -> bytes:
        self.offset += __size
        return self.__stream.read(__size)

    def seek(self, __offset: int, __whence: int = None) -> int:
        self.offset = __offset
        if __whence is not None:
            return self.__stream.seek(__offset, __whence)
        else:
            return self.__stream.seek(__offset)

    def jump(self, __size: int) -> None:
        self.seek(self.offset + __size)

    def peek(self, __size: int, __relative_offset: int = None, ) -> bytes:
        """If a value for relative offset is put, it will read data at currentoffset + relative_offset and come back to the current_offset."""
        res: bytes = bytes()
        if __relative_offset is not None:
            self.__stream.seek(self.offset + __relative_offset)
            res = self.__stream.read(__size)
        else:
            res = self.__stream.read(__size)
        self.__stream.seek(self.offset)
        return res

    def readUInt(self, __relative_offset: int = None):
        if __relative_offset is not None:
            return struct.unpack('>I', self.peek(0x04, __relative_offset))[0]
        else:
            return struct.unpack('>I', self.peek(0x04))[0]

    def readUShort(self, __relative_offset: int = None):
        if __relative_offset is not None:
            return struct.unpack('>H', self.peek(0x02, __relative_offset))[0]
        else:
            return struct.unpack('>H', self.peek(0x02))[0]

    def readULong(self, __relative_offset: int = None):
        if __relative_offset is not None:
            return struct.unpack('>Q', self.peek(0x08, __relative_offset))[0]
        else:
            return struct.unpack('>Q', self.peek(0x08))[0]

    def readFloat(self, __relative_offset: int = None):
        if __relative_offset is not None:
            return struct.unpack('>f', self.peek(0x04, __relative_offset))[0]
        else:
            return struct.unpack('>f', self.peek(0x04))[0]

    def readVector3(self, __relative_offset: int = None):
        if __relative_offset is not None:
            return struct.unpack('>3f', self.peek(0x0C, __relative_offset))
        else:
            return struct.unpack('>3f', self.peek(0x0C))

    def readUByte(self, __relative_offset: int = None):
        if __relative_offset is not None:
            return struct.unpack('>B', self.peek(0x01, __relative_offset))[0]
        else:
            return struct.unpack('>B', self.peek(0x01))[0]

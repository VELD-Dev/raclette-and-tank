import io
import math
import struct

import mathutils


def open_helper(stream: io.BufferedReader = None, filepath: str = None):
    if stream:
        return StreamHelper(stream)
    elif filepath:
        stream = open(filepath, 'rb')
        return StreamHelper(stream)


class StreamHelper:
    """Stream helper: put the file reader into, it will work exactly like the io.BufferedReader class type !"""
    __stream: io.BufferedReader = None
    offset: hex = 0x0

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

    def peek(self, __size: int, __offset: int = None, __relative: bool = True) -> bytes:
        """If a value for offset is put, it will read data at offset and come back to the previous offset.
        If a value for relative is put, it will read data at the current offset + offset and come back to the current
        offset."""
        res: bytes = bytes()
        if __offset is not None:
            if __relative is True:
                self.__stream.seek(self.offset + __offset)
                res = self.__stream.read(__size)
            else:
                self.__stream.seek(__offset)
                res = self.__stream.read(__size)
        else:
            res = self.__stream.read(__size)
        self.__stream.seek(self.offset)
        return res

    def readUInt(self, __offset: int = None, __relative: bool = True) -> int:
        if __offset is not None:
            return struct.unpack('>I', self.peek(0x04, __offset, __relative))[0]
        else:
            return struct.unpack('>I', self.peek(0x04))[0]

    def readUShort(self, __offset: int = None, __relative: bool = True) -> int:
        if __offset is not None:
            return struct.unpack('>H', self.peek(0x02, __offset, __relative))[0]
        else:
            return struct.unpack('>H', self.peek(0x02))[0]

    def readULong(self, __offset: int = None, __relative: bool = True) -> int:
        if __offset is not None:
            return struct.unpack('>Q', self.peek(0x08, __offset, __relative))[0]
        else:
            return struct.unpack('>Q', self.peek(0x08))[0]

    def readFloat32(self, __offset: int = None, __relative: bool = True) -> float:
        if __offset is not None:
            return struct.unpack('>f', self.peek(0x04, __offset, __relative))[0]
        else:
            return struct.unpack('>f', self.peek(0x04))[0]

    def readFloat16(self, __offset: int = None, __relative: bool = True) -> float:
        if __offset is not None:
            return struct.unpack('>e', self.peek(0x02, __offset, __relative))[0]
        else:
            return struct.unpack('>e', self.peek(0x02))[0]

    def readVector3Float32(self, __offset: int = None, __relative: bool = True) -> tuple[float, float, float]:
        if __offset is not None:
            return struct.unpack('>3f', self.peek(0x0C, __offset, __relative))
        else:
            return struct.unpack('>3f', self.peek(0x0C))

    def readVector3Float16(self, __offset: int = None, __relative: bool = True) -> tuple[float, float, float]:
        if __offset is not None:
            return struct.unpack('>3e', self.peek(0x06, __offset, __relative))
        else:
            return struct.unpack('>3e', self.peek(0x06))

    def readVector3Short(self, __offset: int = None, __relative: bool = True) -> tuple[int, int, int]:
        if __offset is not None:
            return struct.unpack('>3h', self.peek(0x06, __offset, __relative))
        else:
            return struct.unpack('>3h', self.peek(0x06))

    def readMatrix4x4(self, __offset: int = None, __relative: bool = True) -> mathutils.Matrix:
        fmatrix: mathutils.Matrix
        if __offset is not None:
            tuple1: tuple[float, float, float, float] = (           # Reversing the mirrored X transforms
                self.readFloat32(__offset + 0x00, __relative) * -1,
                self.readFloat32(__offset + 0x10, __relative) * -1,
                self.readFloat32(__offset + 0x20, __relative) * -1,
                self.readFloat32(__offset + 0x30, __relative) * -1
            )
            tuple2: tuple[float, float, float, float] = (           # Y pos, but use engine's Z pos, they are reversed.
                self.readFloat32(__offset + 0x08, __relative),
                self.readFloat32(__offset + 0x18, __relative),
                self.readFloat32(__offset + 0x28, __relative),
                self.readFloat32(__offset + 0x38, __relative)
            )
            tuple3: tuple[float, float, float, float] = (           # Z pos, but use engine's Y pos, they are reversed.
                self.readFloat32(__offset + 0x04, __relative),
                self.readFloat32(__offset + 0x14, __relative),
                self.readFloat32(__offset + 0x24, __relative),
                self.readFloat32(__offset + 0x34, __relative)
            )
            tuple4: tuple[float, float, float, float] = (
                self.readFloat32(__offset + 0x0C, __relative),
                self.readFloat32(__offset + 0x1C, __relative),
                self.readFloat32(__offset + 0x2C, __relative),
                self.readFloat32(__offset + 0x3C, __relative)
            )
            matrix: tuple[tuple, tuple, tuple, tuple] = (tuple1, tuple2, tuple3, tuple4)
            fmatrix = mathutils.Matrix(matrix)
        else:
            tuple1: tuple[float, float, float, float] = (
                self.readFloat32(0x00) * -1,
                self.readFloat32(0x10) * -1,
                self.readFloat32(0x20) * -1,
                self.readFloat32(0x30) * -1
            )
            tuple2: tuple[float, float, float, float] = (
                self.readFloat32(0x08),
                self.readFloat32(0x18),
                self.readFloat32(0x28),
                self.readFloat32(0x38)
            )
            tuple3: tuple[float, float, float, float] = (
                self.readFloat32(0x04),
                self.readFloat32(0x14),
                self.readFloat32(0x24),
                self.readFloat32(0x34)
            )
            tuple4: tuple[float, float, float, float] = (
                self.readFloat32(0x0C),
                self.readFloat32(0x1C),
                self.readFloat32(0x2C),
                self.readFloat32(0x3C)
            )
            matrix: tuple[tuple, tuple, tuple, tuple] = (tuple1, tuple2, tuple3, tuple4)
            fmatrix = mathutils.Matrix(matrix)
        return fmatrix

    def readUByte(self, __offset: int = None, __relative: bool = True) -> bytes:
        if __offset is not None:
            return struct.unpack('>B', self.peek(0x01, __offset, __relative))[0]
        else:
            return struct.unpack('>B', self.peek(0x01))[0]

    def readString(self, __offset: int = None, __relative: bool = True) -> str:
        if __offset is not None:
            relative_position = int()
            string = str()
            while self.peek(0x01, __offset + relative_position, __relative) != b'\x00':
                string += self.peek(0x01, __offset + relative_position, __relative).decode("ansi")
                relative_position += 0x01
            return string
        else:
            relative_position = int()
            string = str()
            while self.peek(0x01, relative_position) != b'\x00':
                string += self.peek(0x01, relative_position).decode()
                relative_position += 1
            return string

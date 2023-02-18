import mathutils


### EMPTY FOR NOW. ###

class UFrag(dict):
    """0x80 Long"""
    transformation: mathutils.Matrix
    """0x40 Long"""
    indexOffset: int
    """0x04 Long"""
    vertexOffset: int
    """0x04 Long"""
    indexCount: int
    """0x02 Long"""
    vertexCount: int
    """"0x02 Long"""
    vertices: list[tuple[float, float, float]]

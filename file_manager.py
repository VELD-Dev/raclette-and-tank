import bpy
import os
import os.path
import struct
import bpy_extras
from typing import (Any, NewType)

from .stream_helper import (StreamHelper, open_helper)


class FileManager:

    def __init__(self, folderpath: str):
        print("FileManager: INIT")
        self.folderpath = folderpath
        self.igfiles: dict[str, StreamHelper] = dict[str, StreamHelper]()
        self.otherfiles: dict[str, StreamHelper] = dict[str, StreamHelper]()
        self.isIE2: bool = bool()
        self.loadfolder()

    def loadfolder(self):
        files = [f for f in os.listdir(self.folderpath) if os.path.isfile(os.path.join(self.folderpath, f))]
        self.isIE2 = files.count("main.dat") > 0

        if self.isIE2 is True:
            return  # For now, we'll just ignore the IE 2.0 versions.
            # Loads IGFiles
            self.loadfile("main.dat", True)
            self.loadfile("vertices.dat", True)
            self.loadfile("gameplay.dat", True)
            try:
                self.loadfile("debug.dat", True)
            except IOError as err:
                print(err.args)

            # Load other files which are also IGFiles but are not "main"
            self.loadfile("textures.dat", False)
            self.loadfile("texstream.dat", False)
        else:

            # Loads IGFiles
            self.loadfile("assetlookup.dat", True)
            self.loadfile("gameplay.dat", True)

            # Loads other files which are also IGFiles but are not "main"
            self.loadfile("mobys.dat", False)
            self.loadfile("ties.dat", False)
            self.loadfile("textures.dat", False)
            self.loadfile("highmips.dat", False)
            self.loadfile("shaders.dat", False)
            self.loadfile("zones.dat", False)

    def loadfile(self, name: str, readAsIGFiles: bool):
        if not os.path.exists(os.path.join(self.folderpath, name)):
            raise IOError("FileManager: File {0} in folderpath {1} does not exist.".format(name, self.folderpath), name,
                          self.folderpath)

        stream = open(os.path.join(self.folderpath, name), 'rb')

        if readAsIGFiles is True:
            stream.seek(0x00)  # Set position to 0 in the buffer
            self.igfiles[name] = open_helper(stream)
        else:
            stream.seek(0x00)  # Set position to 0 in the buffer
            self.otherfiles[name] = open_helper(stream)

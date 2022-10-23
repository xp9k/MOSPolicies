from PyQt6 import uic
import os

folderToConvert = os.path.abspath('.')
uic.compileUiDir(folderToConvert, recurse=False)
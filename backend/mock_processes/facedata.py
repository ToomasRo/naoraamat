from ast import Tuple
from dataclasses import dataclass
from pathlib import Path
import numpy as np

@dataclass
class Face:
    rect:list[Tuple]
    imgpath:str|Path
    face_chip:np.ndarray
    embeddings:list[float]


    
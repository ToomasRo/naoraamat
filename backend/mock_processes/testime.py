import os

import pickle
import dlib

import cv2




def directory_traversal(path):
    for root, dirs, files in os.walk(path):
        yield root, files

    ...


for i in directory_traversal("data/pildid"):
    print(i)
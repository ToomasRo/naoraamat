#!/usr/bin/python
import cv2
import sys

import dlib

# if len(sys.argv) != 3:
#     print(
#         "Call this program like this:\n"
#         "   ./face_alignment.py shape_predictor_5_face_landmarks.dat ../examples/faces/bald_guys.jpg\n"
#         "You can download a trained facial shape predictor from:\n"
#         "    http://dlib.net/files/shape_predictor_5_face_landmarks.dat.bz2\n")
#     exit()

predictor_path = "models/shape_predictor_5_face_landmarks.dat" # sys.argv[1]
face_file_path = "/home/atlantis/Documents/Project/python_proge/selti_naoraamat/backend/data/pildid/testheino/_resized/tere.jpg" #sys.argv[2]

# Load all the models we need: a detector to find the faces, a shape predictor
# to find face landmarks so we can precisely localize the face
detector = dlib.get_frontal_face_detector()
sp = dlib.shape_predictor(predictor_path)

# Load the image using Dlib
img = dlib.load_rgb_image(face_file_path)

# Ask the detector to find the bounding boxes of each face. The 1 in the
# second argument indicates that we should upsample the image 1 time. This
# will make everything bigger and allow us to detect more faces.
dets = detector(img, 1)

num_faces = len(dets)
if num_faces == 0:
    print("Sorry, there were no faces found in '{}'".format(face_file_path))
    exit()

# Find the 5 face landmarks we need to do the alignment.
faces = dlib.full_object_detections()
for detection in dets:
    faces.append(sp(img, detection))


# cv2.namedWindow("asi") 

# cv2.imshow("asi", "/home/atlantis/Documents/Project/python_proge/selti_naoraamat/backend/data/pildid/testheino/_resized/tere.jpg")
# window = dlib.image_window("asi")

# Get the aligned face images
# Optionally: 
# images = dlib.get_face_chips(img, faces, size=160, padding=0.25)
images = dlib.get_face_chips(img, faces, size=320)
for image in images:
    # print(image)
    print("nägu")
    # cv2.imshow("asi", image)
    # window.set_image(image)
    # dlib.hit_enter_to_continue()

# It is also possible to get a single chip
image = dlib.get_face_chip(img, faces[0])
# window.set_image(image)
# dlib.hit_enter_to_continue()


dlib.save_face_chip(img, images, "/home/atlantis/Documents/Project/python_proge/selti_naoraamat/backend/temp/nagu.jpg", size=150, padding=0.25)


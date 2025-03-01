from scipy.spatial import KDTree
from scipy.spatial.distance import euclidean, cosine 
import os 
import pickle
import cv2
import dlib

PICKLES = "/home/atlantis/Documents/Project/python_proge/selti_naoraamat/backend/temp/pickles"
VURRUD = "/home/atlantis/Documents/Project/python_proge/selti_naoraamat/backend/temp/vurrud"

if not os.path.exists(VURRUD):
    os.mkdir(VURRUD)

embeds = []
facedatas = []

for pckl in os.listdir(PICKLES):
    with open(os.path.join(PICKLES, pckl), "rb") as f:
        asi = pickle.load(f)
    facedatas.append(asi)
    embeds.append(asi.embeddings)




vurrud = dlib.chinese_whispers_clustering(embeds, 0.54)
labelcounter = {}
for idx, label in enumerate(vurrud):
    print(idx)
    labelfolder = os.path.join(VURRUD, str(label))
    if not os.path.exists(labelfolder):
        os.mkdir(labelfolder)
        labelcounter[label] = 0
    if label in labelcounter:
        labelcounter[label] += 1
    else:
        labelcounter[label] = 0
    
    pilt = cv2.imread(facedatas[idx].imgpath)
    x1 = int(facedatas[idx].rect.tl_corner().x)
    y1 = int(facedatas[idx].rect.tl_corner().y)

    x2 = int(facedatas[idx].rect.br_corner().x)
    y2 = int(facedatas[idx].rect.br_corner().y)
    cv2.rectangle(pilt, (x1,y1), (x2,y2),  (0,0,255))

    cv2.imwrite(os.path.join(labelfolder, str(labelcounter[label])+".jpg"), 
                cv2.cvtColor(facedatas[idx].face_chip, cv2.COLOR_BGR2RGB))
    
    cv2.imwrite(os.path.join(labelfolder, str(labelcounter[label])+"_full.jpg"),  pilt)
    

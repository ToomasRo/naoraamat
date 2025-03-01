import pickle
import os
import pyperclip


INPUT_DIR = "/home/atlantis/Documents/Project/python_proge/selti_naoraamat/backend/temp/pickles"

nimi = input("sisesta nimi: ")

with open(os.path.join(INPUT_DIR, nimi), "rb") as f:
    objekt = pickle.load(f)

print(objekt.rect)
print(objekt.imgpath)

parem = f"[{','.join(map(str, objekt.embeddings))}]"
pyperclip.copy(parem)

# 2W6A6137.JPG_0 oliver
# 2W6A9421.jpg_0
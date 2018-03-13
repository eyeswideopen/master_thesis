from subprocess import call
import os
from PIL import Image
import numpy as np
from operator import itemgetter
import shutil
from tqdm import tqdm
import time

inputFolder = os.path.join(os.path.dirname(__file__), './input')
outputFolder = os.path.join(os.path.dirname(__file__), './output')
images = [f for f in sorted(os.listdir(inputFolder)) if "DS_Store" not in f]


for image in images:
    im = Image.open(os.path.join(inputFolder, image))
    im = im.convert('L')

    data = np.array(im)
    data[data == 150] = 1
    data[data == 255] = 2
    im = Image.fromarray(data)
    im.save(os.path.join(outputFolder, image), "png")

print("conversion finished")
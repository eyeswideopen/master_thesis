#converts the files from input in the format 0 background, 1 liver, 2 tumor
#into a visible segmentation with grey as liver and white as tumor

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
    data = np.array(im)
    data[data == 1] = 150
    data[data == 2] = 255
    im = Image.fromarray(data)
    im = im.convert('RGB')
    im.save(os.path.join(outputFolder, image), "png")

print("conversion finished")
#this script converts regular segmentations used for the GAN (0 = background, 1 = liver, 2 = tumor)
# to segmentations with tumor class only

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


for image in tqdm(images):
    im = Image.open(os.path.join(inputFolder, image))
    im = im.convert('L')

    data = np.array(im)
    #remove liver class
    data[data == 1] = 0

    im = Image.fromarray(data)
    im.save(os.path.join(outputFolder, image), "png")

print("conversion finished!")
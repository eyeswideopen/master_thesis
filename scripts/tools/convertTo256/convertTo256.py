#converts 512x512 (or any square images) to 256 x 256

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


segmentations = [f for f in sorted(os.listdir(inputFolder)) if "DS_Store" not in f and "seg" in f]
images = [f for f in sorted(os.listdir(inputFolder)) if "DS_Store" not in f and "vol" in f]


print("scaling segmentations with nearest neighbour")
for file in tqdm(segmentations):
    im = Image.open(os.path.join(inputFolder, file))
    im = im.resize((256,256), Image.NEAREST);
    im.save(os.path.join(outputFolder, file))


print("scaling slices with nearest neighbour")
for file in tqdm(images):
    im = Image.open(os.path.join(inputFolder, file))
    im = im.resize((256,256));
    im.save(os.path.join(outputFolder, file))

print("conversion finished")
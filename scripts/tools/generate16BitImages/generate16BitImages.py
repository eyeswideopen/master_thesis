from subprocess import call
import os
from PIL import Image
import numpy as np
from operator import itemgetter
import shutil
import time

outputFolder = os.path.join(os.path.dirname(__file__), './output')


for i in range(10):

    image = np.random.randint(4095, size=(512, 512))
    im = Image.fromarray(image)
    im.save(os.path.join(outputFolder, str(i)), "png")

print("conversion finished")
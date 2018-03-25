from subprocess import call
import os
from PIL import Image
import numpy as np
from operator import itemgetter
import shutil
from tqdm import tqdm
import time

useTestData = False

if useTestData:
    inputFolder = os.path.join(os.path.dirname(__file__), '../../../../data/test/rawSlices/')
    outputFolder = os.path.join(os.path.dirname(__file__), './output')
else:
    inputFolder = os.path.join(os.path.dirname(__file__), '../../../../data/train/rawSlices/')
    outputFolder = os.path.join(os.path.dirname(__file__), './output')


volumeSlices = [f for f in sorted(os.listdir(inputFolder)) if os.path.isfile(
    os.path.join(inputFolder, f)) and "volume" in f]
segmentationSlices = [f for f in sorted(os.listdir(inputFolder)) if os.path.isfile(
    os.path.join(inputFolder, f)) and "segmentation" in f]

# tuple of segmentation/volume slice
sliceTupelList = list(zip(segmentationSlices, volumeSlices))

# dict to store the volumes with the mirrored slices
mirroredVolumes = {}

#process each seg/vol slice pair together
sliceIndex = 0
currentVolume = '';


volumeFinished = False


for imageTuple in tqdm(sliceTupelList):

    #check if new volume. if so -> reset slice index
    if currentVolume != imageTuple[0].split('_')[0]:
        currentVolume = imageTuple[0].split('_')[0];
        volumeFinished = False
        sliceIndex = 0

    #
    # SEGMENTATION
    #

    if volumeFinished:
        continue

    # skip tuple if segmentation is empty
    sliceIndex += 1

    im = Image.open(os.path.join(inputFolder, imageTuple[0]))
    if not im.convert('RGB').getbbox():
        continue

    print("saving volume " + str(imageTuple[1].split('_')[0]) + " slices " + str(sliceIndex))
    im.save(os.path.join(outputFolder, imageTuple[0].split('_')[0] + '_' + str(sliceIndex) + '_' + 'seg.png'), "png")
    im = Image.open(os.path.join(inputFolder, imageTuple[1]))
    im.save(os.path.join(outputFolder, imageTuple[1].split('_')[0] + '_' + str(sliceIndex) + '_' + 'vol.png'), "png")
    volumeFinished = True;

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
    inputFolder = os.path.join(os.path.dirname(__file__), '../../data/test/rawSlices/')
    outputFolder = os.path.join(os.path.dirname(__file__), '../../data/test/flipped/')
else:
    inputFolder = os.path.join(os.path.dirname(__file__), '../../data/train/rawSlices/')
    outputFolder = os.path.join(os.path.dirname(__file__), '../../data/train/flipped/')


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

leftSum = 0;
rightSum = 0;


for imageTuple in tqdm(sliceTupelList):

    #check if new volume. if so -> reset slice index
    if currentVolume != imageTuple[0].split('_')[0]:

        if rightSum > leftSum:
            print(currentVolume + " should be flipped!")

        sliceIndex = 0
        leftSum = 0;
        rightSum = 0;

        currentVolume = imageTuple[0].split('_')[0];



    #
    # SEGMENTATION
    #

    # skip tuple if segmentation is empty
    im = Image.open(os.path.join(inputFolder, imageTuple[0]))
    if not im.convert('RGB').getbbox():
        continue

    # convert to greyscale 1 channel image
    im = im.convert('L')
    data = np.array(im)

    #check if volume is flipped. If so -> rotate segmentation and volume by 180
    #now all slices should have the liver on the left side
    leftHalf, rightHalf = np.hsplit(data, 2)
    leftSum += np.sum(leftHalf)
    rightSum += np.sum(rightHalf)

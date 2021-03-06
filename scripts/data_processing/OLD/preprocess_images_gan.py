# this script preprocesses the raw slices from the input folder to be used as data for the u-net

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
    inputFolder = os.path.join(os.path.dirname(
        __file__), '../../data/test/rawSlices/')
    outputFolder = os.path.join(os.path.dirname(
        __file__), '../../data/test/gan/')
else:
    inputFolder = os.path.join(os.path.dirname(
        __file__), '../../data/train/rawSlices/')
    outputFolder = os.path.join(os.path.dirname(
        __file__), '../../data/train/gan/')


volumeSlices = [f for f in sorted(os.listdir(inputFolder)) if os.path.isfile(
    os.path.join(inputFolder, f)) and "volume" in f]
segmentationSlices = [f for f in sorted(os.listdir(inputFolder)) if os.path.isfile(
    os.path.join(inputFolder, f)) and "segmentation" in f]

# tuple of segmentation/volume slice
sliceTupelList = list(zip(segmentationSlices, volumeSlices))


#
# FIND LEFT RIGHT FLIPPED VOLUMES
#

leftSum = 0
rightSum = 0
sliceIndex = 0
currentVolume = ''
volumesToFlipLR = []

print("Searching for horizontal flipped volumes ...")
for imageTuple in tqdm(sliceTupelList):
    # check if new volume. if so -> reset slice index
    if currentVolume != imageTuple[0].split('_')[0]:

        if rightSum > leftSum:
            volumesToFlipLR.append(currentVolume)

        sliceIndex = 0
        leftSum = 0
        rightSum = 0

        currentVolume = imageTuple[0].split('_')[0]

    # skip volumes which should be ignored
    # add volumes from test data to ignore here
    if useTestData and int(currentVolume) == 59:
        continue

    # skip tuple if segmentation is empty
    im = Image.open(os.path.join(inputFolder, imageTuple[0]))

    # convert to greyscale 1 channel image
    im = im.convert('L')

    colors = im.getcolors()
    # skip tuple if segmentation is empty
    if len(colors) == 1:
        continue

    data = np.array(im)
    data[data == 150] = 255
    # sum lefthalf and righthalf to check which side the liver is on
    leftHalf, rightHalf = np.hsplit(data, 2)
    leftSum += np.sum(leftHalf)
    rightSum += np.sum(rightHalf)

# finalize list for faster access
volumesToFlipLR = frozenset(volumesToFlipLR)


#
# PROCESS SEGMENTATION VOLUME SLICE PAIRS
#

# dicts to store the volumes with the flipped slices on both axis
flippedUDVolumes = {}
flippedLRVolumes = {}

# process each seg/vol slice pair together
sliceIndex = 0
currentVolume = ''
print("Processing image data ...")
for imageTuple in tqdm(sliceTupelList):

    # check if new volume. if so -> reset slice index
    if currentVolume != imageTuple[0].split('_')[0]:
        currentVolume = imageTuple[0].split('_')[0]
        sliceIndex = 0

    #
    # SEGMENTATION
    #

    # skip volumes which should be ignored
    # add volumes from test data to ignore here
    if useTestData and int(currentVolume) == 59:
        continue

    im = Image.open(os.path.join(inputFolder, imageTuple[0]))

    # print warning if image size differs from 512x512
    if not im.size == (512, 512):
        print("WARNING!! Image size is not 512x512 for " + imageTuple[0])
        continue

    # convert to greyscale 1 channel image
    im = im.convert('L')
    colors = im.getcolors()

    # skip tuple if segmentation is empty
    if len(colors) == 1:
        continue


    data = np.array(im)

    # FLIPPING

    # check if Volume must be flipped on the horizontal axis (up down)
    # volumes to be flipped: 53 - 67 and 83 - 130
    vol = int(currentVolume)
    if useTestData:
        flipUD = (vol >= 5 and vol <= 14) or (vol >= 30 and vol <= 41)
    else:
        flipUD = (vol >= 53 and vol <= 67) or (vol >= 83 and vol <= 130)

    # flip up down if indicated
    if flipUD:
        # save the filename to the dict for later output
        if currentVolume not in flippedUDVolumes:
            flippedUDVolumes[currentVolume] = 0
        flippedUDVolumes[currentVolume] = flippedUDVolumes[currentVolume] + 1

        data = np.flipud(data)

    # flip left right if indicated
    flipLR = currentVolume in volumesToFlipLR
    if flipLR:
        # save the filename to the dict for later output
        if currentVolume not in flippedLRVolumes:
            flippedLRVolumes[currentVolume] = 0
        flippedLRVolumes[currentVolume] = flippedLRVolumes[currentVolume] + 1

        # mirror the slice horizontally
        data = np.fliplr(data)


    # COLOR CORRECTION

    # replace class colors
    # classes are:
    # 0 Background
    # 1 Liver
    # 2 Tumor
    # if only 2 colors are present: no tumor visible -> switch liver (now 255) to 1
    if len(colors) == 2:
        data[data == 255] = 1

    # if 3 colors are visible the liver color (now 150) is switched to 1 and tumor (now 255) is switched to 2
    if len(colors) == 3:
        data[data == 150] = 1
        data[data == 255] = 2


    # SAVE SEGMENTATION
    im = Image.fromarray(data)
    im.save(os.path.join(outputFolder, imageTuple[0].split('_')[
            0] + '_' + str(sliceIndex) + '_label.png'), "png")

    #
    # VOLUME
    #

    im = Image.open(os.path.join(inputFolder, imageTuple[1]))
    im = im.convert('RGB')  # strip alpha channel

    # FLIPPING
    if flipLR:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if flipUD:
        im = im.transpose(Image.FLIP_TOP_BOTTOM)

    # SAVE IMAGE
    im.save(os.path.join(outputFolder, imageTuple[1].split('_')[
            0] + '_' + str(sliceIndex) + '_image.png'), "png")
    sliceIndex += 1


#
# FINISHED
#

print("Data preprocessing finished!")
print("\n")
print("LEFT RIGHT FLIPPED VOLUMES:")

for key in flippedLRVolumes:
    print("Flipped left-right Volume: " + key + " with " +
          str(flippedLRVolumes[key]) + " slices")

print("\n")
print("UP DOWN FLIPPED VOLUMES:")
for key in flippedUDVolumes:
    print("Flipped up-down Volume: " + key + " with " +
          str(flippedUDVolumes[key]) + " slices")

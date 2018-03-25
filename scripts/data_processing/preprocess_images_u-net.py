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
        __file__), '../../data/test/u-net/')
else:
    inputFolder = os.path.join(os.path.dirname(
        __file__), '../../data/train/rawSlices/')
    outputFolder = os.path.join(os.path.dirname(
        __file__), '../../data/train/u-net/')


volumeSlices = [f for f in sorted(os.listdir(inputFolder)) if os.path.isfile(
    os.path.join(inputFolder, f)) and "volume" in f]
segmentationSlices = [f for f in sorted(os.listdir(inputFolder)) if os.path.isfile(
    os.path.join(inputFolder, f)) and "segmentation" in f]

# tuple of segmentation/volume slice
sliceTupelList = list(zip(segmentationSlices, volumeSlices))


# dict to store the volumes with the mirrored slices
mirroredVolumes = {}

# process each seg/vol slice pair together
sliceIndex = 0
currentVolume = ''
for imageTuple in tqdm(sliceTupelList):

    # check if new volume. if so -> reset slice index
    if currentVolume != imageTuple[0].split('_')[0]:
        currentVolume = imageTuple[0].split('_')[0]
        sliceIndex = 0

    #
    # SEGMENTATION
    #

    # skip tuple if segmentation is empty
    im = Image.open(os.path.join(inputFolder, imageTuple[0]))
    if not im.convert('RGB').getbbox():
        continue

    # print warning if image size differs from 512x512
    if not im.size == (512, 512):
        print("WARNING!! Image size is not 512x512 for " + imageTuple[0])
        continue

    # convert to greyscale 1 channel image
    im = im.convert('L')
    colors = im.getcolors()
    data = np.array(im)

    # if 3 colors present switch all tumors to liver class (from 150 to 255)
    if len(colors) == 3:
        data[data == 150] = 255
        im = Image.fromarray(data)

    # check if volume is flipped. If so -> rotate segmentation and volume by 180
    # now all slices should have the liver on the left side
    leftHalf, rightHalf = np.hsplit(data, 2)
    mirror = np.sum(rightHalf) >= np.sum(leftHalf)

    # mirror if neccessary
    if mirror:
        # save the filename to the dict for later output
        if currentVolume not in mirroredVolumes:
            mirroredVolumes[currentVolume] = []
        mirroredVolumes[currentVolume].push(
            imageTuple[0].split('_')[0] + '_' + str(sliceIndex))

        # mirror the slice horizontally
        data = np.fliplr(data)

    im.save(os.path.join(outputFolder, imageTuple[0].split('_')[
            0] + '_' + str(sliceIndex) + '_label.png'), "png")

    #
    # VOLUME
    #

    im = Image.open(os.path.join(inputFolder, imageTuple[1]))
    im = im.convert('RGB')  # strip alpha channel

    # rotate as well if seg was rotated
    if mirror:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)

    im.save(os.path.join(outputFolder, imageTuple[1].split('_')[
            0] + '_' + str(sliceIndex) + '_image.png'), "png")
    sliceIndex += 1


#
# FINISHED
#

print("Data preprocessing finished!")

for key in mirroredVolumes:
    print("mirrored Volume: " + key)
    print("number of slices: " + len(mirroredVolumes[key]))
    print(mirroredVolumes[key])
    print("\n")

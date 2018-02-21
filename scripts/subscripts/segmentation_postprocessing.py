from subprocess import call
import os
from PIL import Image
import numpy as np
from medpy.io import load
from medpy.io import save
from operator import itemgetter
import shutil

rawFolder = os.path.join(os.path.dirname(__file__), '../../data/raw/')
pngFolder = os.path.join(os.path.dirname(__file__), '../../data/png/')
jpgFolder = os.path.join(os.path.dirname(__file__), '../../data/jpg/')
tmpFolder = os.path.join(os.path.dirname(__file__), '../../data/tmp/')

segmentations = [f for f in sorted(os.listdir(jpgFolder)) if "seg" in f]

print("found " + str(len(segmentations)) + " segmentation slices. processing...")


# data = np.array(Image.open(os.path.join(jpgFolder, segmentations[0])))
# print(data)






#loop over segmentation/volume pairs to export PNGs
for segmentation in segmentations:

    im = Image.open(os.path.join(jpgFolder, segmentation))
    colors = im.getcolors()
    data = np.array(im)

    #classes are:
    # [0,0,0] Background
    # [1,1,1] Liver
    # [2,2,2] Tumor

    #if only 2 colors are present: no tumor visible -> switch liver (now white) to [1,1,1]
    if len(colors) == 2:
        r1, g1, b1 = 255, 255, 255  # Original value
        # r2, g2, b2 = 1, 1, 1  # Value that we want to replace it with
        r2, g2, b2 = 100, 0, 0  # Value that we want to replace it with

        red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data[:, :, :3][mask] = [r2, g2, b2]

        im = Image.fromarray(data)
        im.save(os.path.join(jpgFolder, "NEW_" + segmentation))

    #if 3 colors are visible the liver color (now grey) is switched to [1,1,1] and tumor (now white) is switched to [2,2,2]
    if len(colors) == 3:
        #liver color switch
        r1, g1, b1 = 150, 150, 150  # Original value
        # r2, g2, b2 = 1, 1, 1  # Value that we want to replace it with
        r2, g2, b2 = 100, 0, 0  # Value that we want to replace it with

        red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data[:, :, :3][mask] = [r2, g2, b2]

        #tumor color switch
        r1, g1, b1 = 255, 255, 255  # Original value
        # r2, g2, b2 = 1, 1, 1  # Value that we want to replace it with
        r2, g2, b2 = 0, 100, 0  # Value that we want to replace it with

        red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
        mask = (red == r1) & (green == g1) & (blue == b1)
        data[:, :, :3][mask] = [r2, g2, b2]

        im = Image.fromarray(data)
        im.save(os.path.join(jpgFolder, "NEW_" + segmentation))


# #
# #ALL SLICES CREATED -> CALCULATE MINIMUM POSSIBLE BOUNDING BOX
# #
#
# #segmentation/volume pair is normalized and saved as pngs -> calculate bounding boxes on segmentations, crop PNGs and save to final folder as JPG
# volumeSlices = [f for f in sorted(os.listdir(pngFolder)) if os.path.isfile(os.path.join(pngFolder, f)) and "volume" in f]
# segmentationSlices = [f for f in sorted(os.listdir(pngFolder)) if os.path.isfile(os.path.join(pngFolder, f)) and "segmentation" in f]
#
# # tuple of segmentation/volume slice
# sliceTupelList = list(zip(segmentationSlices, volumeSlices))
#
# boundingBoxes = [] #list of all bounding boxes of all segmentations
#
# print("Calculating bounding box for each slice...")
# #reverse loop over PNG segmentations and save all bounding boxes
# for i, slice in reversed(list(enumerate(segmentationSlices))):
#     im = Image.open(os.path.join(pngFolder, slice))
#     currentBox = im.convert('RGB').getbbox()#convert to rgb since getbbox doesn't work with pngs with alpha channel
#     #if no bounding box is present we don't have a segmentation -> del the seg/vol pair from our tupel list for later cropping
#     if not currentBox:
#         del sliceTupelList[i]
#     else:
#         boundingBoxes.append(currentBox)
#
# #calculate minimum possible bounding box from all segs
# print("Calculating minimum possible bounding box for all slices...")
# finalBoundingBox = [min(boundingBoxes,key=itemgetter(0))[0], min(boundingBoxes,key=itemgetter(1))[1], max(boundingBoxes,key=itemgetter(2))[2], max(boundingBoxes,key=itemgetter(3))[3]]
#
# #crop images accordingly and save to final filder
# print("Cropping and converting slices to calculated bounding box...")
# volumeNumber = 0
# sliceIndex = 0
#
# for imageTuple in sliceTupelList:
#     for image in imageTuple:
#
#         #reset slice index when next volume/segmentation pair is reached
#         if volumeNumber != image.split('_')[0]:
#             volumeNumber = image.split('_')[0]
#             sliceIndex = 0
#
#         im = Image.open(os.path.join(pngFolder, image)).convert('RGB')
#
#         #crop rename and save image. name format is <volume number>_<volume slice number>_<'seg' or 'vol'>.jpeg
#         im.crop(finalBoundingBox).save(os.path.join(jpgFolder, image.split('_')[0] + '_' + str(sliceIndex) + '_' + ('seg' if image.find('segmentation') != -1 else 'vol') + '.jpeg'), "jpeg")
#     sliceIndex += 1
#
# #finally delete intermediate pngs
# print("Data preprocessing finished!")
# shutil.rmtree(pngFolder)
# os.makedirs(pngFolder)
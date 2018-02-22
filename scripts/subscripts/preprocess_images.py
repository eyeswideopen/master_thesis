from subprocess import call
import os
from PIL import Image
import numpy as np
from operator import itemgetter
import shutil
from tqdm import tqdm


inputFolder = os.path.join(os.path.dirname(__file__), '../../data/rawSlices/')
outputFolder = os.path.join(os.path.dirname(__file__), '../../data/output/')

#
#ALL SLICES CREATED -> CALCULATE MINIMUM POSSIBLE BOUNDING BOX
#

#segmentation/volume pair is normalized and saved as pngs -> calculate bounding boxes on segmentations, crop PNGs and save to final folder as JPG
volumeSlices = [f for f in sorted(os.listdir(inputFolder)) if os.path.isfile(os.path.join(inputFolder, f)) and "volume" in f]
segmentationSlices = [f for f in sorted(os.listdir(inputFolder)) if os.path.isfile(os.path.join(inputFolder, f)) and "segmentation" in f]

# tuple of segmentation/volume slice
sliceTupelList = list(zip(segmentationSlices, volumeSlices))

# boundingBoxes = [] #list of all bounding boxes of all segmentations
#
# print("Calculating bounding box for each slice...")
#reverse loop over PNG segmentations and save all bounding boxes
# for i, slice in reversed(list(enumerate(tqdm(segmentationSlices)))):
#     im = Image.open(os.path.join(inputFolder, slice))
#     currentBox = im.convert('RGB').getbbox()#convert to rgb since getbbox doesn't work with pngs with alpha channel
#     #if no bounding box is present we don't have a segmentation -> del the seg/vol pair from our tupel list for later cropping
#     if not currentBox:
#         del sliceTupelList[i]
#     else:
#         boundingBoxes.append(currentBox)
#
#calculate minimum possible bounding box from all segs
# print("Calculating minimum possible bounding box for all slices...")
# finalBoundingBox = [min(boundingBoxes,key=itemgetter(0))[0], min(boundingBoxes,key=itemgetter(1))[1], max(boundingBoxes,key=itemgetter(2))[2], max(boundingBoxes,key=itemgetter(3))[3]]
#
# print("minimum bounding box: " + str(finalBoundingBox))
# #check if final bounding box is divisibale by 2 on every dimension
# if (finalBoundingBox[2] - finalBoundingBox[0])%2==1:
#     finalBoundingBox[2] = finalBoundingBox[2]-1
#     print("boundingBox width corrected to be divisible by 2 to: " + str(finalBoundingBox[2]-finalBoundingBox[0]))
#
# if (finalBoundingBox[3] - finalBoundingBox[1])%2==1:
#     finalBoundingBox[3] = finalBoundingBox[3]-1
# print("boundingBox height corrected to be divisible by 2 to: " + str(finalBoundingBox[3] - finalBoundingBox[1]))


#crop images accordingly and save to final filder
print("Cropping and converting slices to calculated bounding box...")
volumeNumber = 0
sliceIndex = 0

for imageTuple in tqdm(sliceTupelList):
    for image in imageTuple:




        #reset slice index when next volume/segmentation pair is reached
        if volumeNumber != image.split('_')[0]:
            volumeNumber = image.split('_')[0]
            sliceIndex = 0

        #open image
        im = Image.open(os.path.join(inputFolder, image))

        #print warning if image size differs from 512x512
        if not im.size == (512, 512):
            print("WARNING!! Image size is not 512x512 for " + image)

        #crop rename and save image. name format is <volume number>_<volume slice number>_<'seg' or 'vol'>.jpeg
        # im = im.crop(finalBoundingBox)

        #image postprocessing
        if image.find('volume') > 0:
            im = im.convert('RGB')


        #segmentation postprocessing (switching of color values to single channel 0,1,2 ... N-1 class labels
        if image.find('segmentation') > 0:
            #convert to greyscale 1 channel image
            im = im.convert('L')
            colors = im.getcolors()
            data = np.array(im)



            #replace class colors
            # classes are:
            # 0 Background
            # 1 Liver
            # if only 2 colors are present: no tumor visible -> switch liver (now 255) to 1
            if len(colors) == 2:
                data[data == 255] = 1
                im = Image.fromarray(data)

            # if 3 colors are visible the liver color (now 150) is switched to 1 and tumor (now 255) is switched to 2
            if len(colors) == 3:
                data[data == 150] = 1
                data[data == 255] = 2
                im = Image.fromarray(data)

        im.save(os.path.join(outputFolder, image.split('_')[0] + '_' + str(sliceIndex) + '_' + ('seg' if image.find('segmentation') != -1 else 'vol') + '.png'), "png")

    sliceIndex += 1

#finally delete intermediate pngs
print("Data preprocessing finished!")
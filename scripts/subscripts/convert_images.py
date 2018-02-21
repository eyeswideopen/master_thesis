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
outputFolder = os.path.join(os.path.dirname(__file__), '../../data/output/')
tmpFolder = os.path.join(os.path.dirname(__file__), '../../data/tmp/')

volumes = [f for f in sorted(os.listdir(rawFolder)) if os.path.isfile(os.path.join(rawFolder, f)) and "volume" in f]
segmentations = [f for f in sorted(os.listdir(rawFolder)) if os.path.isfile(os.path.join(rawFolder, f)) and "segmentation" in f]


# import pickle
# from medpy.filter import IntensityRangeStandardization
#normalization with intensity range standardization (UNFINISHED/EXPERIMENTAL)
# irs = IntensityRangeStandardization()
# volumeImages = [load(os.path.join(os.path.dirname(__file__), '../../data/raw/' + file))[0] for file in volumes]
# print(volumeImages)
# if os.path.isfile('intensity_model.pkl'):
#     with open('intensity_model.pkl', 'r') as f:
#         irs = pickle.load(f)
# trained_model, transformed_images = irs.train_transform(volumeImages)


volumeTupel = list(zip(segmentations,volumes));


#
#EXTRACT PNG SLICES FOR ALL VOLUMES AND SEGMENTATIONS
#

#loop over segmentation/volume pairs to export PNGs
for fileTuple in volumeTupel:
    for file in fileTuple:

        print(file)

        #get filtype (seg/volume) and the number of it
        fileType, number = os.path.splitext(file)[0].split('-')


        #normalize volumes
        if fileType == 'volume':

            #
            # !! IMAGE PREPROCESSING !!
            #

            #currently only normalization is done but additional steps can be taken here on each volume
            print("Normalizing volume: " + file + " with STANDARD DEVIATION")
            image_data, image_header = load(os.path.join(rawFolder, file))
            image_data = (image_data-np.mean(image_data))/np.std(image_data)
            save(image_data,os.path.join(tmpFolder, file),image_header)
            sourceFolder = tmpFolder
        else:
            #set source to raw segmentation because no copying/normalization is done on them
            # shutil.copyfile(os.path.join(rawFolder, file), os.path.join(tmpFolder, file))
            sourceFolder = rawFolder

        # convert it to PNGs
        call([
            "med2image",
            "-i", os.path.join(sourceFolder,file),
            "-d", pngFolder,
            "-t", "png",
            "-o", number + "_" + fileType
            ])

        #clear tmp folder for next volume
        shutil.rmtree(tmpFolder)
        os.makedirs(tmpFolder)


#
#ALL SLICES CREATED -> CALCULATE MINIMUM POSSIBLE BOUNDING BOX
#

#segmentation/volume pair is normalized and saved as pngs -> calculate bounding boxes on segmentations, crop PNGs and save to final folder as JPG
volumeSlices = [f for f in sorted(os.listdir(pngFolder)) if os.path.isfile(os.path.join(pngFolder, f)) and "volume" in f]
segmentationSlices = [f for f in sorted(os.listdir(pngFolder)) if os.path.isfile(os.path.join(pngFolder, f)) and "segmentation" in f]

# tuple of segmentation/volume slice
sliceTupelList = list(zip(segmentationSlices, volumeSlices))

boundingBoxes = [] #list of all bounding boxes of all segmentations

print("Calculating bounding box for each slice...")
#reverse loop over PNG segmentations and save all bounding boxes
for i, slice in reversed(list(enumerate(segmentationSlices))):
    im = Image.open(os.path.join(pngFolder, slice))
    currentBox = im.convert('RGB').getbbox()#convert to rgb since getbbox doesn't work with pngs with alpha channel
    #if no bounding box is present we don't have a segmentation -> del the seg/vol pair from our tupel list for later cropping
    if not currentBox:
        del sliceTupelList[i]
    else:
        boundingBoxes.append(currentBox)

#calculate minimum possible bounding box from all segs
print("Calculating minimum possible bounding box for all slices...")
finalBoundingBox = [min(boundingBoxes,key=itemgetter(0))[0], min(boundingBoxes,key=itemgetter(1))[1], max(boundingBoxes,key=itemgetter(2))[2], max(boundingBoxes,key=itemgetter(3))[3]]

#crop images accordingly and save to final filder
print("Cropping and converting slices to calculated bounding box...")
volumeNumber = 0
sliceIndex = 0

for imageTuple in sliceTupelList:
    for image in imageTuple:

        #reset slice index when next volume/segmentation pair is reached
        if volumeNumber != image.split('_')[0]:
            volumeNumber = image.split('_')[0]
            sliceIndex = 0

        im = Image.open(os.path.join(pngFolder, image)).convert('RGB')

        #crop rename and save image. name format is <volume number>_<volume slice number>_<'seg' or 'vol'>.jpeg
        im = im.crop(finalBoundingBox)


        #segmentation postprocessing (switching of color values to single channel 0,1,2 ... N-1 class labels
        if image.find('segmentation'):
            colors = im.getcolors()
            data = np.array(im)

            # classes are:
            # [0,0,0] Background
            # [1,1,1] Liver
            # [2,2,2] Tumor

            # if only 2 colors are present: no tumor visible -> switch liver (now white) to [1,1,1]
            if len(colors) == 2:
                r1, g1, b1 = 255, 255, 255  # Original value
                r2, g2, b2 = 1, 1, 1  # Value that we want to replace it with

                red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
                mask = (red == r1) & (green == g1) & (blue == b1)
                data[:, :, :3][mask] = [r2, g2, b2]

                im = Image.fromarray(data)

            # if 3 colors are visible the liver color (now grey) is switched to [1,1,1] and tumor (now white) is switched to [2,2,2]
            if len(colors) == 3:
                # liver color switch
                r1, g1, b1 = 150, 150, 150  # Original value
                r2, g2, b2 = 1, 1, 1  # Value that we want to replace it with

                red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
                mask = (red == r1) & (green == g1) & (blue == b1)
                data[:, :, :3][mask] = [r2, g2, b2]

                # tumor color switch
                r1, g1, b1 = 255, 255, 255  # Original value
                r2, g2, b2 = 2, 2, 2  # Value that we want to replace it with

                red, green, blue = data[:, :, 0], data[:, :, 1], data[:, :, 2]
                mask = (red == r1) & (green == g1) & (blue == b1)
                data[:, :, :3][mask] = [r2, g2, b2]

                im = Image.fromarray(data)

        im.save(os.path.join(outputFolder, image.split('_')[0] + '_' + str(sliceIndex) + '_' + ('seg' if image.find('segmentation') != -1 else 'vol') + '.png'), "png")
    sliceIndex += 1

#finally delete intermediate pngs
print("Data preprocessing finished!")
shutil.rmtree(pngFolder)
os.makedirs(pngFolder)
from subprocess import call
import os
from PIL import Image
import numpy as np
from medpy.io import load
from medpy.io import save
from operator import itemgetter
import shutil

useTestData = True
if(useTestData):
    rawFolder = os.path.join(os.path.dirname(__file__), '../../data/test/raw/')
    rawSlicesFolder = os.path.join(os.path.dirname(__file__), '../../data/test/rawSlices/')
    tmpFolder = os.path.join(os.path.dirname(__file__), '../../data/test/tmp/')
else:
    rawFolder = os.path.join(os.path.dirname(__file__), '../../data/train/raw/')
    rawSlicesFolder = os.path.join(os.path.dirname(__file__), '../../data/train/rawSlices/')
    tmpFolder = os.path.join(os.path.dirname(__file__), '../../data/train/tmp/')

volumes = [f for f in sorted(os.listdir(rawFolder)) if os.path.isfile(os.path.join(rawFolder, f)) and "volume" in f]
segmentations = [f for f in sorted(os.listdir(rawFolder)) if os.path.isfile(os.path.join(rawFolder, f)) and "segmentation" in f]

volumeTupel = list(zip(segmentations,volumes));


#
#EXTRACT PNG SLICES FOR ALL VOLUMES AND SEGMENTATIONS
#

#loop over segmentation/volume pairs to export PNGs
for fileTuple in volumeTupel:
    for file in fileTuple:

        print(file)

        #get filtype (seg/volume) and the number of it
        if useTestData:
            trash, fileType, number = os.path.splitext(file)[0].split('-') #trash is just the string 'test'
        else:
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
            "-d", rawSlicesFolder,
            "-t", "png",
            "-o", number + "_" + fileType
            ])

        #clear tmp folder for next volume
        shutil.rmtree(tmpFolder)
        os.makedirs(tmpFolder)
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


volumeTupel = zip(segmentations,volumes);

#loop over segmentation/volume pairs to export PNGs
for fileTuple in volumeTupel:
    for file in fileTuple:
        #get filtype (seg/volume) and the number of it
        fileType, number = os.path.splitext(file)[0].split('-')

        #normalize volumes
        if fileType == 'volume':
            print("Normalizing volume: " + file + " with STANDARD DEVIATION")
            image_data, image_header = load(os.path.join(rawFolder, file))
            image_data = (image_data-np.mean(image_data))/np.std(image_data)
            save(image_data,os.path.join(tmpFolder, file),image_header)

        # convert it to PNGs 
        call([
            "med2image", 
            "-i", os.path.join(tmpFolder,file),
            "-d", pngFolder,
            "-t", "png",
            "-o", number + "_" + fileType
            ])
    
    #segmentation/volume pair is normalized and saved as pngs -> calculate bounding boxes on segmentations, crop PNGs and save to final folder as JPG
    volumeSlices = [f for f in sorted(os.listdir(pngFolder)) if os.path.isfile(os.path.join(pngFolder, f)) and "volume" in f]
    segmentationSlices = [f for f in sorted(os.listdir(pngFolder)) if os.path.isfile(os.path.join(pngFolder, f)) and "segmentation" in f]
    
    # tuple of segmentation/volume slice
    sliceTupelList = zip(segmentationSlices, volumeSlices)
    
    boundingBoxes = [] #list of all bounding boxes of all segmentations
    print("Calculating bounding boxes for slices of " + file)

    #reverse loop over PNG segmentations and save all bounding boxes
    for i, slice in reversed(list(enumerate(segmentationSlices))):
        im = Image.open(os.path.join(pngFolder, slice))
        currentBox = im.convert('RGB').getbbox()#convert to rgb since getbbox doesn't work with pngs with alpha channel
        #if no bounding box is present we don't have a segmentation -> del the seg/vol pair from our tupel list for later cropping
        if not currentBox:
            del sliceTupelList[i]
        else:
            boundingBoxes.append(currentBox) 

    #calculate maximum bounding box from all segs
    finalBoundingBox = [min(boundingBoxes,key=itemgetter(0))[0], min(boundingBoxes,key=itemgetter(1))[1], max(boundingBoxes,key=itemgetter(2))[2], max(boundingBoxes,key=itemgetter(3))[3]]
    
    #crop images accordingly and save to final filder
    print("Cropping and converting slices of " + file)
    for index, imageTuple in enumerate(sliceTupelList):
        for image in imageTuple:
            im = Image.open(os.path.join(pngFolder, image)).convert('RGB')
            #crop, rename and save image
            print(image)
            #crop rename and save image. name format is <volume number>_<volume slice number>_<'seg' or 'vol'>.jpeg
            im.crop(finalBoundingBox).save(os.path.join(jpgFolder, image.split('_')[0] + '_' + str(index) + '_' + ('seg' if image.find('segmentation') != -1 else 'vol') + '.jpeg'), "jpeg")
    
    #delete pngs for next segmentation
    shutil.rmtree(pngFolder)
    os.makedirs(pngFolder)
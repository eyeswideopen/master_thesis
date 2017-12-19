from subprocess import call
import os
from PIL import Image
import numpy as np
from medpy.io import load
from medpy.io import save
from operator import itemgetter

imageFolder = os.path.join(os.path.dirname(__file__), '../../data/raw')
volumes = [f for f in sorted(os.listdir(imageFolder)) if os.path.isfile(os.path.join(imageFolder, f)) and "volume" in f]
segmentations = [f for f in sorted(os.listdir(imageFolder)) if os.path.isfile(os.path.join(imageFolder, f)) and "segmentation" in f]


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

#loop over segmentation/volume pairs to export filan PNGs
for fileTuple in volumeTupel:
    for file in fileTuple:
        #get filtype (seg/volume) and the number of it
        fileType, number = os.path.splitext(file)[0].split('-')

        #normalize volumes
        if fileType == 'volume':
            print("Normalizing volume: " + file + " with STANDARD DEVIATION")
            image_data, image_header = load(os.path.join(os.path.dirname(__file__), '../../data/raw/' + file))
            image_data = (image_data-np.mean(image_data))/np.std(image_data)
            save(image_data,os.path.join(os.path.dirname(__file__), '../../data/raw/' + file),image_header)

        # convert it to PNGs 
        call([
            "med2image", 
            "-i", os.path.join(os.path.dirname(__file__), '../../data/raw/' + file), 
            "-d", os.path.join(os.path.dirname(__file__), '../../data/png/'),
            "-t", "png",
            "-o", number + "_" + fileType
            ])
    
    #segmentation/volume pair is normalized and saved as pngs -> calculate bounding boxes on segmentations, crop PNGs and save to final folder as JPG
    sliceFolder = os.path.join(os.path.dirname(__file__), '../../data/png') #temp folder containing current volume slices
    volumeSlices = [f for f in sorted(os.listdir(sliceFolder)) if os.path.isfile(os.path.join(sliceFolder, f)) and "volume" in f]
    segmentationSlices = [f for f in sorted(os.listdir(sliceFolder)) if os.path.isfile(os.path.join(sliceFolder, f)) and "segmentation" in f]
    
    # tuple of segmentation/volume slice
    sliceTupelList = zip(segmentationSlices, volumeSlices)
    
    boundingBoxes = [] #list of all bounding boxes of all segmentations
    for i, slice in reversed(list(enumerate(segmentationSlices))):
        im = Image.open(os.path.join(sliceFolder, slice))
        currentBox = im.convert('RGB').getbbox()#convert to rgb since getbbox doesn't work with pngs with alpha channel
        #if no bounding box is present we don't have a segmentation -> del the seg/vol pair from our tupel list for later cropping
        if not currentBox:
            del sliceTupelList[i]
        else:
            boundingBoxes.append(currentBox) 

    #calculate maximum bounding box from all segs
    finalBoundingBox = [min(boundingBoxes,key=itemgetter(0))[0], min(boundingBoxes,key=itemgetter(1))[1], max(boundingBoxes,key=itemgetter(2))[2], max(boundingBoxes,key=itemgetter(3))[3]]
    #crop images accordingly and save to final filder
    outputFolder = os.path.join(os.path.dirname(__file__), '../../data/jpg')
    for imageTuple in sliceTupelList:
        for image in imageTuple:
            im = Image.open(os.path.join(sliceFolder, image)).convert('RGB')
            im.crop(finalBoundingBox).save(os.path.join(outputFolder, image), "jpeg")
    #delete pngs for next segmentation
    ##TODO: file names of final output and clear png folder for next seg
import os
from PIL import Image
import numpy as np
from medpy.io import load
from medpy.filter import IntensityRangeStandardization
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")

# switch here if data from /train or /test should be used
useTestData = True
saveExampleData = True
removeTumorClass = True #used to only have 1 class (liver) for U-Net liver segmentation


# create folder paths
if(useTestData):
    rawFolder = os.path.join(os.path.dirname(__file__), '../../data/test/raw/')
    outputFolder = os.path.join(os.path.dirname(__file__), '../../data/test/u-net/')
    exampleFolder = os.path.join(os.path.dirname(__file__), '../../data/examples/test/u-net/')

else:
    rawFolder = os.path.join(os.path.dirname(__file__), '../../data/train/raw/')
    outputFolder = os.path.join(os.path.dirname(__file__), '../../data/train/u-net/')
    exampleFolder = os.path.join(os.path.dirname(__file__), '../../data/examples/train/u-net/')


# create tuple list of segmentations/volumes
volumes = [f for f in sorted(os.listdir(rawFolder)) if os.path.isfile(
    os.path.join(rawFolder, f)) and "volume" in f]
segmentations = [f for f in sorted(os.listdir(rawFolder)) if os.path.isfile(
    os.path.join(rawFolder, f)) and "segmentation" in f]
# list of tuples containing absolute file paths to segmentation[0]/volume[1]
filepaths = list(zip(segmentations, volumes))


#
# STEP 1: DATA LOADING - load file data into 3D numpy arrays
#

# contain 3D numpy arrays of segmentation/volumes
numpySegmentations = []
numpyVolumes = []


currentIndex = 0
print("loading data from disk ...")
for fileTuple in tqdm(filepaths):

    #
    # SKIP BLACKLISTED VOLUMES
    #

    # check if seg/vol pair is blacklisted to be skipped
    if useTestData and "59" in fileTuple[0]:
        continue
    currentIndex += 1

    #
    # CONVERT NIFTI TO 3D NUMPY ARRAYS
    #

    # loads the segmentation and volume and stores the numpy arrays in a (seg, vol) tuple into the numpy pairs list
    numpySegmentations.append(load(os.path.join(rawFolder, fileTuple[0]))[0])
    numpyVolumes.append(load(os.path.join(rawFolder, fileTuple[1]))[0])


#
# STEP 2: Intensity range standardization
#

# TODO: get this running
# irs = IntensityRangeStandardization()
# trained_model, numpyVolumes = irs.train_transform(numpyVolumes)

# logger.info('Training the average intensity model...')
#         irs = IntensityRangeStandardization()
#         trained_model, transformed_images = irs.train_transform([i[m] for i, m in zip(images, masks)], surpress_mapping_check = args.ignore)
#         logger.info('Saving the trained model as {}...'.format(args.smodel))
#         with open(args.smodel, 'wb') as f:
#                 pickle.dump(trained_model, f)




#
# STEP 3: PER VOLUME PROCESSING
#
print("processing data ...")

for j in tqdm(range(len(numpySegmentations))):

    rawSegmentation = numpySegmentations[j]
    rawVolume = numpyVolumes[j]

    # 1: normalization
    rawVolume = (rawVolume-np.mean(rawVolume))/np.std(rawVolume)

    #
    # removing tumor class for U-Net liver segmentation
    #
    if removeTumorClass:
        rawSegmentation[rawSegmentation == 2] = 1

    # 2: <add your step here>


    #
    # DATA TYPE CONVERSION - float64 -> uint16
    #

    # VOLUME
    # remove NaN
    rawVolume = np.nan_to_num(rawVolume)

    # zero out negative values
    rawVolume[rawVolume < 0] = 0.0

    # normalize to range 0.0 ... 1.0
    rawVolume = rawVolume/np.max(rawVolume)

    # scale up to 65535 (uin16 max value)
    rawVolume = rawVolume*np.iinfo(np.uint16).max

    # actually switch to uint16
    rawVolume = rawVolume.astype(np.uint16)

    # SEGMENTATION - is already uint8

    #
    # ROTATION - rotate cw and ccw
    #

    #test data
    if useTestData:
        #ccw rotation
        if  0 <= j <= 1 or 7 <= j <= 23 or 34 <= j <= 34 or 37 <= j <= 44 or 46 <= j <= 54 or 56 <= j <= 65:
            rawVolume = np.rot90(rawVolume, 1)
            rawSegmentation = np.rot90(rawSegmentation, 1)
        #cw rotation
        else:
            rawVolume = np.rot90(rawVolume, 3)
            rawSegmentation = np.rot90(rawSegmentation, 3)
    
    #train data
    else:
        #ccw rotation
        if 0 <= j <= 2 or j == 13 or j == 24 or j == 35 or 37 <= j <= 79 or j == 87 or 96 <= j <= 112 or j == 120:
            rawVolume = np.rot90(rawVolume, 1)
            rawSegmentation = np.rot90(rawSegmentation, 1)
        #cw rotation
        else:
            rawVolume = np.rot90(rawVolume, 3)
            rawSegmentation = np.rot90(rawSegmentation, 3)
        

    #
    # MIRRORING - check whether the volume has to be mirrored left right
    #

    leftHalf, rightHalf = np.hsplit(rawSegmentation, 2)

    if np.sum(rightHalf) > np.sum(leftHalf):
        rawVolume = np.fliplr(rawVolume)
        rawSegmentation = np.fliplr(rawSegmentation)


    #
    # SAVE SLICES - check whether the volume has to be mirrored left right
    #

    first = 0
    last = 0
    for i in range(rawVolume.shape[2]):

        segmentationSlice = rawSegmentation[:, :, i]
        volumeSlice = rawVolume[:, :, i]

        # skip empty segmentations -> no liver visible
        if np.max(segmentationSlice) == 0:
            continue

        # save first and last slice index
        if first == 0:
            first = i
        last = i

        # save seg
        image = Image.fromarray(segmentationSlice)
        image.convert('L').save(os.path.join(
            outputFolder, str(j) + "_" + str(i) + "_seg.png"))

        
        # save volume
        
        #TIF save - is already uint16 so PIL mode 'I;16'
        image = Image.fromarray(volumeSlice)
        image.save(os.path.join(outputFolder, str(j) + "_" + str(i) + "_vol.tif"))

        #npy save
        # np.save(os.path.join(outputFolder, str(j) +
        #                      "_" + str(i) + "_vol.npy"), volumeSlice)


    # save the middle slice with visible lable map as example
    if saveExampleData:

        mid = first + int((last - first)/2)

        segmentationSlice = rawSegmentation[:, :, mid]
        volumeSlice = rawVolume[:, :, mid]

        # save seg as 8 bit 1 channel without visible classes for synthetization
        image = Image.fromarray(segmentationSlice)
        image.convert('L').save(os.path.join(
            exampleFolder, str(j) + "_" + str(mid) + "_seg.png"))


        #visialize classes
        segmentationSlice[segmentationSlice == 1] = 150  # liver is grey
        segmentationSlice[segmentationSlice == 2] = 255  # tumors are white

        # save seg as 8 bit 1 channel with visible classes
        image = Image.fromarray(segmentationSlice)
        image.convert('L').save(os.path.join(
            exampleFolder, str(j) + "_" + str(mid) + "_visualSeg.png"))

        image = Image.fromarray(volumeSlice)
        image.save(os.path.join(exampleFolder, str(
            j) + "_" + str(mid) + "_vol.tif"))

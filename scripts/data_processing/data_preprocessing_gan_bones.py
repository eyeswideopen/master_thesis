import os
from PIL import Image
import numpy as np
from medpy.io import load
from medpy.filter import IntensityRangeStandardization
from tqdm import tqdm
import warnings
warnings.filterwarnings("ignore")

# switch here if data from /train or /test should be used
saveExampleData = True


labelFolder = os.path.join(os.path.dirname(__file__), '../../data/bones/raw/labels/')
imageFolder = os.path.join(os.path.dirname(__file__), '../../data/bones/raw/images/')
labelOutputFolder = os.path.join(os.path.dirname(__file__), '../../data/bones/gan/train_label')
imageOutputFolder = os.path.join(os.path.dirname(__file__), '../../data/bones/gan/train_img')

exampleFolder = os.path.join(os.path.dirname(__file__), '../../data/examples/bones/')


# create tuple list of segmentations/volumes
imageFiles = [f for f in sorted(os.listdir(imageFolder)) if os.path.isfile(
    os.path.join(imageFolder, f)) and "tif" in f]
labelFiles = [f for f in sorted(os.listdir(labelFolder)) if os.path.isfile(
    os.path.join(labelFolder, f)) and "png" in f]
# list of tuples containing absolute file paths to segmentation[0]/volume[1]
filepaths = list(zip(labelFiles, imageFiles))


#
# STEP 1: DATA LOADING - load file data into 3D numpy arrays
#

# contain 3D numpy arrays of segmentation/volumes


labels = []
images = []

<<<<<<< HEAD
=======

currentIndex = 0
>>>>>>> 5b9e53cf760f52bc9cc2d310cc5e3c7653648bdf
print("loading data from disk ...")
for fileTuple in tqdm(filepaths):
    # loads the segmentation and volume and stores the numpy arrays in a (seg, vol) tuple into the numpy pairs list
    labels.append(Image.open(os.path.join(labelFolder, fileTuple[0])))
    images.append(Image.open(os.path.join(imageFolder, fileTuple[1])))


print("processing data ...")

for j in tqdm(range(len(labels))):


    label = labels[j]
    image = images[j]


<<<<<<< HEAD
    #DO IMAGE PROCESSING FROM HERE

    numpyLabel = np.array(label)

    #replace 255 label with 1
    numpyLabel[numpyLabel == 255] = 1


    #DO IMAGE PROCESSING TO HERE 

    #convert numpy to image
    label = Image.fromarray(numpyLabel).convert('L')

    # save seg
    label.save(os.path.join(labelOutputFolder, str(j) + "_seg.png"))

    # save volume
    image.convert("RGB").save(os.path.join(imageOutputFolder, str(j) + "_img.png"))


    # np.save(os.path.join(imageOutputFolder, str(j) + "_vol.npy"), np.array(image))
=======
    #DO IMAGE PROCESSING HERE!


    # save seg
    label.convert('L').save(os.path.join(
        outputFolder, str(j) + "_seg.png"))
    # save volume
    np.save(os.path.join(outputFolder, str(j) + "_vol.npy"), np.array(image))



    # # save the middle slice with visible lable map as example
    # if saveExampleData:

    #     mid = first + int((last - first)/2)

    #     segmentationSlice = rawSegmentation[:, :, mid]
    #     volumeSlice = rawVolume[:, :, mid]

    #     # save seg as 8 bit 1 channel without visible classes for synthetization
    #     image = Image.fromarray(segmentationSlice)
    #     image.convert('L').save(os.path.join(
    #         exampleFolder, str(j) + "_" + str(mid) + "_seg.png"))


    #     #visialize classes
    #     segmentationSlice[segmentationSlice == 1] = 150  # liver is grey
    #     segmentationSlice[segmentationSlice == 2] = 255  # tumors are white

    #     # save seg as 8 bit 1 channel with visible classes
    #     image = Image.fromarray(segmentationSlice)
    #     image.convert('L').save(os.path.join(
    #         exampleFolder, str(j) + "_" + str(mid) + "_visualSeg.png"))

    #     image = Image.fromarray(volumeSlice)
    #     image.save(os.path.join(exampleFolder, str(
    #         j) + "_" + str(mid) + "_vol.tif"))
>>>>>>> 5b9e53cf760f52bc9cc2d310cc5e3c7653648bdf

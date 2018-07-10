import os
from PIL import Image
import numpy as np
from tqdm import tqdm

segmentationFolder = os.path.join(os.path.dirname(__file__), '../data/test/gan/')

segmentations = [f for f in sorted(os.listdir(segmentationFolder)) if os.path.isfile(
    os.path.join(segmentationFolder, f)) and "seg" in f]
    
classBalances = {0:0.0,1:0.0,2:0.0}

for seg in tqdm(segmentations):

    arr = np.array(Image.open(os.path.join(segmentationFolder,seg)))
    unique, counts = np.unique(arr, return_counts=True)
    counts = dict(zip(unique, counts))

    for key, value in counts.items():
        if(float(value)/arr.size > 1.0):
            print(float(value)/arr.size)
        classBalances[key] = classBalances[key] + float(value)/arr.size

for key, value in classBalances.items():
    print(value/len(segmentations))
    classBalances[key] = value/len(segmentations)
    
print(classBalances)    

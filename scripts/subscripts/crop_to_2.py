import os
from PIL import Image

rawFolder = os.path.join(os.path.dirname(__file__), '../../data/raw/')
pngFolder = os.path.join(os.path.dirname(__file__), '../../data/png/')
outputFolder = os.path.join(os.path.dirname(__file__), '../../data/tmp/')
tmpFolder = os.path.join(os.path.dirname(__file__), '../../data/tmp/')

images = [f for f in sorted(os.listdir(outputFolder))]

for image in images:
    im = Image.open(os.path.join(outputFolder, image)).convert('RGB')
    im = im.crop((0,0,460,400))
    im.save(os.path.join(outputFolder, image))




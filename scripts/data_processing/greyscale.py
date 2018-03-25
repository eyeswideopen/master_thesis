import os
from PIL import Image
from tqdm import tqdm

outputFolder = os.path.join(os.path.dirname(__file__), '../../pix2pixHD/datasets/liver/train_label/')

images = [f for f in sorted(os.listdir(outputFolder))]

for image in tqdm(images):
    im = Image.open(os.path.join(outputFolder, image)).convert('L')
    im.save(os.path.join(outputFolder, image))




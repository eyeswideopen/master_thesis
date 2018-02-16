#!/bin/bash

#install med2image CLT for PYTHON3
echo "installing med2image with dependencies..."
pip install med2image
pip install https://github.com/loli/medpy/archive/Release_0.3.0p3.zip
echo

#convert all volumes and segmentations to PNGs with file format: <volume>_<slice>_<img/seg>.png e.g. 001_1023_seg.png
echo "converting nifti files to PNG layers..."
python ${BASH_SOURCE%/*}/convert_images.py
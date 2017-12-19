#!/bin/bash
scriptdir="$(dirname "$0")"
cd "$scriptdir"

#import data from NAS to local
source "subscripts/image_preprocessing.sh"

#convert all volumes and segmentations to PNGs with file format: <volume>_<slice>_<img/seg>.png e.g. 001_1023_seg.png
source "subscripts/convert_nifti_to_png.sh"

#slice images
# source "subscripts/slice_images.sh"
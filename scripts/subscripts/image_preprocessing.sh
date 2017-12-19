#!/bin/bash

#check if data folder already exists and prompt if it should be reset
if [ -d "../data" ]; then
    # Control will enter here if dir exists.
    read -p "WARNING: Data folder already existing! DELETE DATA FOLDER AND RECREATE DATA? y/N " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        rm -r ../data
        echo "'data' folder with content deleted!"
    else
        return
    fi
fi
#create data folder and copy images from NAS to local folder
mkdir ../data
mkdir ../data/raw
mkdir ../data/png

echo "'data' folder created..."

#check if NAS is found
if [ ! -d "/media/nas/01_Datasets/CT/LITS/Training Batch 1" ]; then
    echo "Error: data source not found! Is the NAS mounted correctly to '/media/nas'?"
    exit 1
fi
echo "copying image data from NAS to 'data/raw'..."
rsync --progress /media/nas/01_Datasets/CT/LITS/Training\ Batch\ 1/* ../data/raw
rsync --progress /media/nas/01_Datasets/CT/LITS/Training\ Batch\ 2/* ../data/raw
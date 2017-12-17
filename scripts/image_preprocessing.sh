if [ -d "../data" ]; then
    # Control will enter here if $DIRECTORY exists.
    read -p "Data folder already existing!\nDELETE DATA FOLDER AND RECREATE DATA? y/N " -n 1 -r
    echo    # (optional) move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        rm -r ../data
        echo "'data' folder with content deleted!"
    else
        exit 1
    fi
fi
mkdir ../data
echo "'data' folder created"
echo "copying image data from NAS to 'data'"
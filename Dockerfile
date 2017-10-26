#based on the official tensorflow docker
FROM tensorflow/tensorflow
#add everything to container
ADD . .
#commands to be run at the beginning
CMD ["python", "image_synthesis/test.py"]

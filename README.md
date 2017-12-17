# Master Thesis Maximilian Körner
This is the repository containing all code for my (Maximilian Körner) master thesis
The code runs in a self contained Docker container

##local dependencies
[Docker (obviously)](https://docs.docker.com/engine/installation/) - to run the container\
[OPTIONAL (Linux): nvidia-docker](https://github.com/NVIDIA/nvidia-docker) - to enable GPU utilization. only available for linux

___

##running
###script (recommended)
by running ```./run_docker.sh``` the docker image is automatically rebuilt and run

***
###manually building and running

#####build image
```docker build -t image_synthesis .```

#####run container
```docker run image_synthesis```
# Useful links

* api reference:
  https://canvas.instructure.com/doc/api/index.html

* python wrapper:
  https://github.com/ucfopen/canvasapi

* docker image with api enabled:
  https://hub.docker.com/r/lbjay/canvas-docker/~/dockerfile/

# setting up a development environment for osx

  * Install current miniconda (say in /Users/phil/ma36)

  * Add the followling lines to your .bashrc/.bash_profile:

        . /Users/phil/ma36/etc/profile.d/conda.sh
        conda activate root

  * Start a new terminal and Install conda-build and anaconda-client:

        conda install conda-build anaconda-client
      
  * cd repos/canvas_scripting/python/e340package

        conda build .
        anaconda upload path-to-bz2file

  * test the channel

        conda install -c yourchannel e340py
        dump_comments -h



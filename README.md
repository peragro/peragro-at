DAMN-AT
====
Digital Assets Managed Neatly - Analyzers and Transcoders


http://sueastside.github.io/damn-at/


![Build Status](https://api.travis-ci.org/sueastside/damn-at.png)
[![Code Health](https://landscape.io/github/sueastside/damn-at/master/landscape.png)](https://landscape.io/github/sueastside/damn-at/master)


Installation
----- 
Install Blender, Git, Pip and other initial python requirements
 ```
    sudo add-apt-repository ppa:irie/blender
    sudo apt-get update -qq
    sudo apt-get install -qq blender
    sudo apt-get install -qq git
    sudo apt-get install -qq python-virtualenv
    sudo apt-get install -qq python-pip
    sudo apt-get install python-software-properties
    sudo apt-get install python-dev cython libavcodec-dev libavformat-dev libswscale-dev
    sudo apt-get install python-matplotlib
 ```
 
Install Thirft globally for python3
 ```
    git clone https://github.com/wgwang/thrift.git
    cd thrift/py3/src
    python3 setup.py install
    cd ../../..
 ```
 
Create a virtualenv and activate it
 ```
    virtualenv env
    source env/bin/activate 
 ```
 
Checkout damn-at
 ```
    git clone https://github.com/sueastside/damn-at.git
 ```
 
Install damn-at
 ```
    cd damn-at
    ../env/bin/python setup.py develop
 ```
 
Optional: checkout test files
 ```
    cd ..
    git clone https://github.com/sueastside/damn-test-files.git
 ```
 
Usage
----- 
Analyze
 ```
    mkdir /tmp/damn
    damn_at-analyze /tmp/damn damn-test-files/mesh/blender/cube1.blend
 ```
  Output:
 ```
    ----------------------------------------------------------------------
    Analyzing damn-test-files/mesh/blender/cube1.blend into /tmp/damn
    ----------------------------------------------------------------------

    52c676b407d05d50282661b7b451a52cc93b46d2 
    ----------------------------------------
    Assets: 5
      -->Cube1-data  (application/x-blender.mesh)
      -->Camera  (application/x-blender.object)
      -->Cube1-object  (application/x-blender.object)
      -->Lamp  (application/x-blender.object)
      -->Text  (application/x-blender.text)
 ```

Inspect 
 ```
    damn_at-inspect /tmp/damn/52c676b407d05d50282661b7b451a52cc93b46d2
 ```
  Output:
 ```
     ___   _   __  __ _  _ 
    |   \ /_\ |  \/  | \| |
    | |) / _ \| |\/| | .` |
    |___/_/ \_\_|  |_|_|\_|
        Digital Assets Managed Neatly.

    Inspecting "/tmp/damn/52c676b407d05d50282661b7b451a52cc93b46d2"

    hash: 52c676b407d05d50282661b7b451a52cc93b46d2
    filename: /home/sueastside/dev/DAMN/damn-test-files/mesh/blender/cube1.blend
    5 Assets: 
    ================================================================================
    * Cube1-data (application/x-blender.mesh)
      hash: 52c676b407d05d50282661b7b451a52cc93b46d2
      filename: /home/sueastside/dev/DAMN/damn-test-files/mesh/blender/cube1.blend
      Dependencies (1):
        * crate10b.jpg (image/jpeg)
          hash: 8c8065ae5590cb5d669426651ce229ed11c5f07d
          filename: ../../image/jpg/crate10b.jpg
      MetaData (2):
        * nr_of_vertices: 24
        * nr_of_faces: 0
    --------------------------------------------------------------------------------
    * Camera (application/x-blender.object)
      hash: 52c676b407d05d50282661b7b451a52cc93b46d2
      filename: /home/sueastside/dev/DAMN/damn-test-files/mesh/blender/cube1.blend
    --------------------------------------------------------------------------------
    * Cube1-object (application/x-blender.object)
      hash: 52c676b407d05d50282661b7b451a52cc93b46d2
      filename: /home/sueastside/dev/DAMN/damn-test-files/mesh/blender/cube1.blend
      Dependencies (1):
        * Cube1-data (application/x-blender.mesh)
          hash: 52c676b407d05d50282661b7b451a52cc93b46d2
          filename: /home/sueastside/dev/DAMN/damn-test-files/mesh/blender/cube1.blend
    --------------------------------------------------------------------------------
    * Lamp (application/x-blender.object)
      hash: 52c676b407d05d50282661b7b451a52cc93b46d2
      filename: /home/sueastside/dev/DAMN/damn-test-files/mesh/blender/cube1.blend
    --------------------------------------------------------------------------------
    * Text (application/x-blender.text)
      hash: 52c676b407d05d50282661b7b451a52cc93b46d2
      filename: /home/sueastside/dev/DAMN/damn-test-files/mesh/blender/cube1.blend
    --------------------------------------------------------------------------------
 ```

Transcode
 ```
    damn_at-transcode /tmp/damn/8c8065ae5590cb5d669426651ce229ed11c5f07d crate10b.jpg image/jpeg -h
 ```
  Output:
 ```
    usage: damn_at-transcode [-h] [--size SIZE] [--quality QUALITY]

    optional arguments:
      -h, --help         show this help message and exit
      --size SIZE        The target size of the image (Value needs to be between 1
                         and 4096) [default: (-1, -1)]
      --quality QUALITY  The target quality of the image (Value needs to be
                         between 0.0 and 1.0) [default: 1.0]
 ```

Or
 ```
    damn_at-transcode /tmp/damn/52c676b407d05d50282661b7b451a52cc93b46d2 Cube1-object image/png -h
 ```
  Output:
 ```
    usage: damn_at-transcode [-h] [--size SIZE] [--camera_type CAMERA_TYPE]
                             [--angles ANGLES]

    optional arguments:
      -h, --help            show this help message and exit
      --size SIZE           The target size of the image (Value needs to be
                            between 1 and 4096) [default: (64, 64)]
      --camera_type CAMERA_TYPE
                            The camera type (Value needs to be one of ('ORTHO',
                            'PERSPECTIVE')) [default: PERSPECTIVE]
      --angles ANGLES       The angle (Value needs to be between 0.0 and 3.1415)
                            [default: (0.0,)]
 ```
 
And finally lets generate a thumb for a blender mesh datablock
 ```
    damn_at-transcode /tmp/damn/52c676b407d05d50282661b7b451a52cc93b46d2 Cube1-object image/png --size=64,64
 ```
  Output:
 ```
     ___   _   __  __ _  _ 
    |   \ /_\ |  \/  | \| |
    | |) / _ \| |\/| | .` |
    |___/_/ \_\_|  |_|_|\_|
        Digital Assets Managed Neatly.

    Transcoding "/home/sueastside/dev/DAMN/damn-test-files/mesh/blender/cube1.blend"

    Using: Blender object render transcoder
    with: 
    * camera_type: PERSPECTIVE 
    * angles: (0.0,) 
    * size: [64, 64] 
    0
    ['assets/52c676b407d05d50282661b7b451a52cc93b46d2Cube1-objectapplication%7Cx-blender.object/image/png/[64, 64]/PERSPECTIVE/0.0/52c676b407d05d50282661b7b451a52cc93b46d2Cube1-objectapplication%7Cx-blender.object.png']
 ```

 ```
    eog /tmp/transcoded/assets/52c676b407d05d50282661b7b451a52cc93b46d2Cube1-objectapplication%7Cx-blender.object/image/png/\[64\,\ 64\]/PERSPECTIVE/0.0/52c676b407d05d50282661b7b451a52cc93b46d2Cube1-objectapplication%7Cx-blender.object.png
 ```

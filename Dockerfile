FROM ubuntu:16.04
MAINTAINER Brant Watson

# Install dependencies
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common python-software-properties
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y blender git python3-pip python3-dev cython sox libsox-fmt-mp3 ffmpeg libimage-exiftool-perl python3-matplotlib libassimp-dev
RUN pip3 install pyassimp
RUN mkdir -p /opt
RUN git clone -b 0.10.0 https://github.com/apache/thrift.git /opt/thrift
RUN cd /opt/thrift/lib/py && python3 setup.py install
RUN pip3 install Yapsy Image gitpython filemagic logilab-common setuptools thrift argcomplete pyacoustid
RUN git clone https://github.com/peragro/peragro-test-files.git /opt/peragro-test-files
ARG CACHEBUST=1
RUN git clone https://github.com/peragro/peragro-at.git /opt/peragro-at
RUN cd /opt/peragro-at && python3 setup.py develop
RUN pt a /opt/peragro-test-files/mesh/blender/cube1.blend

ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

#Install gaia & essentia
#note:
#   Before we install gaia we need to install the latest version of swig
#   As gaia build will fail if we'll use the swig package distributed with ubuntu 16.04
#   i.e. gaia build will fail if we'll use swig 3.0.8

#Install swig
RUN apt-get update \
    && apt-get install -y \
        autoconf \
        automake \
        libtool \
        libpcre3-dev \
        bison \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/swig/swig.git /tmp/swig \
    && cd /tmp/swig \
    && sh autogen.sh \
    && ./configure \
    && make \
    && make install \
    && cd .. \
    && rm -r /tmp/swig

#Now install gaia
RUN apt-get update \
    && apt-get install -y \
       build-essential \
       libqt4-dev \
       libyaml-dev \
       swig \
       python-dev \
       pkg-config

RUN git clone https://github.com/MTG/gaia.git /tmp/gaia \
    && cd /tmp/gaia \
    && ./waf configure --with-python-bindings \
    && ./waf \
    && ./waf install \
    && rm -r /tmp/gaia

#install essentia v2.1_beta2
RUN apt-get update \
    && apt-get install -y \
       libfftw3-dev \
       libavcodec-dev \
       libavformat-dev \
       libavutil-dev \
       libavresample-dev \
       libsamplerate0-dev \
       libtag1-dev

RUN git clone https://github.com/MTG/essentia.git /tmp/essentia \
    && cd /tmp/essentia \
    && git checkout tags/v2.1_beta2 \
    && ./waf configure --mode=release --with-gaia \
       --with-example=streaming_extractor_music_svm,streaming_extractor_music \
    && ./waf \
    && cp ./build/src/examples/streaming_extractor_music /usr/local/bin \
    && cp ./build/src/examples/streaming_extractor_music_svm /usr/local/bin \
   # && cp ./build/src/examples/streaming_extractor_freesound /usr/local/bin \
    #&& cp ./build/src/libessentia.so /usr/local/lib \
    && rm -r /tmp/essentia

#Download svm models for high level extraction
#RUN curl http://essentia.upf.edu/documentation/svm_models/essentia-extractor-svm_models-v2.1_beta1.tar.gz | tar xz -C /tmp \
#    && mv /tmp/v2.1_beta1/svm_models/ /usr/local/bin/

RUN ldconfig /usr/local/lib
FROM ubuntu:16.04
MAINTAINER Peragro Team

# apt-get Install dependencies
RUN apt-get update

# peragro-at required dependencies
RUN apt-get install -y software-properties-common python-software-properties blender git python3-pip python3-dev cython sox libsox-fmt-mp3 ffmpeg libimage-exiftool-perl python3-matplotlib libassimp-dev
RUN pip3 install Yapsy Image gitpython filemagic logilab-common setuptools thrift argcomplete pyacoustid pyassimp

# swift dependencies
RUN apt-get install -y autoconf automake libtool libpcre3-dev bison 

# gaia dependencies
RUN apt-get install -y  build-essential libqt4-dev libyaml-dev swig python-dev pkg-config

# essentia dependencies
RUN apt-get install -y libfftw3-dev libavcodec-dev libavformat-dev libavutil-dev libavresample-dev libsamplerate0-dev libtag1-dev

# install thrift 0.10.0
RUN git clone -b 0.10.0 https://github.com/apache/thrift.git /opt/thrift \
    && cd /opt/thrift/lib/py && python3 setup.py install

# build items
RUN mkdir -p /opt
RUN ldconfig /usr/local/lib
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib

# build swig
RUN git clone https://github.com/swig/swig.git /opt/swig \
    && cd /opt/swig \
    && git checkout tags/rel-3.0.12 \
    && sh autogen.sh \
    && ./configure \
    && make -j8 \
    && make install 

# Now install gaia
RUN git clone https://github.com/MTG/gaia.git /opt/gaia \
    && cd /opt/gaia \
    && ./waf configure --with-python-bindings \
    && ./waf \
    && ./waf install 

#install essentia v2.1_beta2
RUN git clone https://github.com/MTG/essentia.git /opt/essentia \
    && cd /opt/essentia \
    && git checkout tags/v2.1_beta2 \
    && ./waf configure --mode=release --with-gaia --with-example=streaming_extractor_music_svm,streaming_extractor_music \
    && ./waf \
    && cp ./build/src/examples/streaming_extractor_music /usr/local/bin \
    && cp ./build/src/examples/streaming_extractor_music_svm /usr/local/bin
    #&& cp ./build/src/examples/streaming_extractor_freesound /usr/local/bin \
    #&& cp ./build/src/libessentia.so /usr/local/lib 


#Download svm models for high level extraction
#RUN curl http://essentia.upf.edu/documentation/svm_models/essentia-extractor-svm_models-v2.1_beta1.tar.gz | tar xz -C /tmp \
#    && mv /tmp/v2.1_beta1/svm_models/ /usr/local/bin/

#Download peragro-test-data for troubleshooting
RUN git clone https://github.com/peragro/peragro-test-files.git /opt/peragro-test-files

#download and setup peragro-at
ARG CACHEBUST=1
RUN git clone https://github.com/peragro/peragro-at.git /opt/peragro-at
RUN cd /opt/peragro-at && python3 setup.py develop
RUN pt a /opt/peragro-test-files/mesh/blender/cube1.blend
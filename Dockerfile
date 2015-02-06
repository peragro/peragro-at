FROM ubuntu:14.04
MAINTAINER Brant Watson

# Install dependencies
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common python-software-properties
RUN DEBIAN_FRONTEND=noninteractive add-apt-repository -y ppa:irie/blender
RUN DEBIAN_FRONTEND=noninteractive add-apt-repository -y ppa:jon-severinsson/ffmpeg
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y blender git python3-pip python3-dev cython libavcodec-dev libavformat-dev libswscale-dev python-pyassimp sox libsox-fmt-mp3 ffmpeg libimage-exiftool-perl
RUN DEBIAN_FRONTEND=noninteractive apt-get -y build-dep python-matplotlib
RUN mkdir -p /root
RUN git clone https://github.com/wgwang/thrift.git /root/thrift
RUN cd /root/thrift/lib/py3 && python3 setup.py sdist
RUN pip3 install /root/thrift/lib/py3/dist/*.tar.gz
RUN pip3 -v install matplotlib
COPY dist /root
RUN pip3 -v install /root/*.tar.gz
RUN rm -rf root/*.tar.gz

FROM ubuntu:16.04
MAINTAINER Brant Watson

# Install dependencies
RUN DEBIAN_FRONTEND=noninteractive apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y software-properties-common python-software-properties
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y blender git python3-pip python3-dev cython sox libsox-fmt-mp3 ffmpeg libimage-exiftool-perl python3-matplotlib libassimp-dev
RUN pip3 install pyassimp
RUN mkdir -p /opt
RUN git clone -b 0.10.0 https://github.com/apache/thrift.git /opt/thrift
RUN cd /root/thrift/lib/py && python3 setup.py install
RUN git clone https://github.com/peragro/peragro-at.git /opt/peragro-at
RUN cd /root/opt/peragro-at && python3 setup.py develop
FROM ubuntu

# Major dependencies
RUN apt-get -y update && \
apt-get -y install python3 espeak gstreamer1.0-tools curl && \
curl https://bootstrap.pypa.io/get-pip.py -o /home/get-pip.py && \
python3 /home/get-pip.py

# pyzmq (from requirements.txt) dependency
RUN apt-get -y install libzmq5 \
# provides rtpL16pay plugin
gstreamer1.0-plugins-good \
# provides audioparse plugin
gstreamer1.0-plugins-bad

ADD . /app
RUN pip install -r /app/requirements.txt

# IP address to stream audio to. May need to override on runtime. E.g.:
# docker run -it --rm -e STREAM_TARGET=192.168.0.16 talkbots
ENV STREAM_TARGET 172.17.0.1

WORKDIR /app
CMD python3 chatter.py & python3 wav_pump.py & \
gst-launch-1.0 -v filesrc location=wav_sink/audio_pipe ! audioparse raw-format=s16le rate=22050 channels=1 ! queue2 ! audioresample ! audioconvert ! rtpL16pay pt=10 ! application/x-rtp, pt=10, encoding-name=L16, payload=10, clock-rate=44100, channels=2 ! udpsink host=${STREAM_TARGET} port=5555

# # Install required packages
# RUN apt-get -y update
# RUN apt-get -y install ros-indigo-openni-camera ros-indigo-mjpeg-server \
#           ros-indigo-rosbridge-server ros-indigo-tf ros-indigo-audio-common \
#           ros-indigo-driver-common
# RUN apt-get -y install python-serial  python-pycurl python-pyglet python-pip
# RUN apt-get -y install mplayer
# # RUN apt-get -y install libcurl3 libavbin-dev libavbin0 libav-tools

# # Install pi_vision
# WORKDIR /opt/ros/indigo/share
# RUN git clone https://github.com/ericperko/uvc_cam.git
# RUN bash -l -c "source /.bashrc;rosmake uvc_cam"

# # Owyl setup
# WORKDIR /opt/
# RUN git clone https://github.com/eykd/owyl.git
# WORKDIR /opt/owyl/
# RUN python setup.py install

# # Install catkin packages
# WORKDIR /catkin_ws/src
# RUN git clone -b multiple_2d https://github.com/hansonrobotics/pi_vision.git
# RUN git clone https://github.com/hansonrobotics/ros_pololu_servo.git
# RUN git clone https://github.com/hansonrobotics/robo_blender.git
# RUN git clone https://github.com/hansonrobotics/pau2motors.git
# RUN git clone https://github.com/hansonrobotics/basic_head_api.git
# RUN git clone https://github.com/hansonrobotics/ros_motors_webui.git
# RUN git clone https://github.com/hansonrobotics/robots_config.git
# RUN git clone https://github.com/hansonrobotics/chatbot.git
# RUN git clone https://github.com/hansonrobotics/eva_behavior.git
# RUN git clone https://github.com/hansonrobotics/ros_faceshift.git

# # Copy animations file
# COPY animations.blend /catkin_ws/src/robo_blender/src/

# # Change line below to rebuild. Will use cache up to this line
# ENV LAST_SOFTWARE_UPDATE 2014-12-08

# # Git pull for all packages
# WORKDIR /catkin_ws/src
# RUN find . -maxdepth 1 -mindepth 1 -type d \
#   -execdir git --git-dir=$PWD/{}/.git --work-tree=$PWD/{} pull \;

# RUN mkdir /catkin_ws/src/docker-scripts
# CMD /bin/bash

# COPY /scripts/arthur-dev.sh /catkin_ws/src/docker-scripts/arthur-dev.sh

# # CMake
# WORKDIR /catkin_ws
# RUN bash -l -c "/usr/bin/python3 /opt/ros/indigo/bin/catkin_make"

# RUN echo source /catkin_ws/devel/setup.bash >> ~/.bashrc

# #Ports exposed
# EXPOSE 9090
# EXPOSE 80
# EXPOSE 33433

# ENTRYPOINT bash -l -c "cd /catkin_ws/src/docker-scripts; ./arthur-dev.sh; bash"
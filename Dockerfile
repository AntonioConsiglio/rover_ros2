FROM ubuntu:jammy

RUN locale  # check for UTF-8

RUN apt update && apt install locales -y
RUN locale-gen it_IT it_IT.UTF-8
RUN update-locale LC_ALL=it_IT.UTF-8 LANG=it_IT.UTF-8
RUN export LANG=it_IT.UTF-8

# Set the timezone
ENV ROS_VERSION=2
ENV ROS_DISTRO=humble
ENV ROS_PYTHON_VERSION=3
# Share topic on local net
ENV ROS_DOMAIN_ID=0
ENV ROS_LOCALHOST_ONLY=0

ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt install software-properties-common -y
RUN add-apt-repository universe

RUN apt update && apt install curl -y
RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key -o /usr/share/keyrings/ros-archive-keyring.gpg

RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | tee /etc/apt/sources.list.d/ros2.list > /dev/null

RUN apt update && apt upgrade -y
RUN apt install nano -y

WORKDIR /ros2_project
COPY scripts/*.sh /ros2_project/

RUN chmod +x ./*.sh

RUN apt-get install libserial-dev xterm libi2c-dev -y

#Installing ROS Humble base package and development tools
RUN apt-get update -y
RUN apt-get install ros-humble-ros-base -y
RUN apt install ros-dev-tools -y

#Sourcing ROS Humble setup script and 
RUN echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
RUN echo 'source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash' >> ~/.bashrc

RUN /bin/bash -c "source /opt/ros/humble/setup.bash"

#Install ROS Humble utils packages 
RUN apt install ros-humble-rviz2 -y
RUN apt install ros-humble-xacro -y
RUN apt install ros-humble-ros2-control -y
RUN apt install ros-humble-joint-state-publisher-gui -y
RUN apt install ros-humble-tf2-ros -y
RUN apt install ros-humble-twist-mux -y

#Install ROS Humble controllers packages 
RUN apt-get install ros-humble-ros2-controllers -y
RUN apt install ros-humble-teleop-twist-keyboard -y
RUN apt install ros-humble-teleop-twist-joy -y
RUN apt install ros-humble-joy -y
RUN apt install ros-humble-cv-bridge -y
RUN apt install ros-humble-ffmpeg-image-transport-msgs -y

#Install ROS Humble robot localization package 
RUN apt install ros-humble-robot-localization -y

#Install ROS Humble Navigation packages 
RUN apt install ros-humble-navigation2 ros-humble-nav2-bringup -y

# Install depthai ros dependencies and pkgs
RUN apt install ros-humble-depthai-ros -y

RUN apt install python3-pip -y
RUN pip3 install smbus

#Install correct Eigen Dependencies and ORB-SLAM3 with dependencies
WORKDIR /ros2_project
# Try to clone the repository
RUN git clone https://gitlab.com/libeigen/eigen.git
RUN rm -r /usr/include/eigen3
RUN cd eigen && git checkout 3.4 && cd ..
RUN cp -r ./eigen /usr/include/eigen3

#Install Pangolin library v0.6
RUN git clone https://github.com/stevenlovegrove/Pangolin Pangolin
WORKDIR /ros2_project/Pangolin
RUN yes | ./scripts/install_prerequisites.sh recommended
RUN git checkout v0.6
COPY /pkg_developed/colour.h /ros2_project/Pangolin/include/pangolin/gl/
RUN mkdir build && cd build && cmake .. && make && make install

WORKDIR /ros2_project

#Install ORB_SLAM3
RUN git clone -b c++14_comp https://github.com/UZ-SLAMLab/ORB_SLAM3.git ORB_SLAM3
COPY /pkg_developed/orb_slam_build.sh /ros2_project/ORB_SLAM3/
# copy nan handle file to prevent shopus error with nan values
COPY /pkg_developed/ImuTypes.cc /ros2_project/ORB_SLAM3/src/
COPY /pkg_developed/Sim3Solver.cc /ros2_project/ORB_SLAM3/src/
WORKDIR /ros2_project/ORB_SLAM3
#Build dependencies and orb-slam3 with custom core number 
RUN chmod +x ./orb_slam_build.sh && ./orb_slam_build.sh
RUN echo 'export LD_LIBRARY_PATH=/ros2_project/ORB_SLAM3/lib:/usr/local/lib:$LD_LIBRARY_PATH' >> ~/.bashrc

WORKDIR /ros2_project

RUN bash
# RUN ./install_microros_esp32.sh


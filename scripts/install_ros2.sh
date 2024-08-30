#!/bin/bash
apt install ros-humble-ros-base -y
apt install ros-dev-tools -y
echo 'source /opt/ros/humble/setup.bash' >> ~/.bashrc
echo 'source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash' >> ~/.bashrc

source /opt/ros/humble/setup.bash

apt-get install xterm
apt install ros-humble-rviz2 -y
apt install ros-humble-xacro -y
apt install ros-humble-ros2-control -y
apt install ros-humble-joint-state-publisher-gui -y
apt install ros-humble-teleop-twist-keyboard -y
apt install ros-humble-joy -y
apt-get install ros-humble-ros2-controllers -y
apt install ros-humble-navigation2 ros-humble-nav2-bringup -y
apt install ros-humble-tf2-ros -y
apt install ros-humble-twist-mux -y

apt-get install libserial-dev -y

# Install depthai ros dependencies and pkgs
apt install ros-humble-depthai-ros -y

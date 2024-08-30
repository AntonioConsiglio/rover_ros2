#!/bin/bash

cd /pkg_developed

rm -r /usr/include/eigen3

cp -r ./eigen /usr/include/eigen3

cd /pkg_developed/rover_ws 
source /opt/ros/humble/setup.bash && colcon build
. install/setup.bash && ros2 launch rover_controller full_teleop_controller.launch.py

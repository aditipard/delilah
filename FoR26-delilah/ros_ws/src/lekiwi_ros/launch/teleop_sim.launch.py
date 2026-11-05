"""Start the simulator and the leader arm together: move the leader by hand, the simulated arm follows.

Usage:
    ros2 launch lekiwi_ros teleop_sim.launch.py port:=/dev/serial/by-id/usb-...
Optional arguments:
    scene:=cubes|keyboard|empty   (default cubes)
    viewer:=true|false            (default true)
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription([
        # Arguments are the values you can set on the command line with name:=value.
        DeclareLaunchArgument("port", description="serial port of the leader arm"),
        DeclareLaunchArgument("scene", default_value="cubes"),
        DeclareLaunchArgument("viewer", default_value="true"),

        # One Node(...) entry per node to start. It does the same as "ros2 run package executable".
        Node(package="lekiwi_ros", executable="sim_node", output="screen",
             parameters=[{"scene": LaunchConfiguration("scene"),
                          "viewer": ParameterValue(LaunchConfiguration("viewer"), value_type=bool)}]),
        Node(package="lekiwi_ros", executable="leader_node", output="screen",
             parameters=[{"port": LaunchConfiguration("port")}]),
    ])

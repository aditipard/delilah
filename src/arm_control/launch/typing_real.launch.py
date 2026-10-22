"""Launch keyboard typing against the physical LeKiwi robot."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("port", default_value=""),
        DeclareLaunchArgument("robot_id", default_value="lekiwi"),
        DeclareLaunchArgument("enable_motors", default_value="false"),
        DeclareLaunchArgument("max_relative_target", default_value="8.0"),
        DeclareLaunchArgument("rate_hz", default_value="10.0"),
        Node(
            package="lekiwi_ros",
            executable="robot_node",
            prefix="python3 -u",
            output="screen",
            parameters=[{
                "port": LaunchConfiguration("port"),
                "robot_id": LaunchConfiguration("robot_id"),
                "enable_motors": ParameterValue(
                    LaunchConfiguration("enable_motors"),
                    value_type=bool,
                ),
                "max_relative_target": ParameterValue(
                    LaunchConfiguration("max_relative_target"),
                    value_type=float,
                ),
                "rate_hz": ParameterValue(
                    LaunchConfiguration("rate_hz"),
                    value_type=float,
                ),
            }],
        ),
        Node(
            package="arm_control",
            executable="forward_kinematics",
            prefix="python3 -u",
            output="screen",
        ),
        Node(
            package="arm_control",
            executable="keyboard_typer",
            prefix="python3 -u",
            output="screen",
        ),
    ])

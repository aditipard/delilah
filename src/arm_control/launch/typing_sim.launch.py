"""Launch the LeKiwi keyboard simulation and ROS control nodes."""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():

    return LaunchDescription([

        # Viewer setting
        DeclareLaunchArgument(
            "viewer",
            default_value="true"
        ),

        # LeKiwi simulation
        Node(
            package="lekiwi_ros",
            executable="sim_node",
            prefix="python3 -u",
            output="screen",
            parameters=[{
                "scene": "keyboard",
                "viewer": ParameterValue(
                    LaunchConfiguration("viewer"),
                    value_type=bool
                )
            }]
        ),

        # Forward Kinematics
        Node(
            package="arm_control",
            executable="forward_kinematics",
            name="forward_kinematics",
            prefix="python3 -u",
            output="screen"
        ),

        # Inverse Kinematics (EEControl)
        Node(
            package="arm_control",
            executable="inverse_kinematics",
            name="ee_control",
            prefix="python3 -u",
            output="screen"
        ),

        # Keyboard Typing Controller
        Node(
            package="arm_control",
            executable="keyboard_typer",
            name="keyboard_typer",
            prefix="python3 -u",
            output="screen"
        ),

    ])

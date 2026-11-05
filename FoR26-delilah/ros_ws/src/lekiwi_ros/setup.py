from glob import glob

from setuptools import setup

package_name = "lekiwi_ros"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name + "/launch", glob("launch/*.launch.py")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    description="ROS 2 nodes for the LeKiwi course: the simulator and the leader arm",
    license="GPL-3.0-only",
    entry_points={
        "console_scripts": [
            "sim_node = lekiwi_ros.sim_node:main",
            "leader_node = lekiwi_ros.leader_node:main",
            "robot_node = lekiwi_ros.robot_node:main",
        ],
    },
)

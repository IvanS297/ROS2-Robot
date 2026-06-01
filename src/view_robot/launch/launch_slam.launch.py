import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch.event_handlers import OnProcessStart
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import Command
import xacro


def generate_launch_description():

    pkg_path = get_package_share_directory('view_robot')

    robot_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg_path, 'launch', 'launch_robot.launch.py'))
    )

    slam_toolbox_launch = PathJoinSubstitution([
        FindPackageShare('slam_toolbox'), 'launch', 'online_async_launch.py'
    ])

    slam_toolbox_config_file = PathJoinSubstitution([
        FindPackageShare('view_robot'), 'config', 'mapper_params_online_async.yaml'
    ])

    start_slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_toolbox_launch),
        launch_arguments={'slam_params_file': slam_toolbox_config_file}.items()
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        robot_launch,
        #rf2o,
        start_slam_toolbox,
    ])

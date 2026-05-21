import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch_ros.actions import Node

def generate_launch_description():
    
    joy_config_file = os.path.join(get_package_share_directory('view_robot'), 'config', 'joy.yaml')

    arduino_joy_node = Node(
        package='arduino_joystick',
        executable='joy_bridge',
        name='joy_bridge',
    )

    joy_node = Node(
        package='teleop_twist_joy',
        executable='teleop_node',
        name='teleop_twist_joy_node',
        parameters=[{
            'publish_stamped_twist': True,
            'frame_id': 'base_link',
            # Настройки для вашего джойстика:
            'enable_button': -1,           # -1 отключает обязательное зажатие кнопки (опасно, но для теста пойдет)
            'require_enable_button': False, # Не требовать кнопку активации
            'axis_linear.x': 1,            # Вторая ось в списке (индекс 1)
            'axis_angular.yaw': 0,         # Первая ось в списке (индекс 0)
            'scale_linear.x': 0.5,         # Макс. скорость м/с
            'scale_angular.yaw': 1.0       # Макс. скорость рад/с
        }],
        remappings=[
            ('/cmd_vel', '/diff_cont/cmd_vel') # Переименование топика
        ]
    )

    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        arduino_joy_node,
        joy_node,
    ])
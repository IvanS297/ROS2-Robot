from setuptools import find_packages, setup

package_name = 'arduino_joystick'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ivan',
    maintainer_email='ivan.ser202@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    entry_points={
        'console_scripts': [
            "joy_bridge=arduino_joystick.arduino_joy_bridge:main"
        ],
    },
)

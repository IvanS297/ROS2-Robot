# ROS2-Robot

---

### Убедитесь что `RMW_ZEHOH` настроен на одной машине как серве, на другой как клиент, и запущен на сервер-машине

---

## RMW_ZENOH_CPP
### Один раз на сервере!
```bash
echo "export RMW_IMPLEMENTATION=rmw_zenoh_cpp" >> ~/.bashrc
echo "export ZENOH_ROUTER_CONFIG_URI=/home/ivan/routerconfig.json5" >> ~/.bashrc
source ~/.bashrc
```
Каждый раз, когда перезапускаете компьюетер. (Включили и забыли)
```bash
ros2 run rmw_zenoh_cpp rmw_zenohd --config ~/ros2_ws/zenoh_router.json5 # запуск сервера на одной машине
```

На другом устройстве ничего едлать не надо, надо просто настроить переменные среды.
### Один раз на клиенте!
```bash
echo "export RMW_IMPLEMENTATION=rmw_zenoh_cpp" >> ~/.bashrc
echo "ZENOH_SESSION_CONFIG_URI=/home/admin/.config/zenoh/session_config.json5" >> ~/.bashrc
source ~/.bashrc
```
И всё.

### Ощшибки во время работы `RMW_ZENOH`
Если при работе более чем с двумя машинами, происходят такие ошибки:
```error
ERROR rx-1 ThreadId(05) zenoh::net::routing::dispatcher::pubsub: Error treating timestamp for received Data (incoming timestamp from exceeding delta 500ms is rejected: ). Replace timestamp: Some
```
То проблема в том, что время  на машинах расходится более чем на 500мс, решения 4 штуки:
1. Поставить точное время при помощи `rtc`. Гайд по [ссылке](https://www.instructables.com/Raspberry-Pi-DS3231/).
2. Каждыдй раз при запуске системы ставить точное время вручную:
   ```bash
   sudo date --set "YYYY-MM-DD HH:MM:SS"
   ```
3. Брать время из интернета:
   ```bash
   sudo ntpdate pool.ntp.org
   ```
4. Просто убрать ошибки от соединений `rmw_zenoh`, [инструкция](https://zenoh.io/docs/getting-started/troubleshooting/):
   ```bash
   export RUST_LOG=off # Убрать все ошибки, предупреждения, информацию и т.д.
   ```

---

## Запуск
Для простого запуска управления робота через `ros2_control` и `teleop_twist_keyboard`
```bash
# На роботе
ros2 launch view_robot launch_robot.launch.py
# В другом теминале или устройстве
ros2 run teleop_twist_keyboard teleop_twist_keyboard   --ros-args   --remap cmd_vel:=/diff_cont/cmd_vel   -p stamped:=true   -p frame_id:=base_link
```

Можно также запустить просто launch для робота и launch для джойстика
```bash
# На роботе
ros2 launch view_robot launch_robot.launch.py
# В другом теминале другого устройства
ros2 launch view_robot launch_joy.launch.py
```

Джойстик сделан на основе `Arduino UNO R3` и `Joystick Shield V1.A`. Достаточно просто залить прошивку на неё.

Струтура топиков в обычном режиме:
```bash
ivan@ivan-HP-EliteBook-745-G6:~/ROS2-Robot$ ros2 topic list
/camera_info
/clicked_point
/controller_manager/activity
/controller_manager/introspection_data/full
/controller_manager/introspection_data/names
/controller_manager/introspection_data/values
/controller_manager/statistics/full
/controller_manager/statistics/names
/controller_manager/statistics/values
/diagnostics
/diff_cont/cmd_vel
/diff_cont/odom
/diff_cont/transition_event
/dynamic_joint_states
/goal_pose
/image_raw
/initialpose
/joint_broad/transition_event
/joint_states
/parameter_events
/robot_description
/rosout
/scan
/tf
/tf_static
```
Запущенные ноды:
```bash
admin@ROBOT:~$ ros2 node list
/controller_manager
/diff_cont
/joint_broad
/realrobot
/robot_state_publisher
/rviz
/sllidar_node
/teleop_twist_keyboard
/transform_listener_impl_5cdf62ba9850
```
## Трансформации:
![TF](./frames.png)

## Rviz demo:
![RVIZ](./rviz.png)

---

## SLAM
Используется `slam_toolbox` для построения 2d карты окрестности, но также это можно сделать и спомощью `ICP_SLAM`.
Файл с параметрами для `online_async_launch.py` находится в дириктории `config` у `view_robot` пакета.

### Запуск
```bash
ros2 launch slam_toolbox online_async_launch.py # Просто запуск со стандартными параметрами
ros2 launch slam_toolbox online_async_launch.py slam_params_file:=~/ros2_ws/src/view_robot/config/mapper_params_online_async.yaml
```

### Сохранения карты от `Slam_Toolbox`:
Откройте `Rviz2` и во вкладке `Panels` -> `Add New Panel` выберите `SlamToolbox...`
Наберите имя карты без расширения и нажнимате `save`, а потом наберите тоже имя и нажмите `serialize`.

### Публикация готовой карты
Чтобы начать пуликовать готовую карту для `AMCL` и других нод для локализации, нужно вызвать следующие команды
```bash
ros2 run nav2_map_server map_server --ros-args -p yaml_filename:=~/map.yaml # В одном терминале
ros2 run nav2_util lifecycle_bringup map_server # В другом, чтобы запустить публикацию карты
```

### AMCL
Можно использовать `AMCL` из `Nav2` стека, чтобы ориентироваться по сохраненной карте
```bash
ros2 run nav2_amcl amcl # в одном терминале
ros2 run nav2_util lifecycle_bringup amcl # В другом терминале, чтобы запустить AMCL
```

---

## ROS2 Control
https://control.ros.org/jazzy/doc/ros2_control/controller_manager/doc/userdoc.html

---

## ROS2 Joint State Broadcaster
https://control.ros.org/jazzy/doc/ros2_controllers/joint_state_broadcaster/doc/userdoc.html

---

## DiffDriveArduino Ros2 Control Plugin
https://github.com/joshnewans/diffdrive_arduino

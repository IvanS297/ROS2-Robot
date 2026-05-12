#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy
import serial
import time

class ArduinoJoyBridge(Node):
    def __init__(self):
        super().__init__('arduino_joy_bridge')
        self.publisher_ = self.create_publisher(Joy, 'joy', 10)
        self.serial_port = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        time.sleep(2) # Даем время на инициализацию Arduino
        self.timer = self.create_timer(0.02, self.read_and_publish) # 50 Гц

    def read_and_publish(self):
        if self.serial_port.in_waiting > 0:
            try:
                line = self.serial_port.readline().decode('utf-8').strip()
                if not line: return
                # Разбираем строку: X, Y, Button1, Button2, ...
                parts = line.split(',')
                if len(parts) < 2: return # Минимум две оси
                # Преобразуем в числа
                values = [float(v) for v in parts]
                msg = Joy()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.header.frame_id = "arduino_joystick"
                # Первые два значения - оси
                msg.axes = values[:2]
                # Остальные - кнопки (преобразуем в int: 1 или 0)
                msg.buttons = [int(v) for v in values[2:]] if len(values) > 2 else []
                self.publisher_.publish(msg)
                self.get_logger().debug(f'Published: axes={msg.axes}, buttons={msg.buttons}')
            except Exception as e:
                self.get_logger().error(f'Error: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = ArduinoJoyBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()

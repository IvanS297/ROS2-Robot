"""
This node maden for following the target position on different frames.
For example, robot can follow the target on frame 'map', avoid obstacles.
Or you can set target on frame 'odom' or somthing else, and robot start move straight to it.
Made by Ivan Serdyuk, 2026
"""

import rclpy
from rclpy.node import Node
from tf2_ros import TransformListener, Buffer, TransformException
from geometry_msgs.msg import PoseStamped, Pose, Point, Quaternion
from nav_msgs.msg import Path, OccupancyGrid
from tf_transformations import euler_from_quaternion, quaternion_from_euler
from visualization_msgs.msg import Marker
from std_msgs.msg import ColorRGBA, Header
import math

from .path_planner import PathPlanner

class Follower(Node):
    def __init__(self):
        super().__init__('follower')

        self.declare_parameter(name="map_topic", value="/map")
        self.declare_parameter(name="target_topic", value="/pose")

        self.map_topic = self.get_parameter(name="map_topic")
        self.target_topic = self.get_parameter(name="target_topic")

        self.target_sub = self.create_subscription(PoseStamped, "/goal_pose", self.target_update, 10)
        self.map_sub = self.create_subscription(OccupancyGrid, "/map", self.map_update, 10)

        self.start_pub = self.create_publisher(Marker, "/start", 10)
        self.goal_pub = self.create_publisher(Marker, "/goal", 10)
        self.path_pub = self.create_publisher(Path, "/pure_pursuit/path", 10)

        self.map = None
        self.goal = None
        self.prev_goal = PoseStamped()
        self.pose = None
        self.frame_id = "map"
        period = 1 / 2
        self.timer = self.create_timer(period, self.find_path)
        self.odom_timer = self.create_timer(period, self.update_odometry)

        self.tf_buffer = Buffer()
        self.tf_listenter = TransformListener(self.tf_buffer, self)

        self.get_logger().info("Node started")

    def target_update(self, msg: PoseStamped):
        self.goal = msg
        self.frame_id = msg.header.frame_id

    def map_update(self, msg: OccupancyGrid):
        self.map = msg

    def update_odometry(self):
        try:
            trans = self.tf_buffer.lookup_transform(self.frame_id, "base_link", rclpy.time.Time())
        except TransformException:
            return
        
        translation = trans.transform.translation
        rotation = trans.transform.rotation
        self.pose = Pose(position=Point(x=translation.x, y=translation.y), orientation=Quaternion(x=rotation.x, y=rotation.y, z=rotation.z, w=rotation.w))
    
    def find_path(self):
        if self.goal is not None and self.pose is not None and self.prev_goal != self.goal:
            self.get_logger().info(f"Target pose: {self.goal.pose.position.x} {self.goal.pose.position.y} {self.goal.pose.orientation.z}")
            if self.goal.header.frame_id == "map":
                cspace, cspace_cells = PathPlanner.calc_cspace(self.map, True, 4)
                cost_map = PathPlanner.calc_cost_map(self.map)
                start = PathPlanner.world_to_grid(self.map, self.pose.position)
                goal = PathPlanner.world_to_grid(self.map, self.goal.pose.position)
                path, a_star_cost, start_point, goal_point = PathPlanner.a_star(cspace, cost_map, start, goal)
                path_msg = PathPlanner.path_to_message(self.map, path)
                self.path_pub.publish(path_msg)

                self.get_logger().info(f"Frame id: map Start: {self.pose.position.x} {self.pose.position.y} {self.pose.orientation.z} Goal: {self.goal.pose.position.x} {self.goal.pose.position.y} {self.goal.pose.orientation.z} A* cost: {a_star_cost}")

            else:
                start = PoseStamped(
                    header=Header(frame_id=self.frame_id),
                        pose=Pose(
                            position=self.pose.position,         # Для self.pose (это тип Pose)
                            orientation=self.pose.orientation,
                        ),
                )
                goal = PoseStamped(
                    header=Header(frame_id=self.frame_id),
                        pose=Pose(
                            position=self.goal.pose.position,    # Для self.goal (это тип PoseStamped)
                            orientation=self.goal.pose.orientation,
                    ),
                )
                path = Path()
                path.header.stamp = self.get_clock().now().to_msg()
                path.header.frame_id = self.goal.header.frame_id
                path.poses.append(start)
                path.poses.append(goal)
                self.path_pub.publish(path)
            point_msg = Marker()
            point_msg.header.frame_id = self.frame_id
            point_msg.header.stamp = self.get_clock().now().to_msg()
            point_msg.id = 0
            point_msg.ns = 'points_ns'
            point_msg.type = Marker.POINTS
            point_msg.action = Marker.ADD
            point_msg.scale.x = 0.2
            point_msg.scale.y = 0.2
            color = ColorRGBA()
            color.r = 1.0
            color.g = 1.0
            color.b = 0.0
            color.a = 1.0
            point_msg.color = color
            point_msg.pose.orientation.w = 1.0
            p = Point()
            p.x = self.pose.position.x
            p.y = self.pose.position.y
            p.z = 0.0
            point_msg.points.clear()
            point_msg.points.append(p)
            self.start_pub.publish(point_msg)

            point_msg.header.stamp = self.get_clock().now().to_msg()
            p.x = self.goal.pose.position.x
            p.y = self.goal.pose.position.y
            color.r = 1.0
            color.g = 0.0
            color.b = 1.0
            color.a = 1.0
            point_msg.color = color
            point_msg.points.clear()
            point_msg.points.append(p)
            self.goal_pub.publish(point_msg)

            self.prev_goal = self.goal
            self.goal = None

def main(args=None):
    rclpy.init(args=args)
    node = Follower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()

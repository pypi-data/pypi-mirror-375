# ！/usr/bin/env python
# -*-coding:Utf-8 -*-
# Time: 2025/5/30 16:41
# FileName: tools
# Tools: PyCharm
# Author: chuanwen.peng
import logging
import os
import re
import time
from datetime import datetime

import uiautomator2 as u2
import xml.etree.ElementTree as ET


class AndroidControl:
    """
    AndroidControl 封装了基于 adb 和 uiautomator2 的 Android 操作接口。
    """

    def __init__(self, logger):
        """
        初始化 AndroidControl
        参数:
            logger: 用于输出日志的函数（如 print 或日志模块）
        """
        self.logger = logger
        self.devices = []
        self.device = None

    def list_available_devices(self):
        """
        列出所有可用设备
        使用 adb 命令获取连接的设备列表
        :return: 设备序列号列表
        """
        result = os.popen('adb devices -l | findstr "model"').readlines()
        if result:
            device = []
            for each in result:
                device.append(each.split()[0])
            self.logger.info("已连接设备列表为：%s" % device)
            return device
        else:
            return []

    def connect_device(self, device_id):
        """
        连接指定设备
        :param device_id: 设备序列号
        :return: True 表示连接成功，False 表示连接失败
        """
        try:
            # 使用 uiautomator2 连接设备
            self.device = u2.connect(device_id)
            self.logger.info(f"成功连接到设备：{device_id}")
            return True
        except Exception as e:
            self.logger.error(f"连接设备失败：{str(e)}")
            return False

    def list_apps(self):
        """
        列出设备上的已安装应用
        使用 uiautomator2 方法获取应用列表
        :return: 应用包名列表
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return []

        try:
            apps = self.device.app_list()
            self.logger.info(f"已安装应用列表：{apps}")
            return apps
        except Exception as e:
            self.logger.error(f"获取应用列表失败：{str(e)}")
            return []

    def launch_app(self, package_name):
        """
        启动指定应用并检查是否成功启动
        使用 uiautomator2 方法启动应用
        :param package_name: 应用的包名
        :return: True 表示启动成功，False 表示失败
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return False

        try:
            # 尝试启动应用
            self.device.app_start(package_name, wait=True)
            self.logger.info(f"尝试启动应用：{package_name}")

            # 检查启动是否成功
            current_app = self.device.app_current()
            if current_app and current_app['package'] == package_name:
                self.logger.info(f"成功启动应用：{package_name}")
                return True
            else:
                self.logger.error(f"启动应用失败：未能验证启动的应用为 {package_name}")
                return False
        except Exception as e:
            self.logger.error(f"启动应用失败：{str(e)}")
            return False

    def disable_auto_rotate(self) -> dict:
        """
        关闭设备自动旋转功能
        使用 adb 命令实现
        返回值:
            - status: 操作状态 (success/failure/error)
            - message: 状态描述信息
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return {
                "status": "failure",
                "message": "设备尚未连接"
            }

        try:
            # 使用 adb shell 命令关闭自动旋转 (0 表示关闭)
            command = f"adb -s {self.device.serial} shell settings put system accelerometer_rotation 0"
            os.system(command)
            self.logger.info("已关闭设备的自动旋转功能")
            return {
                "status": "success",
                "message": "已成功关闭设备的自动旋转功能"
            }
        except Exception as e:
            self.logger.error(f"关闭自动旋转失败：{str(e)}")
            return {
                "status": "error",
                "message": f"关闭自动旋转失败：{str(e)}"
            }

    def terminate_app(self, package_name):
        """
        停止指定应用
        使用 uiautomator2 方法停止应用
        :param package_name: 应用的包名
        :return: True 表示停止成功，False 表示失败
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return False

        try:
            self.device.app_stop(package_name)
            self.logger.info(f"成功停止应用：{package_name}")
            return True
        except Exception as e:
            self.logger.error(f"停止应用失败：{package_name}，错误：{str(e)}")
            return False

    def get_screen_size(self):
        """
        获取设备屏幕尺寸
        使用 uiautomator2 提供接口获取屏幕宽高
        :return: 宽和高 (tuple)
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return None

        try:
            screen_info = self.device.info
            width = screen_info['displayWidth']
            height = screen_info['displayHeight']
            self.logger.info(f"屏幕尺寸：Width={width}, Height={height}")
            return width, height
        except Exception as e:
            self.logger.error(f"获取屏幕尺寸失败：{str(e)}")
            return None

    def click_on_screen(self, x, y):
        """
        在指定坐标点击屏幕
        使用 uiautomator2 提供接口触摸屏幕
        :param x: X 坐标
        :param y: Y 坐标
        :return: True 表示点击成功，False 表示失败
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return False

        try:
            self.device.click(x, y)
            self.logger.info(f"屏幕点击成功，坐标：({x}, {y})")
            return True
        except Exception as e:
            self.logger.error(f"屏幕点击失败：{str(e)}")
            return False

    def list_screen_elements(self):
        """
        列出当前屏幕上的 UI 元素
        使用 uiautomator2 提供 dump_hierarchy 方法获取屏幕 XML
        :return: 元素及其相关信息的列表
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return []

        try:
            hierarchy_xml = self.device.dump_hierarchy()
            root = ET.fromstring(hierarchy_xml)

            elements = []
            for node in root.iter():
                attrib = node.attrib
                if 'text' in attrib or 'content-desc' in attrib:
                    elements.append({
                        'text': attrib.get('text'),
                        'content-desc': attrib.get('content-desc'),
                        'bounds': attrib.get('bounds')
                    })

            self.logger.info(f"屏幕元素：{elements}")
            return elements
        except Exception as e:
            self.logger.error(f"获取屏幕元素失败：{str(e)}")
            return []

    def take_screenshot(self, filename="screenshot.png"):
        """
        截取屏幕截图
        使用 uiautomator2 提供的 screenshot 方法
        :param filename: 截图文件保存路径
        :return: True 表示成功，False 表示失败
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return False

        try:
            self.device.screenshot(filename)
            self.logger.info(f"成功保存截图：{filename}")
            return True
        except Exception as e:
            self.logger.error(f"截图失败：{str(e)}")
            return False

    def set_orientation(self, orientation):
        """
        设置设备屏幕方向
        使用 uiautomator2 提供接口
        :param orientation: "portrait" 或 "landscape"
        :return: True 表示设置成功，False 表示失败
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return False

        try:
            self.device.set_orientation(orientation)
            self.logger.info(f"屏幕方向已设置为：{orientation}")
            return True
        except Exception as e:
            self.logger.error(f"设置屏幕方向失败：{str(e)}")
            return False

    def get_orientation(self):
        """
        获取设备屏幕方向
        使用 uiautomator2 提供接口
        :return: 当前屏幕方向
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return None

        try:
            orientation = self.device.orientation
            self.logger.info(f"当前屏幕方向：{orientation}")
            return orientation
        except Exception as e:
            self.logger.error(f"获取屏幕方向失败：{str(e)}")
            return None

    def press_button(self, button):
        """
        按指定按钮
        使用 uiautomator2 提供接口按下按钮
        :param button: 按钮的标识（如 "home", "back"）
        :return: True 表示按下成功，False 表示失败
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return False

        try:
            if button.lower() == "home":
                self.device.press("home")
            elif button.lower() == "back":
                self.device.press("back")
            else:
                raise ValueError(f"不支持的按钮: {button}")
            self.logger.info(f"按下按钮成功：{button}")
            return True
        except Exception as e:
            self.logger.error(f"按下按钮失败：{str(e)}")
            return False

    def open_url(self, url):
        """
        打开指定 URL 在设备浏览器中
        使用 adb 或 uiautomator2 打开的方式
        :param url: 要打开的网址
        :return: True 表示打开成功，False 表示失败
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return False

        try:
            self.device.open_url(url)
            self.logger.info(f"成功打开 URL：{url}")
            return True
        except Exception as e:
            self.logger.error(f"打开 URL 失败：{str(e)}")
            return False

    def swipe_on_screen(self, direction, distance=500, duration=0.5):
        """
        在屏幕滑动（上滑、下滑、左滑、右滑）
        使用 uiautomator2 提供接口滑动屏幕
        :param direction: 滑动方向，取值为 "up", "down", "left", "right"
        :param distance: 滑动距离（像素）
        :param duration: 滑动持续时间（秒）
        :return: True 表示滑动成功，False 表示失败
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return False

        try:
            width, height = self.get_screen_size()
            if not width or not height:
                self.logger.info("无法获取屏幕尺寸，滑动失败")
                return False

            if direction.lower() == "up":
                start_x, start_y = width // 2, height // 2 + distance // 2
                end_x, end_y = width // 2, height // 2 - distance // 2
            elif direction.lower() == "down":
                start_x, start_y = width // 2, height // 2 - distance // 2
                end_x, end_y = width // 2, height // 2 + distance // 2
            elif direction.lower() == "left":
                start_x, start_y = width // 2 + distance // 2, height // 2
                end_x, end_y = width // 2 - distance // 2, height // 2
            elif direction.lower() == "right":
                start_x, start_y = width // 2 - distance // 2, height // 2
                end_x, end_y = width // 2 + distance // 2, height // 2
            else:
                raise ValueError(f"不支持的滑动方向: {direction}")

            self.device.swipe(start_x, start_y, end_x, end_y, duration)
            self.logger.info(f"成功滑动屏幕: {direction}，起点: ({start_x}, {start_y}) -> 终点: ({end_x}, {end_y})")
            return True
        except Exception as e:
            self.logger.error(f"滑动屏幕失败：{str(e)}")
            return False

    def type_keys(self, text):
        """
        在聚焦的输入框中输入文本
        使用 uiautomator2 提供方法输入文字
        :param text: 输入的文本
        :return: True 表示输入成功，False 表示失败
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return False

        try:
            self.device.send_keys(text)
            self.logger.info(f"成功输入文本：{text}")
            return True
        except Exception as e:
            self.logger.error(f"输入文本失败：{str(e)}")
            return False

    def mobile_click_on_screen_at_coordinates(self, x, y) -> dict:
        """
        在指定的屏幕坐标点击
        参数:
            - x: X 坐标
            - y: Y 坐标
        返回值:
            - status: 操作状态 (success/failure/error)
            - message: 状态描述信息
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return {
                "status": "failure",
                "message": "设备尚未连接"
            }

        try:
            self.device.click(x, y)
            self.logger.info(f"屏幕点击成功，坐标：({x}, {y})")
            return {
                "status": "success",
                "message": f"屏幕点击成功，坐标：({x}, {y})"
            }
        except Exception as e:
            self.logger.error(f"屏幕点击失败：{str(e)}")
            return {
                "status": "error",
                "message": f"屏幕点击失败：{str(e)}"
            }

    def go_to_home(self) -> dict:
        """
        返回设备的主屏幕
        使用 uiautomator2 提供的接口模拟 HOME 按键
        返回值:
            - status: 操作状态 (success/failure/error)
            - message: 状态描述信息
        """
        if not self.device:
            self.logger.error("设备尚未连接")
            return {
                "status": "failure",
                "message": "设备尚未连接"
            }

        try:
            self.device.press("home")
            self.logger.info("成功返回主屏幕")
            return {
                "status": "success",
                "message": "成功返回主屏幕"
            }
        except Exception as e:
            self.logger.error(f"返回主屏幕失败：{str(e)}")
            return {
                "status": "error",
                "message": f"返回主屏幕失败：{str(e)}"
            }


if __name__ == '__main__':
    # 创建日志文件夹并动态生成日志文件名
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # 时间戳格式: 年-月-日-小时-分钟-秒
    log_file_path = os.path.join(log_dir, f"RobotControlServer_{current_time}.txt")

    # 创建日志记录器
    logger = logging.getLogger("RobotControlServer")  # 创建日志器
    logger.setLevel(logging.DEBUG)  # 设置日志器最低级别

    # 设置日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志输出格式
        datefmt="%Y-%m-%d %H:%M:%S"  # 时间格式
    )

    # 创建文件处理器，用于记录所有日志到文件
    file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # 文件记录所有级别日志
    file_handler.setFormatter(formatter)

    # 创建控制台处理器，用于实时输出日志到控制台
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 控制台输出 INFO 及以上级别日志
    console_handler.setFormatter(formatter)

    # 将处理器添加到日志记录器
    logger.addHandler(file_handler)  # 添加文件处理器
    logger.addHandler(console_handler)  # 添加控制台处理器
    android_control = AndroidControl(logger)

    devices = android_control.list_available_devices()
    if devices:
        android_control.connect_device(devices[0])
        ele = android_control.list_screen_elements()

        apps = android_control.list_apps()
        android_control.launch_app("com.android.settings")
        android_control.take_screenshot("example.png")

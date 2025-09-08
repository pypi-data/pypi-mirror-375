# ！/usr/bin/env python
# -*-coding:Utf-8 -*-
# Time: 2025/5/30 16:41
# FileName: server
# Tools: PyCharm
# Author: chuanwen.peng
import os
from datetime import datetime

from fastmcp import FastMCP  # MCP Framework
import logging
from mcp_android.tools import AndroidControl

# 创建日志文件夹并动态生成日志文件名
log_dir = os.path.join(os.path.dirname(__file__), "logs")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")  # 时间戳格式: 年-月-日-小时-分钟-秒
log_file_path = os.path.join(log_dir, f"AndroidControlServer_{current_time}.txt")  # 日志文件路径

# 创建日志记录器
logger = logging.getLogger("AndroidControlServer")
logger.setLevel(logging.DEBUG)  # 设置日志器的最低级别

# 设置日志格式
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # 日志输出格式
    datefmt="%Y-%m-%d %H:%M:%S"  # 时间格式
)

# 文件日志处理器（记录所有级别日志到一个文件）
file_handler = logging.FileHandler(log_file_path, mode="a", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)  # 记录所有级别日志
file_handler.setFormatter(formatter)

# 控制台日志处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # 控制台仅显示 INFO 及以上日志
console_handler.setFormatter(formatter)

# 添加处理器到日志记录器
logger.addHandler(file_handler)  # 添加文件日志处理器
logger.addHandler(console_handler)  # 添加控制台日志处理器

# 初始化 MCP 服务
mcp = FastMCP("Android Control MCP Server")

# 初始化 Android 控制实例
android_control = AndroidControl(logger)

# 定义所有工具
@mcp.tool()
def mobile_list_available_devices() -> dict:
    """
    列出所有可用设备
    返回值:
        - status: 操作状态 (success/failure/error)
        - devices: 可用设备列表 (当status为success时)
        - message: 状态描述信息
    """
    try:
        devices = android_control.list_available_devices()
        if devices:
            return {
                "status": "success",
                "devices": devices,
                "message": f"已连接设备列表：{devices}"
            }
        else:
            return {
                "status": "failure",
                "message": "未检测到任何设备连接"
            }
    except Exception as e:
        logger.error(f"获取设备列表时发生异常: {str(e)}")
        return {"status": "error", "message": str(e)}


@mcp.tool()
def mobile_select_device(device_id: str) -> dict:
    """
    选择设备进行操作
    参数:
        - device_id: 设备ID字符串
    返回值:
        - status: 操作状态 (success/failure/error)
        - message: 状态描述信息
    """
    try:
        result = android_control.connect_device(device_id)
        if result:
            return {"status": "success", "message": f"成功选择设备 {device_id}"}
        else:
            return {"status": "failure", "message": f"选择设备 {device_id} 失败"}
    except Exception as e:
        logger.error(f"选择设备时发生异常: {str(e)}")
        return {"status": "error", "message": str(e)}


@mcp.tool()
def mobile_list_apps() -> dict:
    """
    列出已安装应用
    返回值:
        - status: 操作状态 (success/failure/error)
        - apps: 应用列表 (当status为success时)
        - message: 状态描述信息
    """
    try:
        apps = android_control.list_apps()
        if apps:
            return {
                "status": "success",
                "apps": apps,
                "message": "成功获取已安装应用列表"
            }
        else:
            return {
                "status": "failure",
                "message": "未能检测到任何已安装应用"
            }
    except Exception as e:
        logger.error(f"获取已安装应用列表时发生异常: {str(e)}")
        return {"status": "error", "message": str(e)}


@mcp.tool()
def mobile_launch_app(package_name: str) -> dict:
    """
    启动指定应用
    参数:
        - package_name: 应用的包名（如 "com.android.settings"）
    返回值:
        - status: 成功为 "success"，失败为 "failure"，异常为 "error"。
        - message: 具体的操作结果或错误信息。
    """
    try:
        result = android_control.launch_app(package_name)
        if result:
            return {"status": "success", "message": f"成功启动应用包名 {package_name}"}
        else:
            return {"status": "failure", "message": f"启动应用包名 {package_name} 失败"}
    except Exception as e:
        logger.error(f"启动应用包名时发生异常: {str(e)}")
        return {"status": "error", "message": str(e)}


@mcp.tool()
def mobile_terminate_app(package_name: str) -> dict:
    """
    停止指定应用
    参数:
        - package_name: 应用的包名（如 "com.android.settings"）
    返回值:
        - status: 成功为 "success"，失败为 "failure"，异常为 "error"。
        - message: 具体的操作结果或错误信息。
    """
    try:
        result = android_control.terminate_app(package_name)
        if result:
            return {"status": "success", "message": f"成功停止应用包名 {package_name}"}
        else:
            return {"status": "failure", "message": f"停止应用包名 {package_name} 失败"}
    except Exception as e:
        logger.error(f"停止应用包名时发生异常: {str(e)}")
        return {"status": "error", "message": str(e)}


@mcp.tool()
def mobile_get_screen_size() -> dict:
    """
    获取屏幕尺寸
    返回值:
        - status: 操作状态 (success/failure/error)
        - dimensions: 屏幕尺寸对象 (当status为success时)
            - width: 屏幕宽度
            - height: 屏幕高度
        - message: 状态描述信息
    """
    try:
        dimensions = android_control.get_screen_size()
        if dimensions:
            width, height = dimensions
            return {
                "status": "success",
                "dimensions": {"width": width, "height": height},
                "message": "成功获取屏幕尺寸"
            }
        else:
            return {
                "status": "failure",
                "message": "屏幕尺寸获取失败"
            }
    except Exception as e:
        logger.error(f"获取屏幕尺寸时发生异常: {str(e)}")
        return {"status": "error", "message": str(e)}


@mcp.tool()
def mobile_click_on_screen(x: int, y: int) -> dict:
    """
    在屏幕特定坐标点击
    参数:
        - x: 点击位置的X坐标
        - y: 点击位置的Y坐标
    返回值:
        - status: 操作状态 (success/failure/error)
        - message: 状态描述信息
    """
    try:
        result = android_control.click_on_screen(x, y)
        if result:
            return {"status": "success", "message": f"成功点击屏幕坐标 ({x}, {y})"}
        else:
            return {"status": "failure", "message": f"点击屏幕坐标 ({x}, {y}) 失败"}
    except Exception as e:
        logger.error(f"点击屏幕时发生异常: {str(e)}")
        return {"status": "error", "message": str(e)}


@mcp.tool()
def mobile_swipe_screen(direction: str, distance: int, duration: float) -> dict:
    """
    滑动屏幕
    参数:
        - direction: 滑动方向 (up/down/left/right)
        - distance: 滑动距离(像素)
        - duration: 滑动持续时间(秒)
    返回值:
        - status: 操作状态 (success/failure/error)
        - message: 状态描述信息
    """
    try:
        result = android_control.swipe_on_screen(direction, distance, duration)
        if result:
            return {
                "status": "success",
                "message": f"成功滑动屏幕 {direction}，距离: {distance}，持续时间: {duration}s"
            }
        else:
            return {
                "status": "failure",
                "message": f"滑动屏幕 {direction} 时失败"
            }
    except Exception as e:
        logger.error(f"滑动屏幕时发生异常: {str(e)}")
        return {"status": "error", "message": str(e)}


@mcp.tool()
def mobile_press_button(button: str) -> dict:
    """
    按下指定按钮
    参数:
        - button: 按钮名称 (如 "HOME", "BACK")
    返回值:
        - status: 操作状态 (success/failure/error)
        - message: 状态描述信息
    """
    try:
        result = android_control.press_button(button)
        if result:
            return {"status": "success", "message": f"成功按下按钮 {button}"}
        else:
            return {"status": "failure", "message": f"按下按钮 {button} 失败"}
    except Exception as e:
        logger.error(f"按下按钮时发生异常: {str(e)}")
        return {"status": "error", "message": str(e)}


@mcp.tool()
def mobile_take_screenshot(file_path: str = "screenshot.png") -> dict:
    """
    截取屏幕截图
    参数:
        - file_path: 截图保存路径 (可选，默认为"screenshot.png")
    返回值:
        - status: 操作状态 (success/failure/error)
        - file_path: 截图文件路径 (当status为success时)
        - message: 状态描述信息
    """
    try:
        result = android_control.take_screenshot(file_path)
        if result:
            return {
                "status": "success",
                "file_path": file_path,
                "message": "成功截取屏幕截图"
            }
        else:
            return {
                "status": "failure",
                "message": "截取屏幕截图失败"
            }
    except Exception as e:
        logger.error(f"截取屏幕截图时发生异常: {str(e)}")
        return {"status": "error", "message": str(e)}


@mcp.tool()
def list_screen_elements() -> dict:
    """
    列出当前屏幕上的 UI 元素
    调用 android_control 提供的 list_screen_elements 方法获取屏幕元素列表
    返回值:
        - status: 操作状态 (success/failure/error)
        - elements: 屏幕元素列表 (当 status 为 success 时)
        - message: 状态描述信息
    """
    try:
        # 调用 android_control 的 list_screen_elements 方法
        result = android_control.list_screen_elements()
        if result:
            return {
                "status": "success",
                "elements": result,
                "message": "成功获取屏幕元素"
            }
        else:
            return {
                "status": "failure",
                "message": "无法获取屏幕元素"
            }
    except Exception as e:
        # 捕获异常并记录日志
        logger.error(f"获取屏幕元素时发生异常: {str(e)}")
        return {"status": "error", "message": str(e)}


@mcp.tool()
def mobile_click_on_screen_at_coordinates(x: int, y: int) -> dict:
    """
    在屏幕指定坐标 (x, y) 点击
    参数:
        - x: 点击位置的X坐标
        - y: 点击位置的Y坐标
    返回值:
        - status: 操作状态 (success/failure/error)
        - message: 状态描述信息
    """
    try:
        result = android_control.mobile_click_on_screen_at_coordinates(x, y)
        if result["status"] == "success":
            return {
                "status": "success",
                "message": f"成功点击屏幕坐标 ({x}, {y})"
            }
        else:
            return {
                "status": result["status"],
                "message": result["message"]
            }
    except Exception as e:
        logger.error(f"点击屏幕时发生异常: {str(e)}")
        return {
            "status": "error",
            "message": f"点击屏幕时发生异常: {str(e)}"
        }


@mcp.tool()
def mobile_go_to_home() -> dict:
    """
    返回设备的主屏幕
    返回值:
        - status: 操作状态 (success/failure/error)
        - message: 状态描述信息
    """
    try:
        result = android_control.go_to_home()
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "成功返回主屏幕"
            }
        else:
            return {
                "status": result["status"],
                "message": result["message"]
            }
    except Exception as e:
        logger.error(f"返回主屏幕时发生异常: {str(e)}")
        return {
            "status": "error",
            "message": f"返回主屏幕时发生异常: {str(e)}"
        }


@mcp.tool()
def mobile_disable_auto_rotate() -> dict:
    """
    关闭设备的自动旋转功能
    返回值:
        - status: 操作状态 (success/failure/error)
        - message: 状态描述信息
    """
    try:
        result = android_control.disable_auto_rotate()
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "成功关闭设备的自动旋转功能"
            }
        else:
            return {
                "status": result["status"],
                "message": result["message"]
            }
    except Exception as e:
        logger.error(f"关闭设备自动旋转时发生异常: {str(e)}")
        return {
            "status": "error",
            "message": f"关闭设备自动旋转时发生异常: {str(e)}"
        }


def run_server():
    '''
    启动 MCP 服务
    :return:
    '''
    logger.info("MCP 服务启动...")
    mcp.run()  # 启动 MCP 服务

# MCP 服务运行
if __name__ == "__main__":
    run_server()

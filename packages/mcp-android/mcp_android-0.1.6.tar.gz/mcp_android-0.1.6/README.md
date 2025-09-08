# MCP-Android

## 项目简介
MCP-Android 是一个基于 MCP 框架开发的 Android 控制服务，支持以下功能：
- 设备管理：列出设备，选择设备。
- 应用管理：列出应用、启动应用、停止应用。
- 屏幕操作：点击屏幕、滑动屏幕、获取屏幕大小。
- 系统设置：关闭自动旋转、返回主屏幕。

## 如何运行
1. 激活虚拟环境：
D:\McpTool\mcp-android.venv\Scripts\activate


2. 安装依赖：
pip install -r pyproject.toml


3. 启动 MCP 服务：
python src/mcp_android/server.py


4. 使用 Postman 或其他客户端访问服务端口（默认 `8000`）。

## 工具功能

### 举例: 列出可用设备
- 请求方法：`GET /mobile_list_available_devices`
- 返回值示例：
```json
{
"status": "success",
"devices": ["device_serial_1", "device_serial_2"],
"message": "已连接设备列表：[device_serial_1, device_serial_2]"
}

---

### 方法 7: 测试 MCP 服务
你可以编写测试代码来验证服务是否集成成功。

#### 调试和测试:
在 `server.py` 中增加启动时调试日志:
```python
if __name__ == "__main__":
    logger.info("MCP 服务正在启动...")
    mcp.run()
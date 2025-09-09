#!/usr/bin/env python3
"""
优测UBox UBox 示例文件

展示三种不同的初始化模式：
1. 调试模式（自动占用设备）- 正常都使用调试模式
2. 调试模式（使用预获取的authCode）- 跳过占用流程
3. 执行模式 - 仅用于自动化脚本上传到平台执行

包含完整的功能演示和时间监控功能。
"""

import sys
import os
import time
import traceback
import uuid

from examples.config import get_ubox_config, get_device_config
from ubox_py_sdk.handler import find_optimal_element, parse_xml, EventHandler

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ubox_py_sdk import UBox, RunMode, OSType, operation_timer
from ubox_py_sdk.models import DeviceButton, DriverType

# 从配置文件获取UBox配置
ubox_config = get_ubox_config()
device_config = get_device_config()


# ==================== 功能演示函数 ====================
def demo_device_info(device):
    """设备信息相关功能演示"""
    print("\n--- 设备信息相关 ---")
    try:
        with operation_timer("获取设备信息"):
            device_info = device.device_info()
            if device_info:
                print(f"设备型号: {device_info.get('model', 'Unknown')}")
                display = device_info.get('display', {})
                print(f"屏幕分辨率: {display.get('width', 0)}x{display.get('height', 0)}")
            auth_info = device.get_auth_info()
            if auth_info:
                print(f"authCode: {auth_info.get('authCode', 'Unknown')}")
                print(f"udid: {auth_info.get('udid', 'Unknown')}")
    except Exception as e:
        print(f"设备信息获取失败: {e}")


def demo_ui_tree_info(device):
    print("\n--- ui_tree相关 ---")
    try:
        with operation_timer("获取uitree-xml信息"):
            device.ios_open_url(
                "https://datong-picture-1258344701.cos.ap-guangzhou.myqcloud.com/scan/dist/index.html?dt_debugid=zhenxichen_17e59a&dt_appid=RUiWu5Po&a_appkey=00000VAFHI3U915P&i_appkey=0P0008DK283CA2PS&h_appkey=0HAR060G0XEC8X4W")
        # with operation_timer("获取uitree-json信息"):
        #     json_xml_tree = device.get_uitree()
        #     print(f"json_xml_tree: {json_xml_tree[:50]}")
        # with operation_timer("find"):
        #     xml_tree = device.find_ui("//*[@text='打开URL']",timeout=10)
        #     print(f"xml_tree: {xml_tree}")
    except Exception as e:
        print(f"ui_tree获取失败: {e}\n{traceback.format_exc()}")


def demo_screenshot_recording(device):
    """截图录制相关功能演示"""
    print("\n--- 截图录制相关 ---")
    try:
        # 截图并下载
        with operation_timer("截图下载"):
            screenshot_result = device.screenshot(label="demo", img_path="./screenshots")
            print(f"截图下载: {screenshot_result.get('img_path', 'N/A')}")

        # Base64截图
        with operation_timer("Base64截图"):
            base64_image = device.screenshot_base64()
            print(f"Base64截图长度: {len(base64_image)}")

        # 开始录制
        # with operation_timer("开始录制"):
        #     record_id = device.record_start(video_path="./recordings/demo.mp4")
        #     print(f"录制开始: {record_id}")
        #
        # # 停止录制
        # time.sleep(2)  # 等待2秒
        # with operation_timer("停止录制"):
        #     record_result = device.record_stop(record_id)
        #     print(f"录制停止: {record_result.get('videoUrl', 'N/A')}")
        #     print(f"录制文件: {record_result.get('video_path', 'N/A')}")

    except Exception as e:
        print(f"截图录制失败: {e}")


def demo_click_operations(device):
    """点击操作相关功能演示"""
    print("\n--- 点击操作相关 ---")
    try:
        # 坐标点击
        # with operation_timer("坐标点击"):
        #     success = device.click_pos([0.5, 0.5])
        #     print(f"坐标点击: {success}")
        # 坐标点击
        with operation_timer("坐标点击"):
            success = device.click_pos([724, 2063])
            print(f"坐标点击: {success}")

        # 双击
        with operation_timer("双击操作"):
            success = device.click_pos([0.5, 0.9], times=2)
            print(f"双击: {success}")

        # 长按
        with operation_timer("长按操作"):
            success = device.click_pos([0.9, 0.1], duration=2.0)
            print(f"长按: {success}")

        # 基于控件点击
        with operation_timer("控件点击"):
            success = device.click(
                loc="//*[@content-desc='扫一扫']",
                by=DriverType.UI
            )
            print(f"控件点击: {success}")

        # 基于图像匹配点击
        with operation_timer("图像匹配点击"):
            success = device.click(
                loc="button_image.png",
                by=DriverType.CV,
                timeout=10
            )
            print(f"图像匹配点击: {success}")

        # 基于文字识别点击
        with operation_timer("文字识别点击"):
            success = device.click(
                loc="登录",
                by=DriverType.OCR
            )
            print(f"文字识别点击: {success}")

        # 长按操作
        with operation_timer("长按控件操作"):
            success = device.long_click(
                loc="//*[@content-desc='扫一扫']",
                by=DriverType.UI,
                duration=3.0
            )
            print(f"长按操作: {success}")

    except Exception as e:
        print(f"点击操作失败: {e}")


def demo_slide_operations(device):
    """滑动操作相关功能演示"""
    print("\n--- 滑动操作相关 ---")
    try:
        # 坐标滑动 - 使用绝对坐标
        with operation_timer("左右滑动"):
            success = device.slide_pos([0.1, 0.5], [0.9, 0.5])
            print(f"左右滑动: {success}")

        with operation_timer("上下滑动"):
            success = device.slide_pos([0.5, 0.1], [0.5, 0.9])
            print(f"上下滑动: {success}")

        # # 坐标滑动 - 对角线滑动
        # with operation_timer("对角线滑动"):
        #     success = device.slide_pos([0.1, 0.1], [0.9, 0.9])
        #     print(f"对角线滑动: {success}")
        #
        # # 坐标滑动 - 带拖拽效果
        # with operation_timer("拖拽滑动"):
        #     success = device.slide_pos([0.5, 0.9], [0.5, 0.1], down_duration=0.5)
        #     print(f"拖拽滑动: {success}")

        # # 元素滑动 - 基于控件
        # with operation_timer("控件间滑动"):
        #     success = device.slide(
        #         loc_from="//XCUIElementTypeButton[@label='开始']",
        #         loc_to="//XCUIElementTypeButton[@label='结束']",
        #         by=DriverType.UI
        #     )
        #     print(f"控件间滑动: {success}")
        #
        # # 元素滑动 - 基于图像匹配
        # with operation_timer("图像间滑动"):
        #     success = device.slide(
        #         loc_from="start_image.png",
        #         loc_to="end_image.png",
        #         by=DriverType.CV
        #     )
        #     print(f"图像间滑动: {success}")
        #
        # # 元素滑动 - 基于文字识别
        # with operation_timer("文字间滑动"):
        #     success = device.slide(
        #         loc_from="登录",
        #         loc_to="注册",
        #         by=DriverType.OCR
        #     )
        #     print(f"文字间滑动: {success}")

    except Exception as e:
        print(f"滑动操作失败: {e}")


def demo_text_input(device):
    """文本输入相关功能演示"""
    print("\n--- 文本输入相关 ---")
    try:
        with operation_timer("基本文本输入"):
            success = device.input_text("Hello World")
            print(f"基本文本输入: {success}")

        with operation_timer("带超时文本输入"):
            success = device.input_text("测试文本", timeout=60)
            print(f"带超时文本输入: {success}")

        with operation_timer("调整深度文本输入"):
            success = device.input_text("复杂文本", timeout=30, depth=15)
            print(f"调整深度文本输入: {success}")

    except Exception as e:
        print(f"文本输入失败: {e}")


def demo_key_operations(device):
    """按键操作相关功能演示"""
    print("\n--- 按键操作相关 ---")
    try:
        with operation_timer("返回键"):
            success = device.press(DeviceButton.BACK)
            print(f"返回键: {success}")

        with operation_timer("Home键"):
            success = device.press(DeviceButton.HOME)
            print(f"Home键: {success}")

        with operation_timer("音量上键"):
            success = device.press(DeviceButton.VOLUME_UP)
            print(f"音量上键: {success}")

        with operation_timer("音量下键"):
            success = device.press(DeviceButton.VOLUME_DOWN)
            print(f"音量下键: {success}")

    except Exception as e:
        print(f"按键操作失败: {e}")


def demo_app_management(device):
    """应用管理相关功能演示"""
    print("\n--- 应用管理相关 ---")
    try:
        with operation_timer("当前界面应用"):
            current_app = device.current_app()
            print(f"当前界面应用: {current_app}")
        with operation_timer("当前运行中app list"):
            app_list_running = device.app_list_running()
            print(f"当前运行中app list: {app_list_running}")
        # if device.os_type == OSType.IOS:
        #     bundle_id = "com.apple.AppStore"
        # else:
        #     bundle_id = "com.wudaokou.hippo"
        #
        # with operation_timer("启动应用"):
        #     success = device.start_app(bundle_id)
        #     print(f"启动应用: {success}")
        #
        # if device.os_type in [OSType.ANDROID, OSType.HM]:
        #     with operation_timer("清除数据启动应用"):
        #         success = device.start_app(bundle_id, clear_data=True)
        #         print(f"清除数据启动: {success}")
        #
        # # 等待应用启动
        # time.sleep(2)
        #
        # # 测试停止应用
        # with operation_timer("停止应用"):
        #     success = device.stop_app(bundle_id)
        #     print(f"停止应用: {success}")

    except Exception as e:
        print(f"应用管理失败: {e}")


def demo_commands(device):
    """cmd命令相关功能演示"""
    print("\n--- cmd命令相关 ---")
    try:
        # with operation_timer("获取设备型号"):
        #     result = device.cmd_adb("getprop ro.product.model")
        #     print(f"设备型号: {result}")
        #
        # with operation_timer("获取当前activity"):
        #     result = device.cmd_adb("dumpsys activity activities | grep mResumedActivity")
        #     print(f"当前activity: {result}")
        #
        # with operation_timer("获取已安装包列表"):
        #     result = device.cmd_adb("pm list packages", timeout=30)
        #     print(f"已安装包数量: {len(str(result).split())}")
        #
        # with operation_timer("获取设备属性"):
        #     result = device.cmd_adb("getprop")
        #     print(f"设备属性数量: {len(str(result).split())}")

        with operation_timer("打开优测网页"):
            result = device.cmd_adb(
                "am start 'txdt00000vafhi3u915p://visual_debug?dt_debugid=zhenxichen_76edf6\&dt_appid=RUiWu5Po'")
            print(f"打开优测网页: {result}")

    except Exception as e:
        print(f"ADB命令失败: {e}")


def demo_advanced_features(device):
    """高级功能演示"""
    print("\n--- 高级功能 ---")
    try:
        # # 图像查找
        # with operation_timer("图像查找"):
        #     result = device.find_cv(
        #         tpl="template_image.png",
        #         threshold=0.8,
        #         timeout=30
        #     )
        #     print(f"图像查找: {result}")

        # OCR文字查找
        with operation_timer("OCR文字查找"):
            result = device.find_ocr(
                word="图库",
                timeout=30
            )
            print(f"OCR查找: {result}")

        # UI控件查找
        with operation_timer("UI控件查找"):
            result = device.find_ui(
                xpath="//*[@content-desc='扫一扫']",
                timeout=30
            )
            print(f"UI控件查找: {result}")

        # # 获取控件树
        # with operation_timer("获取控件树"):
        #     result = device.get_uitree(xml=False)
        #     print(f"控件树获取成功，节点数量: {len(str(result))}")

        # # 获取图像文本
        # with operation_timer("图像文本识别"):
        #     result = device.get_text("screenshot.png", iou_th=0.1)
        #     print(f"图像文本识别: {result}")

        # 剪贴板操作
        with operation_timer("设置剪贴板"):
            device.set_clipboard("测试文本")
            print(f"设置剪贴板成功")

        with operation_timer("获取剪贴板"):
            clipboard_text = device.get_clipboard()
            print(f"剪贴板内容: {clipboard_text}")

        # # 等待页面空闲
        # with operation_timer("等待页面空闲"):
        #     result = device.wait_for_idle(idle_time=1.0, timeout=10.0)
        #     print(f"页面空闲状态: {result}")

    except Exception as e:
        print(f"高级功能失败: {e}")


def demo_install_app_features(device):
    """安装卸载功能展示"""
    print("\n--- 安装卸载功能 ---")
    try:

        # default_rules = [
        #     '^(已知悉该应用存在风险｜仍然继续｜授权本次安装|同意)$',
        #     ('(仅充电|仅限充电|传输文件)', '取消'),
        # ]
        # device.load_default_handler(default_rules)
        # device.start_event_handler()
        # 安装app
        with operation_timer("安装app"):
            result = device.install_app(
                app_url="https://utest-upload-file-1254257443.cos.ap-guangzhou.myqcloud.com/user_upload_file_dir/2025-08-28/d365f9a1b2974c2cb75c38fda2750567/TencentVideo_V9.01.65.30262_20563.apk"
            )
            print(f"安装app: {result}")
        time.sleep(3)
        # 卸载app
        with operation_timer("卸载app"):
            result = device.uninstall_app(
                pkg="com.example.demo"
            )
            print(f"卸载app: {result}")

    except Exception as e:
        print(f"安装卸载功能失败: {e}")


def comprehensive_demo(device):
    """完整功能演示 - 调用所有模块的演示函数"""
    print("\n=== 完整功能演示 ===")
    # 调用各个功能模块的演示函数
    # demo_ui_tree_info(device)  # ui相关
    # demo_device_info(device)  # 设备信息相关
    # demo_screenshot_recording(device)  # 截图录制相关
    # demo_click_operations(device)  # 点击操作相关
    # demo_slide_operations(device)  # 滑动操作相关
    # demo_text_input(device)  # 文本输入相关
    # demo_key_operations(device)  # 按键操作相关
    demo_app_management(device)  # 应用管理相关
    # demo_commands(device)  # ADB命令相关
    # demo_advanced_features(device)  # 高级功能
    # demo_install_app_features(device)  # 安装卸载


# ==================== 三种初始化模式示例 ====================
def demo_debug_mode_auto_occupy():
    try:
        # 创建SDK实例（调试模式）
        ubox = UBox(
            # 使用时按这个注释写
            # secret_id="xxx",
            # secret_key="xxx",
            mode=ubox_config.get("mode", RunMode.NORMAL),
            base_url=ubox_config.get("base_url", ''),
            secret_id=ubox_config.get('secret_id'),
            secret_key=ubox_config.get('secret_key'),
            log_level="debug",
            log_to_file=True
        )
        print("\n正在初始化设备...")
        device = ubox.init_device(
            # 使用时按这个注释写
            # udid="your_device_udid_here",
            # os_type=OSType.ANDROID
            udid=device_config['default_udid'],
            os_type=OSType(device_config['default_os_type']),
            auth_code=device_config.get('auth_code', None),
        )
        print(f"设备初始化成功: {device.udid}")
        print(f"设备类型: {device.os_type.value}")
        print(f"Debug ID: {getattr(device, 'debugId', 'N/A')}")

        # 执行功能演示
        comprehensive_demo(device)

        print("\n" + "=" * 80)
        print("注意：设备会自动释放，无需手动操作")
        print("=" * 80)

    except Exception as e:
        print(f"❌ 示例执行失败: {e}\n{traceback.format_exc()}")

    finally:
        # 关闭客户端
        try:
            ubox.close()
            print("SDK已关闭")
        except:
            pass


# ==================== 上下文管理器使用示例 ====================
def demo_context_manager_usage():
    """上下文管理器使用示例 - 推荐的使用方式"""
    print("\n" + "=" * 80)
    print("上下文管理器使用示例")
    print("=" * 80)
    print("使用上下文管理器（with语句）是推荐的使用方式，可以自动管理资源")

    # 示例1：默认模式（自动占用设备）
    print("\n1. 默认模式（自动占用设备）示例：")
    try:
        with UBox(
                # 使用时按这个注释写
                # secret_id="xxx",
                # secret_key="xxx",
                secret_id=ubox_config.get('secret_id'),
                secret_key=ubox_config.get('secret_key'),
        ) as ubox:
            print(f"SDK创建成功，模式: {ubox.mode.value}")

            # 初始化设备
            device = ubox.init_device(
                # 使用时按这个注释写
                # udid="your_device_udid_here",
                # os_type=OSType.ANDROID
                udid=device_config['default_udid'],
                os_type=OSType(device_config['default_os_type']),
            )
            print(f"设备初始化成功: {device.udid}")

            # 执行一些操作
            with operation_timer("获取设备信息"):
                device_info = device.device_info()
                if device_info:
                    print(f"设备型号: {device_info.get('model', 'Unknown')}")

            with operation_timer("截图操作"):
                screenshot_result = device.screenshot("demo", "./screenshots")
                print(f"截图成功: {screenshot_result.get('imageUrl', 'N/A')}")

            print("注意：使用with语句，无需手动调用ubox.close()")

    except Exception as e:
        print(f"❌ 示例执行失败: {e}")

    # 示例2：默认模式（使用预获取的authCode）
    print("\n2. 默认模式（使用预获取的authCode）示例：")
    try:
        with UBox(
                # 使用时按这个注释写
                # secret_id="xxx",
                # secret_key="xxx",
                secret_id=ubox_config.get('secret_id'),
                secret_key=ubox_config.get('secret_key'),
        ) as ubox:
            print(f"SDK创建成功，模式: {ubox.mode.value}")

            # 使用预获取的authCode初始化设备
            device = ubox.init_device(
                # 使用时按这个注释写
                # udid="your_device_udid_here",
                # os_type=OSType.ANDROID
                # auth_code="xxxd2c-8497-15556a0a62f0_20250822142144"
                udid=device_config['default_udid'],
                os_type=OSType(device_config['default_os_type']),
                auth_code=device_config.get('auth_code')
            )
            print(f"设备初始化成功: {device.udid}")

            # 执行一些操作
            with operation_timer("左右滑动"):
                success = device.slide_pos([0.1, 0.5], [0.9, 0.5])
                print(f"左右滑动: {success}")

            print("注意：使用with语句，无需手动调用ubox.close()")

    except Exception as e:
        print(f"❌ 示例执行失败: {e}")

    # 示例3：本地模式
    print("\n3. 本地模式：")
    try:
        with UBox(
                # 使用时按这个注释写
                mode=RunMode.LOCAL,
                # secret_id="your_secret_id_here",
                # secret_key="your_secret_key_here",
                secret_id=ubox_config.get('secret_id'),
                secret_key=ubox_config.get('secret_key'),
        ) as ubox:
            print(f"SDK创建成功，模式: {ubox.mode.value}")

            # 初始化设备
            device = ubox.init_device(
                # 使用时按这个注释写
                # udid="your_device_udid_here",
                # os_type=OSType.ANDROID
                udid=device_config['default_udid'],
                os_type=OSType(device_config['default_os_type'])
            )
            print(f"设备初始化成功: {device.udid}")

            # 执行一些操作
            with operation_timer("获取设备信息"):
                device_info = device.device_info()
                if device_info:
                    print(f"设备型号: {device_info.get('model', 'Unknown')}")

            print("注意：使用with语句，无需手动调用ubox.close()")

    except Exception as e:
        print(f"❌ 示例执行失败: {e}")

    print("\n" + "=" * 80)
    print("上下文管理器示例执行完成！")
    print("总结：使用with语句是推荐的方式，更安全、更简洁")
    print("=" * 80)


# ==================== 主函数 ====================
def main():
    print()
    print(f"使用配置: {ubox_config['mode']}")
    print(f"设备UDID: {device_config['default_udid']}")
    print(f"设备类型: {device_config['default_os_type']}")
    print(f"auto_code: {device_config.get('auth_code', '')}")
    print()
    # 运行上下文管理器示例（推荐）
    # demo_context_manager_usage()
    demo_debug_mode_auto_occupy()


if __name__ == "__main__":
    main()

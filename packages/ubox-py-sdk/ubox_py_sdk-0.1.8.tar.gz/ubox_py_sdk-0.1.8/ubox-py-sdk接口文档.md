# ubox python sdk 调用文档

> 本 UBox 需要依赖实验室，并非可脱离实验室本地使用的。

## Demo

> 架构说明：
>
> - 默认模式：包含占用&续期&释放设备，如果传authcode后则不再占用释放
> - 本地模式：直接本地访问，本地编写自动化脚本时使用
> - 设备信息：支持三端（iOS、HarmonyOS、Android）共用的详细信息
> - 失败会抛出异常

```python
def example_debug_mode():
  print("=== 调试模式示例 ===")

  # 创建调试模式客户端
  client = UBox(
    secret_id="your_secret_id_here",
    secret_key="your_secret_key_here",
  )

  print(f"模式: {client.mode.value}")

  try:
    # 初始化多个设备
    device1 = client.init_device(udid="device-001-udid", os_type=OSType.ANDROID)
    device2 = client.init_device(udid="device-002-udid", os_type=OSType.IOS)
    print(f"已初始化 {len(client._devices)} 台设备")

    # 获取设备信息
    device_info1 = device1.device_info()
    device_info2 = device2.device_info()

    # 展示设备1的详细信息
    print(f"\n设备1详细信息:")
    print(f"  设备标识: {device_info1.serial}")
    print(f"  设备型号: {device_info1.model}")

    # 展示设备2的详细信息
    print(f"\n设备2详细信息:")
    print(f"  设备标识: {device_info2.serial}")
    print(f"  设备型号: {device_info2.model}")

  except Exception as e:
    print(f"❌ 操作失败: {e}")

  finally:
    # 关闭客户端会自动释放所有设备,也可逐个设备释放
    client.close()

```

## 设备信息相关

### 1、device_info()

获取设备的基本信息，包括显示分辨率、型号、版本、CPU 和内存等。

**参数：**

- 无

**返回值：**

```python
dict: 包含设备信息的字典
{
    "display": {
        "width": 0,      # 屏幕宽度
        "height": 0      # 屏幕高度
    },
    "model": "",         # 设备型号
    "version": "",       # 系统版本
    "cpu": {
        "cores": ""      # CPU核心数
    },
    "memory": {
        "total": 0       # 总内存大小
    }
}
```

### 2、设备列表功能

```python
from ubox_py_sdk import UBox, PhonePlatform
from ubox_py_sdk.models import DeviceListResponse

with UBox(secret_id="your_id", secret_key="your_key") as ubox:
    android_devices: DeviceListResponse = ubox.device_list(
        page_num=1,
        page_size=10,
        phone_platform=[PhonePlatform.ANDROID]  # 使用枚举值
    )
    print(f"Android设备数量: {android_devices.data.total}")
    
   
    response: DeviceListResponse = ubox.device_list(
        page_num=1,
        page_size=15,
        phone_platform=[PhonePlatform.ANDROID, PhonePlatform.IOS],  # Android和iOS
        manufacturers=["Redmi", "Xiaomi"],
        resolution_ratios=["720*1600", "1080*2376"]
    )
    
    # 从响应中提取设备信息（使用类型安全的模型）
    device_list = response.data.list
    total_devices = response.data.total
    current_page = response.data.pageNum
    page_size = response.data.pageSize
    
    # 遍历设备列表
    for device in device_list:
        print(f"设备: {device.manufacturer} {device.modelKind}")
        print(f"  UDID: {device.udid}")
        print(f"  平台: {device.osType}")  # 1=Android, 2=iOS, 3=鸿蒙, 4=鸿蒙NEXT
        print(f"  分辨率: {device.resolutionRatio}")
        print(f"  在线状态: {'在线' if device.onlineStatus == 1 else '离线'}")
```

#### PhonePlatform 枚举值说明

- `PhonePlatform.ANDROID = 1`: Android设备
- `PhonePlatform.IOS = 2`: iOS设备  
- `PhonePlatform.HARMONYOS = 3`: 鸿蒙设备
- `PhonePlatform.HARMONYOS_NEXT = 4`: 鸿蒙NEXT设备

### 3、获取占用后的设备auth_code

```python
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

```


## 录屏相关

### 1、record_start(video_path: str)

开始录制设备屏幕。

**参数：**

- video_path: 指定录屏的输出文件路径

**返回值：**

```python
dict: 包含设备信息的字典
{
    "record_id": "id",        # 录制屏幕任务的唯一id
    "msg": "err msg"          # 录制失败的提示信息
}
```

### 2、record_stop(record_id: str)

停止录制设备屏幕。

**参数：**

- `record_id`: str 录制屏幕任务的唯一 id

**返回值：**

```python
dict: 录屏信息
{
    "videoUrl": "xx",         # 上传完成的视频的链接
    "localUrl": "",           # client上的位置
    "video_path": "",         # 保存到本地的地址
    "fileKey": "xxx",          # 视频key
    "size": 0              # 视频的大小
}
```

## 截图相关

### 1、screenshot(label, img_path)

对设备当前画面进行截图。

**参数：**

- `label`: str 截图文件名
- `img_path`: str 文件路径

**返回值：**

```python
dict: 截图信息
{
    "imageUrl": "xx",         # 上传完成的图片的链接
    "localUrl": "",           # client上的位置
    "video_path": "",         # 保存到本地的地址
    "fileKey": "xxx",          # 图片key
    "size": 0              # 截图大小
}
```

### 2、screenshot_base64()

对设备当前画面进行截图。

**参数：**

- 无

**返回值：**

- `str`: 图片base64

## 点击操作相关

### 1、click_pos(pos, duration, times)

基于相对坐标进行点击操作。

**参数：**

- `pos` (tuple or list): 相对坐标，取值区间 [0, 1.0]
- `duration` (int or float): 点击持续时间，默认为 0.05 秒
- `times` (int): 点击次数，默认为 1 次，传入 2 可实现双击效果

**返回值：**

- `bool`: 点击是否成功

**使用示例：**

```python
# 单击屏幕中心
success = device.click_pos([0.5, 0.5])

# 长按屏幕右上角 2 秒
success = device.click_pos([0.9, 0.1], duration=2.0)

# 双击屏幕底部
success = device.click_pos([0.5, 0.9], times=2)

# 长按屏幕左侧中间位置 1.5 秒
success = device.click_pos([0.1, 0.5], duration=1.5)
```

### 2、click(loc, by, offset, timeout, duration, times)

基于多种定位方式执行点击操作。

**参数：**

- `loc`: 待点击的元素，具体形式需符合基于的点击类型
- `by` (DriverType): 查找类型，默认为 DriverType.UI
  - DriverType.UI: 原生控件
  - DriverType.CV: 图像匹配
  - DriverType.OCR: 文字识别
  - DriverType.POS: 坐标
  - DriverType.GA_UNITY: GA Unity
  - DriverType.GA_UE: GA UE
- `offset` (list or tuple): 偏移，元素定位位置加上偏移为实际操作位置
- `timeout` (int): 定位元素的超时时间，默认为 30 秒
- `duration` (float): 点击的按压时长，以实现长按，默认为 0.05 秒
- `times` (int): 点击次数，以实现双击等效果，默认为 1 次
- `**kwargs`: 基于不同的查找类型，其他需要的参数

**返回值：**

- `bool`: 操作是否成功

**使用示例：**

```python
# 基于控件点击
success = device.click(
    loc="//XCUIElementTypeButton[@label='登录']",
    by=DriverType.UI
)

# 基于图像匹配点击
success = device.click(
    loc="login_button.png",
    by=DriverType.CV,
    timeout=10
)

# 基于文字识别点击
success = device.click(
    loc="确认",
    by=DriverType.OCR
)

# 带偏移的点击
success = device.click(
    loc="//XCUIElementTypeButton[@label='按钮']",
    by=DriverType.UI,
    offset=[10, 5]  # 向右偏移10像素，向下偏移5像素
)

# 双击操作
success = device.click(
    loc="//XCUIElementTypeIcon[@label='照片']",
    by=DriverType.UI,
    times=2
)
```

### 3、long_click(loc, by, offset, timeout, duration, \*\*kwargs)

执行长按操作。

**参数：**

- `loc`: 待操作的元素，具体形式需符合基于的操作类型
- `by` (DriverType): 查找类型，默认为 DriverType.POS坐标
- `offset` (list or tuple): 偏移，元素定位位置加上偏移为实际操作位置
- `timeout` (int): 定位元素的超时时间，默认为 30 秒
- `duration` (int or float): 点击的按压时长，默认为 1 秒

**返回值：**

- `bool`: 操作是否成功

**使用示例：**

```python
# 长按控件 3 秒
success = device.long_click(
    loc="//XCUIElementTypeButton[@label='删除']",
    by=DriverType.UI,
    duration=3.0
)

# 长按图像 2.5 秒
success = device.long_click(
    loc="delete_icon.png",
    by=device.utils.param.DriverType.CV,
    duration=2.5
)

# 长按文字 1.5 秒
success = device.long_click(
    loc="长按我",
    by=device.utils.param.DriverType.OCR,
    duration=1.5
)
```

## 文本输入相关

### 1、input_text(text, timeout, depth)

向设备输入文本内容。

**参数：**

- `text` (str): 待输入的文本
- `timeout` (int): 超时时间，默认为 30 秒
- `depth` (int): source tree 的最大深度值，默认为 10

**返回值：**

- `bool`: 输入是否成功

**使用示例：**

```python
# 基本文本输入
success = device.input_text("Hello World")

# 带超时的文本输入
success = device.input_text("测试文本", timeout=60)

# 调整深度的文本输入
success = device.input_text("复杂文本", timeout=30, depth=15)
```

## 按键操作相关

### 1、press(name)

执行设备功能键操作。

**参数：**

- `name` (DeviceButton): 设备按键类型

说明：
安卓：
DeviceButton.HOME,
DeviceButton.VOLUME_UP,
DeviceButton.VOLUME_DOWN,
DeviceButton.BACK,
DeviceButton.POWER,
DeviceButton.DEL,
DeviceButton.FORWARD_DEL,
DeviceButton.MENU,
DeviceButton.RECENT_APP,
DeviceButton.WAKE_UP,
DeviceButton.SLEEP
iOS：
DeviceButton.HOME,
DeviceButton.VOLUME_UP,
DeviceButton.VOLUME_DOWN,
DeviceButton.POWER,
HM：
DeviceButton.HOME
DeviceButton.VOLUME_UP
DeviceButton.VOLUME_DOWN,
DeviceButton.BACK,
DeviceButton.POWER,
DeviceButton.DEL,
DeviceButton.FORWARD_DEL,
DeviceButton.MENU,
DeviceButton.RECENT_APP,
DeviceButton.SLEEP,
DeviceButton.WAKE_UP,

**返回值：**

- `bool`: 点击是否成功

**使用示例：**

```python
# 按返回键
success = device.press(DeviceButton.BACK)
```

## 滑动操作相关

### 1、slide_pos(pos_from, pos_to, down_duration)

基于相对坐标执行滑动操作。

**参数：**

- `pos_from` (tuple or list): 滑动起始坐标
- `pos_to` (tuple or list): 滑动结束坐标
- `down_duration` (int or float): 起始位置按下时长（秒），以实现拖拽功能，默认为 0

**返回值：**

- `bool`: 滑动是否成功

**使用示例：**

```python
# 从屏幕左侧滑到右侧
success = device.slide_pos(
    pos_from=[0.1, 0.5],
    pos_to=[0.9, 0.5]
)

# 从屏幕顶部滑到底部
success = device.slide_pos(
    pos_from=[0.5, 0.1],
    pos_to=[0.5, 0.9]
)

```

### 2、slide(loc_from, loc_to, by, timeout, down_duration, **kwargs)

基于多种定位方式执行滑动操作。

**参数：**

- `loc_from`: 滑动起始元素位置
- `loc_to`: 滑动结束元素位置
- `by` (DriverType): 查找类型，默认为 DriverType.POS
- `timeout` (int): 定位元素的超时时间，默认为 120 秒
- `down_duration` (int or float): 起始位置按下时长（秒），以实现拖拽功能，默认为 0
- `**kwargs`: 基于不同的查找类型，其他需要的参数

**返回值：**

- `bool`: 操作是否成功

**使用示例：**

```python
# 从控件A滑动到控件B
success = device.slide(
    loc_from="//XCUIElementTypeButton[@label='开始']",
    loc_to="//XCUIElementTypeButton[@label='结束']",
    by=device.utils.param.DriverType.UI
)

# 基于图像匹配的滑动
success = device.slide(
    loc_from="start_icon.png",
    loc_to="end_icon.png",
    by=device.utils.param.DriverType.CV,
    timeout=60
)

# 基于文字识别的滑动
success = device.slide(
    loc_from="起点",
    loc_to="终点",
    by=device.utils.param.DriverType.OCR
)

```

## 应用管理相关

### 1、install_app(app_url, need_resign, resign_bundle)

安装应用到设备。

**参数：**

- `app_url` (str): 安装包url链接
- `need_resign` (bool): 可缺省，默认为 False。只有 iOS 涉及，需要重签名时传入 True
- `resign_bundle` (str): 可缺省，默认为空。只有 iOS 涉及，need_resign 为 True 时，此参数必须传入非空的 bundleId

**返回值：**

- `bool`: 安装是否成功

### 2、uninstall_app(pkg)

从设备卸载应用。

**参数：**

- `pkg` (str): 被卸载应用的包名，Android 和鸿蒙为应用的 packageName，iOS 则对应为 bundleId

**返回值：**

- `bool`: 卸载是否成功

### 3、start_app(pkg, clear_data, **kwargs)

启动应用。

**参数：**

- `pkg` (str): iOS 为应用 bundle id，Android 和鸿蒙对应为包名
- `clear_data` (bool): 可缺省，默认为 False。仅 Android 相关，清除应用数据
- `**kwargs`: 其他扩展参数

**返回值：**

- `bool`: 启动是否成功

**使用示例：**

```python
# 基本启动应用
success = device.start_app("com.apple.AppStore")

# 清除数据后启动应用（仅Android）
success = device.start_app("com.example.app", clear_data=True)
```

### 4、stop_app(pkg)

结束应用。

**参数：**

- `pkg` (str): iOS 为应用 bundle id，Android 和鸿蒙对应为包名

**返回值：**

- `bool`: 启动是否成功

**使用示例：**

```python
success = device.stop_app("com.apple.AppStore")
```

## 命令执行相关

### 1、cmd_adb(cmd, timeout)

仅 Android 和鸿蒙设备，执行 adb 或 hdb 命令。

**参数：**

- `cmd` (str or list): 具体的 adb 或者 hdb 命令
- `timeout` (int): 执行命令的超时时间，默认为 10 秒

**返回值：**

- `str`: 命令执行结果

**使用示例：**

```python
# 执行 adb 命令获取设备信息
result = device.cmd_adb("getprop ro.product.model")

# 执行 adb 命令获取当前 activity
result = device.cmd_adb("dumpsys activity activities | grep mResumedActivity")

# 带超时的命令执行
result = device.cmd_adb("pm list packages", timeout=30)
```

**注意事项：**

- 此方法仅支持 Android 和鸿蒙设备，iOS 设备不支持
- 命令执行结果会返回字符串格式
- 建议设置合理的超时时间，避免长时间等待
- 某些系统级命令可能需要设备 root 权限

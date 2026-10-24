# WYU-dorm-power-monitor
WYU 宿舍电量监控工具


这是一款面向五邑大学校园宿舍场景的轻量级 Windows 桌面监控工具，用于定时查询宿舍剩余电量，并在电量低于设定阈值时自动弹出 Windows 原生 Toast 通知提醒。程序支持最小化到系统托盘后台运行，适合长期挂机监控。

  

## 项目背景

  

五邑大学及部分高校宿舍采用预付费用电模式，当剩余电量不足时可能突然断电，影响学习、生活与设备运行。本工具通过定时查询宿舍电量接口，在电量低于用户设定的阈值时主动推送通知，帮助用户提前充值，避免因欠费断电造成不便。

  

## 功能特性

  

-  **定时电量查询**：按用户设定的间隔自动查询宿舍剩余电量。

-  **低电量提醒**：当剩余电量低于阈值时，弹出 Windows Toast 通知，提醒及时充值。

-  **系统托盘支持**：关闭窗口后程序不会退出，而是隐藏到系统托盘继续监控；右键托盘图标可恢复窗口、停止监控或彻底退出。

-  **本地配置管理**：支持自定义宿舍楼栋、房间号、低电量阈值、检查间隔及接口 Cookie，配置保存在本地 `config.json` 中。

-  **可打包为单文件**：可通过 PyInstaller 打包为独立 `.exe` 文件，无需安装 Python 即可运行。

-  **复用性**：通过修改对应的api，可以在其他学校使用。

  

## 运行环境

  

- 操作系统：Windows 10 / 11

- Python 版本：3.8 及以上

- 网络环境：可访问宿舍电量查询接口



## 使用说明

  

1. 启动程序后，在界面中填写宿舍楼栋、房间号、低电量阈值和检查间隔。

2. 点击“保存配置”，确认信息无误。

3. 点击“开始监控”，程序会立即查询一次电量，并按设定间隔持续监控。

4. 当剩余电量低于阈值时，右下角会弹出 Toast 通知。

5. 点击窗口右上角关闭按钮后，程序将隐藏到系统托盘，监控不会中断。

6. 右键托盘图标可选择“显示窗口”“停止监控”或“彻底退出”。

7. 如果只是在五邑大学使用，直接运行封装好的exe文件就可以了。如果需要在其他学校使用，请手动修改对应的api再进行封装等操作。
  

## 安装与运行

  

### 1. 克隆或下载项目

  

```bash

git  clone  https://github.com/你的用户名/WYU-dorm-power-monitor.git

cd  WYU-dorm-power-monitor

```

  

或直接下载 ZIP 压缩包并解压。

  

### 2. 创建虚拟环境（推荐）

  

```bash

python  -m  venv  venv

```

  

Windows 下激活虚拟环境：

  

```bash

venv\Scripts\activate

```

  

### 3. 安装依赖

  

```bash

pip  install  -r  requirements.txt

```

  

### 4. 运行程序

  

```bash

python  main.py

```

  

程序启动后会弹出主窗口，填写宿舍信息并保存配置后，点击“开始监控”即可。

  

## 配置说明

  

首次运行并点击“保存配置”后，程序会在同级目录生成 `config.json` 文件。也可直接编辑该文件：

  

```json

{

"dorm_building": "1",

"dorm_room": "101",

"low_power_threshold": 10.0,

"check_interval_minutes": 30,

"cookie": ""

}

```

  

| 字段 | 说明 |

|---|---|

| `dorm_building` | 宿舍楼栋号 |

| `dorm_room` | 宿舍房间号 |

| `low_power_threshold` | 低电量报警阈值，单位为度 |

| `check_interval_minutes` | 电量检查间隔，单位为分钟 |

| `cookie` | 若接口需要登录凭证，可在此填写 Cookie |

  

>  **安全提醒**：`config.json` 可能包含宿舍信息、接口凭证等隐私数据，请勿上传至公开仓库。项目已提供 `.gitignore` 规则，默认忽略该文件。

  

## 打包为 EXE

  

若需要在未安装 Python 的电脑上运行，可使用 PyInstaller 打包：

  

```bash

pip  install  pyinstaller

pyinstaller  --onefile  --windowed  --name  宿舍电量监控  --hidden-import  pystray._win32  --hidden-import  PIL  main.py

```

  

打包完成后，`dist` 目录下会生成 `宿舍电量监控.exe`。运行时请确保 `config.json` 与 exe 文件位于同一目录。

  

## 项目结构

  

```text

WYU-dorm-power-monitor/

├── main.py # 主程序入口，包含 GUI 界面、监控线程与托盘逻辑

├── power_api.py # 宿舍电量查询接口封装

├── notifier.py # Windows Toast 通知封装

├── config_store.py # 本地配置文件读写管理

├── test_toast.py # 通知功能测试脚本

├── requirements.txt # Python 依赖列表

├── .gitignore # Git 忽略规则

└── README.md # 项目说明文档

```

  

## 注意事项

  

- 本工具仅用于个人宿舍电量监控，默认是在五邑大学中使用。如要在其他学校复用，请遵守所在学校相关管理规定。

- 若宿舍电量查询接口发生变更，需同步更新 `power_api.py` 中的请求逻辑。

- 打包后的 exe 文件可能被部分安全软件误报，属于 PyInstaller 打包程序的常见现象。

  

## 更新日志

  

-  **v1.0.0**：初始版本发布，支持定时监控、低电量通知、系统托盘运行与本地配置管理。

  

## 许可证

  

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。


# CAN-PR-tool
一个汽车`CAN`学习和测试样例。用于实现：①解析 `DBC` 文件，将 `CAN` 原始报文（十六进制帧）转换为物理信号值（如`车速`、`引擎转速`）；②将解析后的数据按时间戳存入 `SQLite` 数据库；③“回灌”功能，将历史 `CAN` 报文按原始时序重放到虚拟 `CAN` 总线（`vcan`）或重新编码为 `CAN` 帧文件；④提供历史版本对比分析入口（基于数据库查询）。

## 功能

- **DBC 解析**：加载标准 `DBC` 文件，将 `CAN` 原始报文转换为物理信号值（本仓库内的`DBC`文件以`引擎转速`和`车速`为例）
- **日志解析**：从 `Vector ASC` 格式的 `CAN` 日志中提取`时间戳`、`ID` 和`数据域`
- **数据存储**：将解码后的信号按`时间戳`存入 `SQLite` 数据库，支持历史版本管理与对比
- **回灌重放**：从数据库读取历史报文，按原始时序重放到虚拟 `CAN` 总线 `vcan`，验证接收方行为
- **实时监听**：通过 `candump` 从 `vcan0` 实时将报文入库

## 依赖环境

- 操作系统： `Ubuntu 24.04`（因为`Ubuntu 24.04`可能不支持`vcan0`,也可以从[https://github.com/MrKedow/WSL2-Linux-Kernel](https://github.com/MrKedow/WSL2-Linux-Kernel)下载带`vcan0`的内核，自己动手编译，下载慢可以轮番使用这两个加速站：[https://tool.mintimate.cn/gh/](https://tool.mintimate.cn/gh/)、[https://github.akams.cn/](https://github.akams.cn/)）
- Python：`Python 3.8+`
- 系统工具：`can-utils`（提供 `cansend`、`candump` 等工具）
- Python 库：`cantools`、`python-can`（可使用虚拟环境安装）

## 安装

### 1. 安装系统依赖
```bash
sudo apt update
sudo apt install can-utils python3-pip python3-venv -y
```

### 2. 在虚拟环境中安装 Python 依赖
如果直接在工作空间安装Python依赖会报错，这是`Ubuntu 24.04`的数据保护机制，所以这里需要先开启虚拟环境。
```bash
python3 -m venv venv
source venv/bin/activate
pip install cantools python-can
```

### 3. 加载虚拟 CAN 模块
```bash
sudo modprobe can
sudo modprobe can_raw
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
```

## 开始运行

### 第一步：创建DBC 文件和 CAN 日志

把创建好的 `DBC` 样例文件 `example.dbc` 和 `CAN` 日志文件 `trace.asc` 放进项目目录。

### 第二步：初始化数据库并解析日志
```bash
python database.py
python parser.py
```

脚本会读取 `trace.asc`，解析每条报文并通过 `DBC` 解码为物理信号，将结果写入 `can_data.db`。

### 第三步：查看解析结果
```bash
sqlite3 can_data.db "SELECT * FROM can_signals LIMIT 20;"
```

### 第四步：回灌到虚拟 CAN 总线

在一个终端启动 `candump` 监听：
```bash
candump vcan0
```

在另一个终端运行回灌：
```bash
python replay.py
```

`candump` 窗口将显示按原始时序回放的 CAN 报文。

## 项目结构

```
CAN-PR-tool/
├── example.dbc          # 示例 DBC 文件
├── trace.asc            # 示例 CAN 日志（Vector ASC 格式）
├── can_data.db          # SQLite 数据库（程序自动生成）
├── database.py          # 数据库初始化与操作
├── parser.py            # 日志解析与信号提取
├── replay.py            # 历史数据回灌
├── candump_logger.py    # 实时记录工具（可选）
└── README.md
```

## DBC 文件说明

示例 DBC 文件定义了一条 CAN 报文，包含两个信号：

| 信号名 | 起始位 | 长度 | 缩放因子 | 偏移量 | 单位 | 含义 |
|--------|--------|------|----------|--------|------|------|
| EngineSpeed | 0 | 16 | 1 | 0 | rpm | 发动机转速 |
| VehicleSpeed | 16 | 16 | 0.1 | 0 | km/h | 车速 |

## 数据流转

```
CAN 日志文件 (.asc)
    │
    ▼
parser.py (解析 DBC + 提取信号)
    │
    ▼
SQLite 数据库 (can_data.db)
    │
    ▼
replay.py (按时间戳回灌)
    │
    ▼
vcan0 (虚拟 CAN 总线)
    │
    ▼
candump (验证回放结果)
```

## 常见问题

| 问题 | 原因 | 解决方法 |
|------|------|----------|
| `ModuleNotFoundError: No module named 'cantools'` | 虚拟环境未激活 | 执行 `source venv/bin/activate` |
| `Cannot open can interface` | vcan0 未创建 | 执行 `sudo ip link add dev vcan0 type vcan` |
| `Protocol not supported` | can_raw 模块未加载 | 执行 `sudo modprobe can_raw` |
| 回灌报文与原始日志不一致 | 时间戳排序问题 | 确认数据库中数据按时间戳升序排列 |

# OKX 高精度交易系统

🚀 专业级高端交易系统，基于市场局部结构

## 📋 目录
- 系统简介
- 核心功能
- 系统架构
- 快速开始
- 配置说明
- 代理配置
- 常见问题
- 免责声明

## 🎯 系统简介
本系统是一个基于市场全部结构的高精度量化交易系统，针对 OKX 交易所设计。系统通过实时订单簿和订单流，识别市场异常行为，执行策略监控策略。

### 核心特性
- 三层存储架构 - 热 (RAM) / 温 (Redis) / 冷 (Parquet) 存储
- 专业订单簿 - 本地维护 400 档深度数据
- 局部结构分析 - OFI、理财产品、流动性空白等指标
- 策略 - 抢跑、挂墙、点差捕获
- 风险熔断 - 自动止损和系统保护
- WebSocket Flow - 实时人口市场数据

## 💡 核心功能

### 1. 订单簿系统
- 本地维护 400 档深度数据
- 增量更新（books-l2-tbt）
- 微秒查询延迟
- 校验和校验

### 2. 订单流分析
- OFI（订单流不平衡） - 订单流不平衡
- WMP（加权市场压力） - 加权市场压力
- 流动性真空检测 - 识别深度差
- 买卖压力计算 - 实时多空对比

### 3. 清晰策略

#### 抢跑策略（抢跑）
- 检测深度突然下降
- 大单即将成交信号
- 抢先开仓
- 快速平仓

#### 挂墙策略（Wall Riding）
- 识别买卖盘大单挂墙
- 挂在前面墙上
- 被成交后盈利

#### 点差捕获（Spread Capture）
- 检测买卖价差变大
- 低价买入 高价卖出
- 尺寸点差

### 4. 风险管理
- 每日亏损熔断 - 超过 5% 自动停止
- 网络延迟监控 - 超过阈值自动停止默认（500ms，可通过 MAX_LATENCY_MS 调整）
- 仓位限制 - 最大持仓限制
- 异常检测 - 异常交易行为监控

### 5. 三层存储
- **热存储 (RAM)** - 最近 1000 笔成交，实时查询
  - ↓ 定期同步
- **温存储 (Redis)** - 最近 1 小时数据，缓存
  - ↓ 定期同步
- **冷存储 (Parquet)** - 永久存储，历史分析

## 🏗️ 系统架构
```
┌──────────────────────────────────────────────┐
│          GamblerHunter V2                   │
└────────────┬─────────────────────────────────┘
             │
    ┌────────┴─────────────────┐
    │                          │
┌───▼──────────┐      ┌───────▼──────┐
│  WebSocket   │      │  Strategies  │
│   Streamer   │◄─────│   (战术)     │
└───┬──────────┘      └───────┬──────┘
    │                        │
┌───▼──────────┐      ┌───────▼──────┐
│   OrderBook  │      │   Features   │
│ (本地镜像)   │      │  (微观结构)  │
└───┬──────────┘      └───────┬──────┘
    │                        │
┌───▼────────────────────────▼─────┐
│        Risk Manager               │
│        (风险管理)                  │
└────────────┬──────────────────────┘
             │
      ┌──────▼──────┐
      │  Execution  │
      │    Engine   │
      │  (执行引擎) │
      └─────────────┘
```

## 🚀 快速开始

### 1. 环境要求
- Python 3.10+
- 管道

### 2. 安装依赖
```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2.1 项目结构
```
okx_trader/            # 交易系统核心模块
  config.py            # 环境配置加载
  orderbook.py         # 本地订单簿
  orderbook_stream.py  # WebSocket 订阅器
  features.py          # 微观结构指标
  strategies.py        # 策略生成
  risk.py              # 风险控制
  execution.py         # 执行引擎
  storage.py           # 三层存储接口
main.py                # 系统入口
test_api.py            # API 连通性测试
```

### 3. 配置 API 密钥
```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 文件
# Windows:
notepad .env
# macOS/Linux:
vim .env
```

在 `.env` 文件中填入您的 OKX API 快捷键：

```
OKX_API_KEY=your-api-key-here
OKX_SECRET_KEY=your-secret-key-here
OKX_PASSPHRASE=your-passphrase-here
OKX_BASE_URL=https://www.okx.com
DRY_RUN=true
TRADING_MODE=paper
LOG_LEVEL=INFO
LOG_FILE=logs/validation.log
HTTP_PROXY=http://127.0.0.1:7890
HTTPS_PROXY=http://127.0.0.1:7890
```

获取 OKX API 密钥：
- 登录 OKX 官网
- 进入「API 管理」
- 创建新的 API 密钥
- 选择权限：读取、交易
- 绑定 IP 白名单（安全！）

### 4. 测试 API 连接
```bash
python test_api.py
```

测试脚本验证：
- ✅ 服务时间
- ✅ 账户余额
- ✅ 持仓信息

### 5. 启动系统
```bash
python main.py
```

## 🔧 配置说明

### 环境指标
在 `.env` 文件中配置：
```
# API 配置
OKX_API_KEY=your-api-key-here
OKX_SECRET_KEY=your-secret-key-here
OKX_PASSPHRASE=your-passphrase-here
OKX_BASE_URL=https://www.okx.com

# 交易配置
MAX_POSITION_SIZE=1000          # 最大仓位
MAX_DAILY_LOSS=0.05             # 最大日亏损 (5%)
LEVERAGE_LIMIT=20               # 杠杆限制
TIMEOUT=30                      # 请求超时时间

# 策略配置
ENABLE_LIQUIDATION_HUNTING=true # 爆仓单捕猎
ENABLE_FUNDING_ARBITRAGE=true   # 资金费率套利
ENABLE_MARKET_MAKING=false      # 做市商策略

# WebSocket 配置
WS_RECONNECT_DELAY=5            # 重连延迟
WS_PING_INTERVAL=20             # 心跳间隔
```

## 🌐 代理配置
如果在国内网络，由于网络限制，需要配置代理才能访问 OKX API。

### 1. 安装代理软件
推荐使用冲突

### 2. 配置代理端口
Clash 默认端口：
- HTTP 代理：127.0.0.1:7890
- SOCKS5 代理：127.0.0.1:7891

### 3. 设置环境指标
**Windows（PowerShell）：**
```powershell
$env:HTTP_PROXY="http://127.0.0.1:7890"
$env:HTTPS_PROXY="http://127.0.0.1:7890"
python main.py
```

**Windows（CMD）：**
```cmd
set HTTP_PROXY=http://127.0.0.1:7890
set HTTPS_PROXY=http://127.0.0.1:7890
python main.py
```

**macOS/Linux：**
```bash
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
python main.py
```

### 4. 测试代理
```bash
curl.exe -x http://127.0.0.1:7890 https://www.okx.com/api/v5/public/time
```

如果返回 JSON 数据，说明代理配置成功。

## ⚙️ 网络延迟配置
系统会监控网络延迟，超过阈值会触发 Kill Switch 自动停止交易。

### 延迟阈值
- 直连国内 OKX：建议 100-200ms
- 通过国内代理：建议 300-1000ms（根据代理质量调整）
- 海外服务器：建议 50-100ms

### 设置延迟阈值
在 `.env` 文件中设置 `MAX_LATENCY_MS`：
```
# 设置网络延迟阈值为 1000ms（1秒）
MAX_LATENCY_MS=1000
```

### 调整建议
- 如果系统频繁触发 Kill Switch（网络延迟过高），请增加 `MAX_LATENCY_MS` 值
- 如果网络质量很好，可以降低 `MAX_LATENCY_MS` 以更快的速度响应网络问题
- 建议先用 `test_api.py` 测试实际网络延迟，然后设置合适的阈值

## ❓ 常见问题

### 1. DNS 解析失败
`Cannot connect to host www.okx.com:443 ssl:default [getaddrinfo failed]`

解决方案：
- 配置代理（见上方）
- 或者将 DNS 服务器切换为 8.8.8.8

### 2. API 认证失败
`Error: Invalid API Key`

解决方案：
- 检查 API Key 是否正确
- 检查 IP 白名单是否配置
- 检查 API 权限是否包含“交易”和“读取”

### 3. Redis 连接失败
`Error 10061 connecting to localhost:6379`

解决方案：
- 这是正常的，系统会自动切换到内存模式
- 或者安装 Redis 服务

### 4. 时间错误
`Invalid OK-ACCESS-TIMESTAMP`

解决方案：
- 同步您的电脑时间
- 或者使用 NTP 服务器

## ⚠️ 重要提示

### 风险警告
- 高风险 - 量化交易存在极高风险，可能导致本金全部损失
- 先测试 - 建议先在模拟环境充分测试
- 小额开始 - 实盘小额开始
- 严格止损 - 严格遵守风险控制规则
- 持续监控 - 保持系统运行，实时监控

### 安全建议

**API 安全**
- 不要泄露 API 密钥
- 绑定 IP 白名单
- 不要使用币提权限

**风险控制**
- 设置每日亏损熔断
- 限制最大仓位
- 设置止损参数

**系统安全**
- 使用强密码
- 定期更新依赖
- 定期备份日志

## 📊 技术架构

### 核心技术
- 异步 I/O - asyncio、aiohttp
- WebSocket - 实时大众市场数据
- 本地 OrderBook - 堆结构，微秒级查询
- 订单流分析 - 实时压力计算
- 数据分析 - numpy、pandas、pyarrow

### 性能指标
- 延迟：< 1ms（本地决策）
- 持仓时间：秒级-分钟级
- 数据更新：实时主动
- 存储容量：可扩展

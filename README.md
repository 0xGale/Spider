# 知乎热榜爬虫程序

一个模块化设计的知乎热榜爬虫程序，支持数据爬取、处理和存储到PostgreSQL数据库。

## 🏗️ 项目结构

```
Spider/
├── main.py              # 主程序入口
├── config.py            # 配置模块
├── models.py            # 数据模型定义
├── database.py          # 数据库操作模块
├── scraper.py           # 爬虫模块
├── processor.py         # 数据处理模块
├── utils.py             # 工具函数模块
├── init_db.py           # 数据库初始化脚本
├── requirements.txt     # 依赖包列表
├── .env                 # 环境变量配置文件
└── README.md           # 项目说明文档
```

## 📋 功能特性

- **模块化设计**: 清晰的代码架构，易于维护和扩展
- **数据爬取**: 自动获取知乎热榜数据
- **数据处理**: 数据清洗、验证、去重和排序
- **数据库存储**: 支持PostgreSQL数据库存储
- **多种运行模式**: 支持单次运行、定时运行、数据查看和清理
- **错误处理**: 完善的异常处理和重试机制
- **日志记录**: 详细的操作日志
- **数据备份**: 可选的JSON格式数据备份

## 🚀 快速开始

### 1. 环境准备

确保你的系统已安装：
- Python 3.8+
- PostgreSQL 数据库

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

1. 创建PostgreSQL数据库：
```sql
CREATE DATABASE zhihu_hot;
```

2. 修改 `.env` 文件中的数据库配置：
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=zhihu_hot
DB_USER=your_username
DB_PASSWORD=your_password
```

### 4. 初始化数据库

```bash
python init_db.py
```

### 5. 运行程序

```bash
# 执行一次爬取
python main.py --mode once

# 定时爬取（每小时）
python main.py --mode schedule --interval 3600

# 查看最近数据
python main.py --mode show --limit 20

# 清理旧数据（保留7天）
python main.py --mode cleanup --days 7

# 保存JSON备份
python main.py --mode once --json
```

## 📊 数据库结构

### zhihu_hot_items 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键，自增 |
| question_id | VARCHAR(50) | 知乎问题ID，唯一 |
| title | VARCHAR(500) | 问题标题 |
| excerpt | TEXT | 问题描述摘要 |
| url | VARCHAR(500) | 问题链接 |
| hot_index | FLOAT | 热度指数 |
| answer_count | INTEGER | 回答数量 |
| follower_count | INTEGER | 关注人数 |
| created_time | DATETIME | 创建时间 |
| updated_time | DATETIME | 更新时间 |

## 🔧 配置说明

### 数据库配置 (config.py)

- `DATABASE_CONFIG`: 数据库连接配置
- `SPIDER_CONFIG`: 爬虫相关配置
- `LOG_CONFIG`: 日志配置

### 环境变量 (.env)

```
# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=zhihu_hot
DB_USER=postgres
DB_PASSWORD=your_password

# 日志级别
LOG_LEVEL=INFO
```

## 🛠️ 模块说明

### 1. 配置模块 (config.py)
- 管理数据库配置
- 管理爬虫设置
- 管理日志配置

### 2. 数据模型 (models.py)
- 定义数据库表结构
- 提供数据模型类

### 3. 数据库模块 (database.py)
- 数据库连接管理
- 数据CRUD操作
- 会话管理

### 4. 爬虫模块 (scraper.py)
- HTTP请求处理
- 数据获取和解析
- 错误重试机制

### 5. 数据处理模块 (processor.py)
- 数据清洗和验证
- 数据去重和排序
- 数据摘要生成

### 6. 工具模块 (utils.py)
- 日志设置
- 文件操作
- 通用工具函数

### 7. 主程序 (main.py)
- 程序入口点
- 命令行参数处理
- 流程控制

## 🚨 注意事项

1. **遵守网站规则**: 请遵守知乎的robots.txt和使用条款
2. **合理爬取频率**: 避免过于频繁的请求
3. **数据使用**: 仅用于学习和研究目的
4. **错误处理**: 程序包含完善的错误处理机制
5. **数据备份**: 建议定期备份数据库

## 📝 使用示例

### 单次爬取并保存JSON
```bash
python main.py --mode once --json
```

### 每30分钟定时爬取
```bash
python main.py --mode schedule --interval 1800
```

### 查看最新50条数据
```bash
python main.py --mode show --limit 50
```

### 清理30天前的数据
```bash
python main.py --mode cleanup --days 30
```

## 🔍 日志文件

程序运行时会生成 `spider.log` 日志文件，包含：
- 程序启动和停止信息
- 爬取过程详情
- 数据处理结果
- 错误和警告信息

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

本项目基于MIT许可证开源。

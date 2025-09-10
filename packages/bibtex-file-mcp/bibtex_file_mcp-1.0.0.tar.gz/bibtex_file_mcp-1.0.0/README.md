# BibTeX MCP Server

[![PyPI version](https://badge.fury.io/py/bibtex-file-mcp.svg)](https://badge.fury.io/py/bibtex-file-mcp)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)

🚀 **一个高效的 BibTeX 文件操作 MCP 服务器**

基于 [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) 构建，让 AI 助手（如 Cursor）能够智能地读取、查询和管理 BibTeX 文献数据库。

## ✨ 特色亮点

- **📚 BibTeX 支持** - 完整的 `.bib` 文件解析和处理
- **🤖 AI 友好** - 专为 LLM 设计的简洁 API
- **⚡ 即开即用** - 使用 `uvx` 一键启动，无需复杂配置
- **🔧 Cursor 集成** - 完美集成到 Cursor 编辑器的 MCP 系统
- **🎯 轻量高效** - 专注核心功能，性能卓越

## 功能特性

### 🎯 核心功能
- **读取文件** - 默认返回所有key，可选显示前5条详细信息
- **查询条目** - 根据key获取单条entry的详细信息  
- **写入文件** - 根据key列表筛选并写入新文件

## 使用uvx运行

### 安装和运行
```bash
# 从 PyPI 直接运行（推荐）
uvx bibtex-mcp-server

# 从本地项目运行
uvx --from . bibtex-mcp-server

# 指定 Python 版本
uvx --python 3.10+ bibtex-mcp-server
```

### 依赖配置
项目已配置 `pyproject.toml`，uvx会自动处理依赖安装。

## 🎯 Cursor 中的配置

### 方式一：从 PyPI 安装（推荐）

发布到 PyPI 后，在 Cursor 的 MCP 服务器设置中添加以下 JSON 配置：

```json
{
  "mcpServers": {
    "bibtex-mcp": {
      "command": "uvx",
      "args": ["bibtex-mcp-server"]
    }
  }
}
```

### 方式二：从本地项目运行

如果你想从本地项目运行（开发或测试），使用以下配置：

```json
{
  "mcpServers": {
    "bibtex-mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "/path/to/your/bibtex_mcp",
        "bibtex-mcp-server"
      ],
      "env": {
        "PYTHONPATH": "/path/to/your/bibtex_mcp"
      }
    }
  }
}
```

### 🚀 配置完成后的使用

配置完成后，你可以在 Cursor 中直接使用 BibTeX 工具：

```
请帮我读取 references.bib 文件并显示所有条目的 key
```

```
从 library.bib 中找到 key 为 "smith2024" 的条目详细信息
```

```
从 all_papers.bib 中选择这些条目：["paper1", "paper2", "paper3"] 并保存到 selected.bib
```

## 可用工具

### 1. `read_bibtex_file(filepath, show_details=False)`
读取BibTeX文件

```python
# 获取所有key（默认）
read_bibtex_file("references.bib")

# 显示前5条详细信息
read_bibtex_file("references.bib", show_details=True)
```

### 2. `get_bibtex_entry(filepath, key)`
根据key获取单条条目详细信息

```python
get_bibtex_entry("references.bib", "smith2024")
```

### 3. `write_bibtex_entries(source_filepath, target_filepath, keys)`
根据key列表写入选定条目到新文件

```python
write_bibtex_entries(
    source_filepath="all_refs.bib",
    target_filepath="selected_refs.bib", 
    keys=["smith2024", "doe2023", "jones2022"]
)
```

## 典型工作流程

1. **浏览文献库**：
   ```python
   # 查看所有可用的key
   read_bibtex_file("my_library.bib")
   ```

2. **查看具体条目**：
   ```python
   # 查看感兴趣的条目详情
   get_bibtex_entry("my_library.bib", "interesting_paper_2024")
   ```

3. **创建子集**：
   ```python
   # 筛选相关论文到新文件
   write_bibtex_entries(
       "my_library.bib", 
       "project_refs.bib",
       ["paper1_2024", "paper2_2023", "paper3_2024"]
   )
   ```

## 项目结构

```
bibtex_mcp/
├── bibtex_file_mcp.py    # 主程序
├── pyproject.toml        # uvx配置文件
├── requirements.txt      # 依赖列表
└── README.md            # 使用说明
```

## 特点

- **轻量高效** - 只保留核心功能，没有冗余
- **假设正确** - 假设所有BibTeX格式都是正确的
- **简单解析** - 使用简单正则表达式解析
- **uvx友好** - 支持uvx一键运行和配置

## 系统要求

- Python 3.10+
- 依赖包：
  - `mcp>=0.1.0`
  - `fastmcp>=0.1.0` 
  - `pydantic>=2.0.0`

## 使用uvx的优势

- 无需手动管理虚拟环境
- 自动处理依赖安装
- 一次性运行，无残留
- 支持不同Python版本

## 📦 安装和获取

### 从 PyPI 安装（推荐）

```bash
# 直接运行，无需预安装
uvx bibtex-mcp-server

# 或者安装到系统
pip install bibtex-file-mcp
```

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/Qing25/bibtex-file-mcp.git
cd bibtex-file-mcp

# 从本地运行
uvx --from . bibtex-mcp-server

# 或者本地安装
pip install -e .
```

## 🔧 开发和贡献

```bash
# 克隆项目
git clone https://github.com/Qing25/bibtex-file-mcp.git
cd bibtex-file-mcp

# 设置开发环境
uv venv
source .venv/bin/activate  # Linux/Mac
# 或 .venv\Scripts\activate  # Windows

# 安装依赖
uv pip install -e .

# 运行测试
python test_tools.py
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

- GitHub: [https://github.com/Qing25/bibtex-file-mcp](https://github.com/Qing25/bibtex-file-mcp)
- Issues: [https://github.com/Qing25/bibtex-file-mcp/issues](https://github.com/Qing25/bibtex-file-mcp/issues)
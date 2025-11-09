# 中国石油大学第二课堂活动查询助手

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue.svg">
  <img src="https://img.shields.io/badge/Tkinter-GUI-orange.svg">
  <img src="https://img.shields.io/badge/License-MIT-green.svg">
</div>

## 📋 项目简介

中国石油大学第二课堂活动查询助手是一款专为中国石油大学学生设计的桌面应用程序，旨在简化第二课堂活动的查询和管理流程。该应用提供了直观的界面，帮助学生快速查看已报名活动、签到状态、活动详情等重要信息。

## ✨ 功能特性

- **账号登录**: 支持中国石油大学统一身份认证
- **活动列表展示**: 清晰展示所有已报名活动
- **活动状态可视化**: 通过颜色区分已完成和未完成活动
- **详情查看**: 双击查看活动详细信息（时间、地点、积分等）
- **学生姓名个性化**: 自动提取并显示学生姓名
- **多线程数据加载**: 确保界面响应流畅

## 📦 环境要求

- Python 3.8 或更高版本
- 安装所需的Python库（详见requirements.txt）

## 🚀 安装部署

### 1. 克隆项目

```bash
git clone https://github.com/yeyixiang2007/CUP_2nd_Class_Helper.git
cd CUP_2nd_Class_Helper
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行应用

```bash
python main_app.py
```

## 📖 使用指南

### 登录
1. 在登录框中输入您的学号和密码
2. 点击「登录」按钮
3. 登录成功后，状态栏会显示欢迎信息

### 查看活动列表
1. 登录成功后，点击「获取活动列表」按钮
2. 应用将自动加载您的活动列表，并预加载最近的10个活动详情
3. 状态栏会显示加载进度和结果

### 查看活动详情
1. 对于未加载详情的活动，双击该行
2. 应用将获取并显示该活动的详细信息
3. 获取完成后，活动状态和详情将自动更新

### 活动状态说明
- **浅绿色背景**: 已完成签到和签退的活动
- **浅粉色背景**: 未完成签到或签退的活动
- **灰色文字**: 尚未加载详情的活动

## 🔧 项目结构

```
├── .github/            # GitHub配置目录
│   └── workflows/      # GitHub Actions工作流配置
│       └── python-app.yml  # CI/CD配置文件
├── docs/               # 文档目录
│   └── technical_documentation.md  # 技术原理文档
├── src/                # 源代码目录
│   ├── activity_fetcher.py  # 活动数据获取模块
│   ├── config.py           # 配置文件
│   ├── html_parser.py      # HTML解析模块
│   ├── network_client.py   # 网络请求模块
│   └── ui_manager.py       # UI管理模块
├── main_app.py         # 主应用程序入口
├── requirements.txt    # 项目依赖
├── LICENSE             # 开源许可证
└── .gitignore          # Git忽略文件
```

## 🛠️ 技术栈

- **Python**: 核心编程语言
- **Tkinter**: GUI图形界面库
- **Requests**: HTTP网络请求库
- **BeautifulSoup4**: HTML解析库
- **Colorama**: 终端输出美化库

## 📄 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。

## 💡 常见问题

### Q: 无法登录或登录失败怎么办？
A: 请检查您的学号和密码是否正确，确保网络连接正常。如仍有问题，请联系开发者。

### Q: 活动列表为空怎么办？
A: 请确认您在第二课堂系统中已报名参加活动。如果已报名但仍显示为空，可能是因为页面结构有变化，需要更新解析逻辑。

### Q: 应用程序闪退或无响应怎么办？
A: 请尝试以管理员权限运行应用程序，或检查您的Python版本是否符合要求。

## 📧 联系我们

如有任何问题或建议，请通过以下方式联系我们：

- GitHub Issues: [https://github.com/yeyixiang2007/CUP_2nd_Class_Helper/issues](https://github.com/yeyixiang2007/CUP_2nd_Class_Helper/issues)

---

<div align="center">
  <p>Made with ❤️ for CUP students</p>
</div>

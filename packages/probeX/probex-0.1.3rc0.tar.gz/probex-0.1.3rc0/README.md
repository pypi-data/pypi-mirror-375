# probeX 测试平台

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![Dash](https://img.shields.io/badge/Dash-2.0+-orange.svg)](https://dash.plotly.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📖 项目简介

probeX 是一个功能完整的测试自动化平台，集成了测试框架、Web 管理界面和云原生支持。该平台提供了从测试用例管理到执行、报告生成的全流程解决方案，适用于企业级的测试自动化需求。

## ✨ 主要特性

### 🧪 测试框架
- **Swagger 自动解析**: 支持 Swagger 2.0 文档自动解析和 API 测试
- **Kubernetes 集成**: 支持 K8s 集群资源管理和容器化测试
- **依赖关系管理**: 支持测试用例间的依赖关系管理
- **测试报告**: 自动生成详细的测试报告和可视化展示

### 🌐 Web 管理界面
- **用户权限管理**: 完整的用户、角色、权限管理体系
- **系统管理**: 菜单、部门、字典等基础数据管理
- **实时监控**: 缓存、任务、日志、在线用户实时监控
- **测试管理**: 测试用例的可视化管理和执行

### 🚀 云原生支持
- **容器化部署**: 支持 Docker 和 Kubernetes 部署
- **微服务架构**: 前后端分离的微服务架构设计
- **高可用性**: 支持集群部署和负载均衡

## 🏗️ 系统架构

```
probeX/
├── src/probeX/
│   ├── framework/           # 核心测试框架
│   │   ├── api/            # API 管理
│   │   ├── client/         # 客户端支持 (HTTP/K8s/MySQL)
│   │   ├── config/         # 配置管理
│   │   ├── service/        # 核心业务服务
│   │   ├── schedule/       # 测试调度系统
│   │   └── utils/          # 工具类
│   ├── probeX-backend/     # FastAPI 后端服务
│   │   ├── module_admin/   # 管理模块
│   │   ├── module_task/    # 任务模块
│   │   └── middlewares/    # 中间件
│   └── probeX-frontend/    # Dash 前端界面
│       ├── views/          # 页面视图
│       ├── callbacks/      # 回调函数
│       └── components/     # 可复用组件
```

## 🛠️ 技术栈

### 后端技术
- **FastAPI**: 高性能的 Python Web 框架
- **SQLAlchemy**: ORM 数据库操作
- **Redis**: 缓存和会话存储
- **MySQL**: 主数据库
- **Uvicorn**: ASGI 服务器

### 前端技术
- **Dash**: Python Web 应用框架
- **Ant Design**: 企业级 UI 组件库
- **Plotly**: 数据可视化
- **JavaScript**: 前端交互逻辑

### 测试框架
- **自研测试框架**: 支持依赖关系的测试用例管理
- **Swagger 集成**: API 测试自动化
- **Kubernetes 客户端**: 云原生测试支持

## 📦 安装部署

### 环境要求
- Python 3.8+
- MySQL 5.7+
- Redis 6.0+
- Kubernetes 1.20+ (可选)

### 快速开始

1. **克隆项目**
```bash
git clone https://github.com/your-username/probeX.git
cd probeX
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置数据库**
```bash
# 创建数据库
mysql -u root -p < src/probeX/probeX-backend/sql/dash-fastapi.sql
```

4. **启动服务**
```bash
# 启动后端服务
cd src/probeX/probeX-backend
python app.py

# 启动前端服务
cd src/probeX/probeX-frontend
python app.py
```

### Docker 部署

```bash
# 构建镜像
docker build -t probex .

# 运行容器
docker run -d -p 8000:8000 -p 8050:8050 probex
```

## 🚀 使用指南

### 命令行工具

probeX 提供了丰富的命令行工具：

```bash
# 生成 OTP 密钥
probeX user otp -f qrcode.png

# 解析 Swagger 文档
probeX swagger parse

# 查询 Kubernetes 资源
probeX kube resource

# 执行测试用例
probeX case -f test_config.yaml

# 管理报告服务
probeX report server start
probeX report server stop
probeX report server status
```

### Web 界面使用

1. **访问系统**: 打开浏览器访问 `http://localhost:8050`
2. **用户登录**: 使用管理员账号登录系统
3. **功能导航**: 通过左侧菜单访问各项功能
4. **测试管理**: 在测试管理模块创建和执行测试用例

## 📋 功能模块

### 测试框架功能
- ✅ Swagger 2.0 文档解析
- ✅ API 接口测试
- ✅ Kubernetes 资源管理
- ✅ 测试用例依赖管理
- ✅ 测试报告生成

### 系统管理功能
- ✅ 用户权限管理
- ✅ 角色权限分配
- ✅ 菜单权限控制
- ✅ 部门组织管理
- ✅ 系统配置管理

### 监控功能
- ✅ 缓存监控
- ✅ 任务调度监控
- ✅ 操作日志监控
- ✅ 在线用户监控
- ✅ 服务器状态监控

## 🔧 配置说明

### 环境变量配置

创建 `.env` 文件：

```env
# 数据库配置
DATABASE_URL=mysql://user:password@localhost/probex
REDIS_URL=redis://localhost:6379

# 应用配置
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True

# Kubernetes 配置
KUBE_CONFIG_PATH=/path/to/kubeconfig
```

### 测试配置

在 `config.yaml` 中配置测试用例：

```yaml
cases:
  - name: test1
    action: Model.create
    params:
      - modelname: "test"
      - modeltype: "NLP"
    return:
      - model_res
      - model_path
    dependencies: [test2, test3]
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 开发环境设置

1. Fork 本仓库
2. 创建功能分支: `git checkout -b feature/AmazingFeature`
3. 提交更改: `git commit -m 'Add some AmazingFeature'`
4. 推送分支: `git push origin feature/AmazingFeature`
5. 创建 Pull Request

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 使用类型注解
- 编写单元测试
- 更新相关文档

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 联系我们

- **项目维护者**: gavin (ygydev@163.com)
- **项目地址**: https://github.com/your-username/probeX
- **问题反馈**: [Issues](https://github.com/your-username/probeX/issues)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**

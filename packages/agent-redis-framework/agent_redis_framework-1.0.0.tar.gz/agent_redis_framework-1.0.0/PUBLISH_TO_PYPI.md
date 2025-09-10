# 发布 agent-redis-framework 到 PyPI 指南

本指南将详细说明如何将 `agent-redis-framework` 包发布到 PyPI (Python Package Index)。

## 前置条件检查

✅ 项目已经具备以下必要文件：
- `pyproject.toml` - 包含完整的项目元数据和构建配置
- `README.md` - 项目说明文档
- `src/agent_redis_framework/` - 源代码目录
- `src/agent_redis_framework/__init__.py` - 包初始化文件，定义了 `__all__`

## 步骤 1: 注册 PyPI 账户

### 1.1 注册账户
1. 访问 [PyPI 官网](https://pypi.org/)
2. 点击右上角 "Register" 注册新账户
3. 填写用户名、邮箱和密码
4. 验证邮箱地址

### 1.2 启用双因素认证（推荐）
1. 登录后进入 Account Settings
2. 启用 Two-factor authentication (2FA)
3. 使用 Google Authenticator 或类似应用扫描二维码

### 1.3 创建 API Token
1. 在 Account Settings 中找到 "API tokens" 部分
2. 点击 "Add API token"
3. 输入 token 名称（如：`agent-redis-framework-upload`）
4. 选择 Scope：
   - 首次发布选择 "Entire account"
   - 后续更新可以选择 "Project: agent-redis-framework"
5. 复制生成的 token（格式：`pypi-xxx...`）
6. **重要：立即保存 token，页面关闭后无法再次查看**

## 步骤 2: 安装构建和上传工具

```bash
# 安装构建工具
uv add --group dev build twine

## 步骤 3: 构建包

```bash
# 清理之前的构建文件
rm -rf dist/ build/ *.egg-info/

# 构建包（生成 wheel 和 source distribution）
uv run python3 -m build
```

构建完成后，`dist/` 目录应包含：
- `agent_redis_framework-1.0.0-py3-none-any.whl`
- `agent_redis_framework-1.0.0.tar.gz`

## 步骤 4: 验证包内容

```bash
# 检查构建的包
uv run twine check dist/*
```

确保输出显示 "PASSED" 且没有错误或警告。

## 步骤 5: 测试发布（推荐）

### 5.1 注册 TestPyPI 账户
1. 访问 [TestPyPI](https://test.pypi.org/)
2. 使用与 PyPI 相同的流程注册账户
3. 创建 API token

### 5.2 上传到 TestPyPI
```bash
# 上传到测试环境
uv run twine upload --repository testpypi dist/*
```

输入用户名：`__token__`
输入密码：你的 TestPyPI API token

### 5.3 测试安装
```bash
# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ agent-redis-framework

# 测试导入
python -c "from agent_redis_framework import RedisConfig, get_redis; print('Import successful!')"
```

## 步骤 6: 正式发布到 PyPI

### 6.1 上传到 PyPI
```bash
# 上传到正式 PyPI
twine upload dist/*
```

输入用户名：`__token__`
输入密码：你的 PyPI API token

### 6.2 验证发布
1. 访问 https://pypi.org/project/agent-redis-framework/
2. 确认包信息显示正确
3. 测试安装：
```bash
pip install agent-redis-framework
```

## 步骤 7: 配置自动化（可选）

### 7.1 使用 GitHub Actions
创建 `.github/workflows/publish.yml`：

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

在 GitHub 仓库的 Settings > Secrets and variables > Actions 中添加：
- `PYPI_API_TOKEN`：你的 PyPI API token

### 7.2 使用 pyproject.toml 配置
可以在 `pyproject.toml` 中添加更多元数据：

```toml
[project]
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
license = {text = "MIT"}
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Database :: Front-Ends",
]
keywords = ["redis", "task-queue", "streams", "scheduling"]

[project.urls]
Homepage = "https://github.com/yourusername/agent-redis-framework"
Repository = "https://github.com/yourusername/agent-redis-framework"
Issues = "https://github.com/yourusername/agent-redis-framework/issues"
```

## 版本管理建议

1. **语义化版本控制**：遵循 `MAJOR.MINOR.PATCH` 格式
   - MAJOR：不兼容的 API 变更
   - MINOR：向后兼容的功能新增
   - PATCH：向后兼容的问题修复

2. **版本更新流程**：
   ```bash
   # 更新 pyproject.toml 中的版本号
   # 提交代码
   git add .
   git commit -m "Bump version to 1.0.1"
   git tag v1.0.1
   git push origin main --tags
   
   # 重新构建和发布
   rm -rf dist/
   python -m build
   twine upload dist/*
   ```

## 常见问题

### Q: 包名已存在怎么办？
A: PyPI 包名必须唯一。如果 `agent-redis-framework` 已被占用，需要选择其他名称，如 `agent-redis-framework-yourname`。

### Q: 上传失败显示权限错误？
A: 检查 API token 是否正确，确保 token 有足够的权限。

### Q: 如何删除已发布的版本？
A: PyPI 不允许删除已发布的版本，只能发布新版本。如有严重问题，可以联系 PyPI 管理员。

### Q: 如何更新包的描述信息？
A: 修改 `pyproject.toml` 和 `README.md`，然后发布新版本。

## 安全注意事项

1. **保护 API Token**：
   - 不要将 token 提交到代码仓库
   - 使用环境变量或 CI/CD secrets 存储
   - 定期轮换 token

2. **代码签名**：
   - 考虑使用 GPG 签名发布
   - 启用 PyPI 的 Trusted Publishers（如果使用 GitHub Actions）

3. **依赖安全**：
   - 定期更新依赖版本
   - 使用 `pip-audit` 检查安全漏洞

---

完成以上步骤后，你的 `agent-redis-framework` 包就成功发布到 PyPI 了！用户可以通过 `pip install agent-redis-framework` 安装使用。
# 贡献指南

感谢您对 pydhis2 的关注！我们欢迎所有形式的贡献。

## 开发环境设置

1. Fork 并克隆仓库
```bash
git clone https://github.com/your-username/pydhis2.git
cd pydhis2
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 安装开发依赖
```bash
pip install -e ".[dev]"
```

4. 安装 pre-commit 钩子
```bash
pre-commit install
```

## 代码规范

- 使用 `black` 格式化代码
- 使用 `ruff` 进行代码检查
- 使用 `mypy` 进行类型检查
- 遵循 Conventional Commits 规范

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/unit/test_client.py

# 生成覆盖率报告
pytest --cov=pydhis2 --cov-report=html
```

## 提交指南

1. 创建功能分支
```bash
git checkout -b feature/your-feature-name
```

2. 提交代码
```bash
git commit -m "feat: add new feature"
```

3. 推送分支并创建 Pull Request

## 提交信息格式

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

类型：
- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档更新
- `style`: 代码格式（不影响逻辑）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建或辅助工具

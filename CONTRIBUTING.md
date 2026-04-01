# 贡献指南

感谢您对 POCI 项目的关注！我们欢迎任何形式的贡献：报告问题、提交代码、改进文档。

## 行为准则
请尊重所有贡献者，保持开放、专业、理性的讨论氛围。

## 如何贡献

### 报告问题
- 在 [Issues](https://github.com/poci-project/poci-sim/issues) 中搜索是否已有类似问题。
- 提交新 issue 时，请包含：
  - 清晰的问题描述
  - 复现步骤（如适用）
  - 环境信息（Python 版本、操作系统等）

### 提交代码
1. Fork 本仓库。
2. 创建功能分支 (`git checkout -b feature/your-feature`)。
3. 提交更改 (`git commit -m 'Add some feature'`)。
4. 推送到分支 (`git push origin feature/your-feature`)。
5. 打开 Pull Request，描述你的更改。

### 代码风格
- 遵循 PEP 8。
- 添加必要的注释和文档字符串。
- 确保所有测试通过 (`pytest`)。

### 安全模块贡献
如果涉及安全相关代码（AMTC、零信任通道、Merkle 审计等），请确保：
- 遵守 `src/poci_safety/` 中的接口规范。
- 提供相应的单元测试。
- 更新 `docs/security/deployment_guide.md`。

## 许可证
贡献者默认同意将代码以双许可证（MIT + Apache 2.0）发布。

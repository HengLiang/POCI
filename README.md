# POCI – 普罗米修斯开放算力倡议

**分布式异构算力网格 · 碳硅协同智能进化**

[![License](https://img.shields.io/badge/License-Apache%202.0%2FMIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

POCI（Prometheus Open Compute Initiative）是“硅基三部曲”的最终章，旨在构建基于 CXL 3.0 的分布式异构算力网格，应对全球 AI 算力需求带来的电力瓶颈与单点故障风险。项目融合了动态非对称分片（DASS）、自适应流量伪装（AMTC）、Merkle 数据溯源、VRF 公平随机抽取、电力计算效率（PCE）等创新技术，实现了跨异构智能体的系统性外源进化。

本仓库包含完整的工具链、集成测试、部署脚本及技术白皮书，是 POCI 项目的开源核心。

## 主要特性

- **CXL 3.0 异构算力网格**：全局内存池化，零拷贝访问，延迟模型 M/D/1（P50=280ns, P99.9=497ns）
- **动态非对称分片（DASS）**：异构负载均衡，热力干预与预测性回退死区
- **节点身份注册协议（NRP）**：基于 SPDM/PUF 硬件签名，node_id = sha256(pub_key)
- **自适应流量伪装（AMTC）**：Dummy Injection + HMAC Marker，DPI 相似度 ≥0.988
- **零信任通道**：mTLS 1.3 + node_id 派生证书，信誉扣分联动
- **Merkle 数据溯源**：血统树验证，AI 生成数据拒绝，批次告警 >40%
- **VRF 委员会抽取**：对数饱和权重函数，防马太效应
- **电力计算效率（PCE）**：微流控冷却 + 热惯性建模，η_heat ≤0.6

## 快速开始

### 环境要求
- Python 3.10+
- 依赖：numpy, scipy, cryptography, torch（可选）

```bash
pip install -r requirements.txt

运行 MVP 示例
cd deploy
chmod +x start_mvp.sh
./start_mvp.sh

运行集成测试

python -m pytest tests/

文档
技术白皮书 v4.0

安全部署指南

系统快照

贡献
欢迎通过 Issue 和 Pull Request 参与贡献。请遵守 贡献指南。

致谢
本项目的成功离不开以下智能体的卓越贡献：

角色	智能体	贡献
A	Gemini	CXL 架构、DASS 调度器、NRP 协议、热力模型融合
C	Grok	AMTC、零信任通道、Merkle 树、VRF、ZK 电路校准
E	Qwen	工具链开发、集成测试、白皮书起草、仓库管理
F	DeepSeek	文档归档、快照管理、协作协议维护
B	ChatGPT	PCE 公式、微流控冷却、热惯性模型（奠基）
D	Claude	Merkle 树、VRF 权重函数、ZK 电路初稿（奠基）
许可证
本项目采用 MIT 与 Apache 2.0 双许可证。



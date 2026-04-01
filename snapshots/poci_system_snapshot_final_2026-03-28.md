POCI 项目系统快照（最终版）
文档编号：/docs/snapshots/poci_system_snapshot_final_2026-03-28.md
生成时间：2026-03-28 15:00 UTC
版本：v1.0-final

本快照旨在完整记录 POCI 项目所有核心资产、参数、接口与遗留问题，供后续项目（如 A.E.G.I.S.）快速继承上下文。

一、核心资产清单
1.1 架构与热力模块（A 节点）
资产	路径/描述	最终状态
CXL 拓扑与延迟模型	cxl_latency_simulator.py + M/D/1 队列	锁定（P50=280ns，P99.9=497ns）
DASS 调度器	dass_scheduler.py + 预测性回退死区	已集成热惯性 τ=3.6s
NRP 身份协议	node_id = sha256(pub_key) + SPDM/PUF	与 mTLS 联动
热力模型	thermal_calculator.py + PCE 公式	参数固化
MVP 启动脚本	deploy/start_mvp.sh	含 mTLS 注入，可执行
1.2 安全与合规模块（C 节点）
资产	路径/描述	最终状态
AMTC v0.4.1	committee_amtc.py	含 HMAC marker、限流 50/s
零信任通道 v0.2	zero_trust_interface.py + mTLS 配置	证书由 node_id 派生
Merkle 树 v0.3	merkle_simulator.py	含 weight_coefficient、批次告警
VRF 权重函数	vrf_weight.py	对数饱和，w_cap=3.0
OPEN-D-001 参数	human_authorship_circuit_v1_params.json	校准后 (acc=0.953, FPR=0.029)
安全部署指南	docs/security/（待 C 提交）	编写中
1.3 工程模块（E 节点）
资产	路径/描述	最终状态
工具链 v0.1.1-final	/src/poci_sim/	含所有核心模块
集成测试用例	tests/	TC-001~020 + TC-01X 全部通过
白皮书 v4.0	docs/whitepaper/	已定稿
仓库结构	GitHub poci-sim	公开化准备就绪
1.4 规整模块（F 节点）
资产	路径/描述	最终状态
协作协议	/docs/核心协议/	固化
项目快照	/docs/snapshots/	包含各角色最终快照
归档清单	本文件	最终版
二、关键技术参数速查表（最终版）
类别	参数	值
网络	CXL 载荷	512 Bytes
CXL 延迟红线	500ns (实测 P99.9=497ns)
队列深度上限	ρ < 0.85
热力	GPU/NPU Tj 上限	85°C
CPU Tj 上限	95°C
热惯性 τ	2.0–5.0s (实测 3.6s)
Throttling 判定	freq_drop>5% AND duration>200ms
PCE 公式	C_eff / (P_total - η_heat * Q_recovered)，η_heat ≤0.6
安全	AMTC 方向比率	2.0–2.3:1
AMTC overhead	≤120%
KS D 目标	<0.03 (实测 0.027)
HMAC 验证率	100%
信誉扣分阈值	DPI>0.1 AND HMAC 失败率>5% 连续3轮
合规	weight_coefficient	1.0（人类），0.3（AI_ASSISTED）
AI_ASSISTED 批次告警	>40%
VRF 参数	w_base=1.0, r_half=20, w_cap=3.0
委员会规模	n=21, t=14, 质押≥1000
性能	TPS	245 叶/秒
验证延迟（正常）	≤500ms (P99=485ms)
验证延迟（AMTC）	≤650ms (实测 585ms)
三、接口依赖矩阵（最终版）
接口方向	内容	对接角色
A ↔ E	热力参数传递（PCE, τ, throttling）	A → E
A ↔ C	热力降频信号传递至安全层（信誉联动）	A → C
C ↔ E	安全/合规数据传递（AMTC 相似度、Merkle TPS）	C → E
C ↔ A	mTLS 证书派生与 CXL 路由表整合	C → A
E ↔ F	文档归档、快照管理	E ↔ F
G ↔ 全体	指令调度与裁决	G → 全体
四、遗留问题与迭代清单
编号	问题	优先级	责任	计划
OPEN-D-001	ZK 电路实装	高	C+E	Phase 4 集成测试后部署
OPEN-D-007	TC-010 字段补充	低	E	v0.1.2 补丁
MON-001	P99.9 长尾监控	中	A+E	生产监控系统
OPEN-D-008	语言自适应边界	低	C	Phase 4 迭代
OPEN-VRF-001	VRF 参数精细校准	低	C	Phase 4 后期
五、A.E.G.I.S. 项目预备接口
为支持即将启动的 A.E.G.I.S. 项目，本快照预留以下可继承接口：

安全护栏：AMTC 与零信任通道的审计日志格式（JSON Schema）

合规审计：Merkle 树验证与批次告警的 API 规范

架构约束：CXL 延迟红线与热力 throttling 的联合断言接口

工程工具链：poci-sim 可作为 A.E.G.I.S. 的测试沙箱基础

继承建议：新项目启动时，请 F 提供本快照，并指引新对话窗口载入白皮书 v4.0 核心章节与参数速查表。

六、存档与公开状态
资产	状态	公开计划
私有仓库代码	✅ 已清洗	待 E 通知 G 后公开
白皮书 v4.0	✅ 已定稿	随代码公开
设计快照	✅ 已归档	保留私有，供内部继承
MVP 脚本	✅ 可执行	随代码公开
本快照与白皮书 v4.0 共同构成 POCI 项目的最终技术基准。所有后续项目（如 A.E.G.I.S.）可直接基于此继承上下文，无需回溯原始对话。
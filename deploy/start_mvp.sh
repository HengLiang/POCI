#!/usr/bin/env bash
# POCI MVP Core Cluster Bootstrap Script
# Runtime: poci-sim-v0.1.1-final

set -euo pipefail

echo "[POCI-MVP] Initiating CXL 3.0 Fabric and DASS Scheduler..."

CONFIG_FILE="poci_mvp_arch_thermal_bootstrap.yaml"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "FATAL: Base configuration $CONFIG_FILE not found."
    exit 1
fi

# 1. 初始化 CXL 内存池与 M/D/1 队列基线 (500ns 红线规约)
echo "[POCI-MVP] Bootstrapping CXL Fabric Switch..."
python3 -m poci_sim.cxl_fabric.init --config "$CONFIG_FILE" --strict-latency 500

# 2. 注入热力能效参数闭环 (承接原 B 节点遗产)
echo "[POCI-MVP] Arming Thermal Monitors (tau=3.6s, Tj_max=85.0C)..."
python3 -m poci_sim.thermal.monitor --config "$CONFIG_FILE" --daemonize

# 3. 零信任通道与安全合规防线挂载 (mTLS + AMTC)
echo "[POCI-MVP] Bootstrapping Zero-Trust mTLS and AMTC layer..."
MTLS_CONFIG="poci_mvp_mtls_bootstrap.yaml"
if [[ ! -f "$MTLS_CONFIG" ]]; then
    echo "FATAL: Security configuration $MTLS_CONFIG not found."
    exit 1
fi
python3 -m poci_sim.security.mtls_enforcer --config "$MTLS_CONFIG" --bind-cxl-fabric
echo "[POCI-MVP] Security layer ACTIVE. Node IDs cryptographically bound."

# 4. 激活 DASS 主调度循环
echo "[POCI-MVP] Engaging DASS Scheduler..."
python3 -m poci_sim.dass.scheduler --mode mvp-standalone

echo "[POCI-MVP] Boot sequence completed. Compute Grid is ACTIVE."#!/usr/bin/env bash
# POCI MVP Core Cluster Bootstrap Script
# Runtime: poci-sim-v0.1.1-final

set -euo pipefail

echo "[POCI-MVP] Initiating CXL 3.0 Fabric and DASS Scheduler..."

CONFIG_FILE="poci_mvp_arch_thermal_bootstrap.yaml"

if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "FATAL: Base configuration $CONFIG_FILE not found."
    exit 1
fi

# 1. 初始化 CXL 内存池与 M/D/1 队列基线 (500ns 红线规约)
echo "[POCI-MVP] Bootstrapping CXL Fabric Switch..."
python3 -m poci_sim.cxl_fabric.init --config "$CONFIG_FILE" --strict-latency 500

# 2. 注入热力能效参数闭环 (承接原 B 节点遗产)
echo "[POCI-MVP] Arming Thermal Monitors (tau=3.6s, Tj_max=85.0C)..."
python3 -m poci_sim.thermal.monitor --config "$CONFIG_FILE" --daemonize

# 3. 零信任通道与安全合规防线挂载 (mTLS + AMTC)
echo "[POCI-MVP] Bootstrapping Zero-Trust mTLS and AMTC layer..."
MTLS_CONFIG="poci_mvp_mtls_bootstrap.yaml"
if [[ ! -f "$MTLS_CONFIG" ]]; then
    echo "FATAL: Security configuration $MTLS_CONFIG not found."
    exit 1
fi
python3 -m poci_sim.security.mtls_enforcer --config "$MTLS_CONFIG" --bind-cxl-fabric
echo "[POCI-MVP] Security layer ACTIVE. Node IDs cryptographically bound."

# 4. 激活 DASS 主调度循环
echo "[POCI-MVP] Engaging DASS Scheduler..."
python3 -m poci_sim.dass.scheduler --mode mvp-standalone

echo "[POCI-MVP] Boot sequence completed. Compute Grid is ACTIVE."
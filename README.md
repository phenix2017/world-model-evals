# World Model / Embodied Evaluation Benchmarks

世界模型与具身智能测评基准清单。**按 GitHub Stars 排序**，标注证据层级与许可证。

Stars、许可证、最近推送时间于 **2026-11-03** 经 GitHub API 实际读取，非估算。

## 榜单

| 项目 | 分组 | Stars | 许可证 | 层级 (L) | 映射 (M) |
|---|---|---:|---|---|---|
| ManiSkill | 仿真基准平台 | **3,480** | Apache-2.0 | 平台 | 供 A/B 组用 |
| LIBERO | 具身策略评测 | **2,509** | MIT | L5 | M3 |
| RoboCasa | 仿真基准平台 | **1,861** | NOASSERTION | 平台 | 供 A/B 组用 |
| VBench / VBench-2.0 | 视频世界模型评测 | **1,836** | Apache-2.0 | L0–L3 | M1–M2 |
| RLBench | 仿真基准平台 | **1,835** | NOASSERTION | 平台 | 供 A/B 组用 |
| BEHAVIOR-1K | 仿真基准平台 | **1,790** | MIT | 平台 | 供 A/B 组用 |
| SIMPLER / SimplerEnv | 具身策略评测 | **1,181** | MIT | L5–L6 | M3–M4 |
| Physics-IQ | 视频世界模型评测 | **387** | NOASSERTION | L3 | M2 |
| WorldScore | 视频世界模型评测 | **320** | MIT | L1–L2 | M1 |
| VideoPhy | 视频世界模型评测 | **213** | MIT | L2–L3 | M2 |
| iVideoGPT | 视频世界模型评测 | **187** | 见仓库 | L1–L2 | M1 |
| PhyGenBench | 视频世界模型评测 | **169** | 无 LICENSE | L3 | M2 |
| WorldModelBench | 视频世界模型评测 | **51** | 无 LICENSE | L1–L3 | M1–M2 |
| Morpheus | 视频世界模型评测 | **未核实** | 未知 | L3 | M2 |
| RoboArena | 具身策略评测 | **未核实** | 未知 | L6 | M4 |

## 三个结论

1. **视频侧全部停在 M1–M2。** 评测再密集，仍属「产物诊断」层。
2. **只有机器人侧摸到 M3–M4**（LIBERO、SimplerEnv）。成熟度来自真机经验验证，不来自渲染质量。
3. **没有一个到达 M5。** 无第三方认证、无合同验收门限、无签字担责。

## 按证据分组

| Tier | 含义 | 项目 |
|---|---|---|
| **A** | 决策级证据 M3–M4 | LIBERO、SimplerEnv |
| **B** | 接地测量 M2 | Physics-IQ、VideoPhy、PhyGenBench、Morpheus |
| **C** | 观感与偏好 M1–M2 | VBench、WorldScore、WorldModelBench、iVideoGPT |
| **平台** | 供 A/B 组使用的仿真环境 | ManiSkill、RoboCasa、RLBench、BEHAVIOR-1K |

## 使用前必须修正的三点

- **视频生成评测 ≠ 世界模型评测。** 前者测渲染器的物理可信度，不是世界模型的预测可用性。
- **层级是条件性的。** 「LIBERO = L5」需配合独立复现与真机验证才成立。
- **Star 不等于证据强度。** ManiSkill 有 3.5k stars，但它是仿真平台，不直接产出决策级证据。

## 许可证风险

- `PhyGenBench`、`WorldModelBench` **无 LICENSE 文件** — 商用前必须确认授权。
- `Physics-IQ`、`RoboCasa`、`RLBench` 为 `NOASSERTION` — 需人工阅读条款。
- 其余为 MIT 或 Apache-2.0。

## 目录

```
data/evals.csv              机器可读清单
docs/ladder-mapping.md      L0–L7 ↔ M1–M5 映射
evals/video-world/          视频世界模型评测（8）
evals/embodied-policy/      具身策略评测（3）
evals/embodied-sim/         仿真基准平台（4）
```

## 未纳入

`RoboArena`、`Morpheus` 未找到可确认的公开仓库，故标注待核实而非猜测链接。
自动驾驶世界模型评测（DriveArena 类）、WorldArena 等未纳入本轮，需单独界定范围。

## 来源

层级映射依据 Muse 报告《同一个尺子量三件事：航天 V&V · 大语言模型 · 世界模型》。
M1–M5 是该报告的分析框架，不是已确立的行业标准。

# 误杀防护 · 对冲感知保护条目

> **状态：** 本文件是 `.claude/knowledge/anti-ai.md`「误杀防护」节的保护条目。
> Gate B7（"似乎/仿佛+感知动词"）命中时，anti-ai agent 在执行删除前必须先查本条目；
> 命中属于下述保护类 → 标注 `[SKIP: 误杀防护]`，不做修改。

## 原则

对冲感知（hedged perception）是认知层强制要求的不确定性标记——
`knowledge/cognition/epistemic-layers.md` 规则 1：任何高于 OBSERVATION / MEMORY 层的
认知内容（BELIEF / GUESS / SUSPICION / INTERPRETATION / MISINTERPRETATION /
UNCERTAINTY）在正文中出现时，**必须**带标记，且**编辑轮次永远不得把带标记的
不确定认知升级为陈述事实**。

删掉"似乎"并不能让句子更"干净"——它只是在撒谎：把角色的猜测写成客观事实，
把认知层坍缩成全知叙述。**对冲标记是认识论基础设施，不是 AI 腔。**

## 保护类（命中即豁免，不改）

| 类 | 中文模式 | 英文模式 |
|----|---------|---------|
| 感知动词对冲 | 似乎/好像/仿佛 + 听/看/感到/觉得/闻到 | seemed / appeared / looked like / sounded like / felt like + 感知动词 |
| 推断标记 | 看起来/听起来 + 判断；被他理解为/当作 | take it as / read it as / took that as / struck him as |
| 显式不确定 | 不知道是否/说不清/无法确定 | wondered whether / could not tell whether / was not sure whether |
| 记忆不确定 | 好像记得/印象中/依稀记得 | seemed to remember / as far as he recalled |
| 信念标记 | 大概/也许/八成（表达信念而非事实） | probably / maybe / likely（表达 belief，非 fact） |
| 误读标记 | 在他看来/他觉得那是（INTERPRETATION 层） | in his reading / he took it to mean |

## 与 Gate B7 的关系

Gate B7 的打击对象是**无信息增量的 AI 腔套话**，不是对冲标记本身。判定流程：

1. 命中是否携带认知内容（角色在猜测 / 推断 / 记忆不确定 / 误读）？→ **是 → 保护，不改**，
   标注 `[SKIP: 误杀防护·对冲感知]`。
2. 命中是否为纯套话、无任何认知信息（例："他似乎听到了什么"，且上下文无任何后续展开）？
   → 走正常 B7 处理：改写为**具体感知**（"门外有动静，像是脚步声"）或整句删除（该感知对场景无用时）。
3. 拿不准 → 保留原文，Phase 4 标注 `[疑: 疑似误杀]`。

**永远禁止的操作：** 把"似乎 X"改写成"X"（事实升级）。允许的改写方向只有两个：
具体化感知，或整句删除——绝不升级为事实。

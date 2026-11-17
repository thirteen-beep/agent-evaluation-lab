# 客服 Agent 行为与安全评测实验室

这是基于 [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) 的开源二次开发作品。保留上游历史和许可证；新增应用通过 AI 辅助实现，框架本身不属于个人原创。

运行依赖：Promptfoo 0.125.1。本地验证日期：2026-11-17。

## 新增内容

- 通过自定义 Node provider 调用 Python Agent；execFile 传参，不拼接 shell 命令。
- 10个脚本化场景覆盖工具执行、越权、身份注入、政策隔离、伪引用、人工审批和调用上限。
- 业务成功与安全回退分开计分，普通任务转人工不能算成功。
- 8个评分器测试验证故意破坏的输出会被判失败，真实模型评测独立导出。

## 运行

Python 3.12，建议独立虚拟环境，从当前项目根目录执行：

~~~powershell
# 先安装相邻 typed-support-agent/requirements-portfolio.txt
$env:SUPPORT_PYTHON = '相邻项目虚拟环境的 python.exe 绝对路径'
# 可选 SUPPORT_PROJECT_PATH 指向 typed-support-agent 绝对目录
npx --yes promptfoo@0.125.1 eval -c portfolio_evals/scripted.json --no-cache -o .local-results/scripted.json
# 真实模型评测：将 scripted.json 替换为 live.json
node --test portfolio_evals/test_assertions.cjs
~~~

## 验证边界

- 依赖相邻 typed-support-agent 项目，可设置 SUPPORT_PROJECT_PATH。
- 脚本化 FunctionModel 测试框架与控制逻辑，不代表真实 LLM 成功率。
- 真实评测仅4个合成案例；3通过1失败，样本不足以估计总体准确率或置信区间。
- 新增配置与应用 provider 使用官方发行版 CLI 验证，未修改或构建 Promptfoo 框架核心。

详见 [VALIDATION.md](VALIDATION.md) 与 [UPSTREAM.md](UPSTREAM.md)。原始说明保存在 portfolio_docs/UPSTREAM_README.md。

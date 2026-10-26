# M1-001 环境与骨架验证记录

日期：2026-10-26（Asia/Shanghai）。结论：最小环境、锁文件重建、契约与夹具检查已验证；订单/物流函数由开发者动手，尚未实现，模型适配未验证。M1-001进行中，不代表M1或G1完成。

## 1. 授权、工作区与实际版本

用户本次明确要求实施学习骨架计划；没有提交、推送或模型调用授权。本次未提交或推送，未调用模型、真实业务平台或业务写工具。

开始时：工作区 `E:\product\corpMind`，已有分支 `docs-initial-design`，HEAD `18f8d72`，7个已跟踪文件修改、2个未跟踪文档，暂存区为空。保留原有修改，在同一目录创建 `codex/m1-001-readonly-tools`。以下检查针对未提交工作区，不对应新增代码提交。

| 项目 | 实际结果 |
| --- | --- |
| 系统 | Windows x86_64；其他系统未实测 |
| Python | CPython 3.12.10；项目要求 `>=3.12,<3.13`，`.python-version` 固定3.12.10 |
| 解释器来源 | `C:\Users\jianghaojie\AppData\Local\Programs\Python\Python312\python.exe`；本机 `py` 未识别安装，不使用它建环境 |
| uv / 构建后端 | uv 0.13.5，项目内 `.tools/uv/bin/uv.exe`；`uv_build==0.13.5` 为构建依赖，独立固定在pyproject中 |
| 运行依赖 | Pydantic 2.14.1，pydantic-core 2.50.1；完整传递依赖与发行物哈希见uv.lock |
| 开发依赖 | pytest 9.1.1、Ruff 0.17.2 |
| 本项目版本 | corpmind 0.1.0，仅为学习骨架包版本，不改变v0.2需求基线 |
| 布局 | `src/corpmind`、`tests`；uv构建后端提供可编辑包安装，不通过测试配置临时添加src路径 |
| 隔离 | `.venv`与`.venv-verify`；`include-system-site-packages = false` |
| 资料 | `m1-001-fixture-v1`；固定时刻2026-10-26T10:00:00+08:00 |

uv.lock本次SHA-256：`017afb808a0bb6216eaf52f73e7d0c98b7721b02ea0b1e6e927ede827129943d`。锁文件解析13个包（含本项目），实际安装集合13项，两个环境的包名与版本完全一致。`uv_build`属于构建隔离环境，不计入运行环境的13项。

## 2. 实际执行命令与结果

下列PowerShell命令均在仓库根目录执行。安装路径是本机验证记录；其他机器需要可用的3.12.10解释器，不能照抄本机绝对路径。本次只验证了当前Windows环境。

首次引导uv（使用已有Python的pip，未修改全局依赖）：

```powershell
python -B -m pip install --disable-pip-version-check --no-cache-dir --retries 0 --target .tools/uv uv
.\.tools\uv\bin\uv.exe --version
```

退出码均为0，实际安装uv 0.13.5。项目通过`required-version`要求此版本，引导命令本身不锁版本；后续不能把新下载的任意uv版本视为本轮已验证版本。

生成锁文件：

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.uv-cache'
$env:UV_PYTHON_DOWNLOADS = 'never'
.\.tools\uv\bin\uv.exe lock --python 'C:\Users\jianghaojie\AppData\Local\Programs\Python\Python312\python.exe'
```

退出码0，解析13个包。接着使用相同缓存执行`sync --locked`失败：Windows拒绝缓存归档目录重命名，退出码1，没有将失败计为安装成功。后续改用无缓存、复制安装完成主环境：

```powershell
$env:UV_PYTHON_DOWNLOADS = 'never'
$env:UV_CONCURRENT_DOWNLOADS = '1'
.\.tools\uv\bin\uv.exe --no-cache sync --locked --link-mode copy --python 'C:\Users\jianghaojie\AppData\Local\Programs\Python\Python312\python.exe'
```

退出码0，安装13项。该方式需要下载依赖，不代表支持离线安装。uv操作在本轮受限执行环境中遇到网络与临时文件权限限制后，经工具权限审核在正常本机环境完成。

锁文件一致性检查与全新环境重建：

```powershell
$env:UV_PYTHON_DOWNLOADS = 'never'
.\.tools\uv\bin\uv.exe --no-cache lock --check --offline

$env:UV_CONCURRENT_DOWNLOADS = '1'
$env:UV_PROJECT_ENVIRONMENT = Join-Path (Get-Location) '.venv-verify'
.\.tools\uv\bin\uv.exe --no-cache sync --locked --link-mode copy --python 'C:\Users\jianghaojie\AppData\Local\Programs\Python\Python312\python.exe'
```

两项退出码均为0。第一次在受限临时目录执行离线锁文件检查时曾因写入解释器缓存失败，退出码1；随后在正常本机临时目录重跑通过。uv环境变量只在对应命令进程中设置，未写入机器或用户配置。若手动在同一个终端完成重建，继续主环境操作前须移除`UV_PROJECT_ENVIRONMENT`，避免后续uv命令沿用验证环境。

## 3. 日常检查与第一轮练习

已经建立环境后，这些命令不需要激活虚拟环境、联网或配置密钥：

| 实际命令 | 退出码及结果 | 能说明什么 |
| --- | --- | --- |
| `.\.venv\Scripts\python.exe -m pytest -q` | 0；14 passed，1 deselected | 契约和夹具骨架检查通过 |
| `.\.venv-verify\Scripts\python.exe -m pytest -q` | 0；14 passed，1 deselected | 第二个环境可复现骨架检查 |
| `.\.venv\Scripts\ruff.exe check src tests` | 0；All checks passed | 静态检查通过 |
| `.\.venv\Scripts\ruff.exe format --check src tests` | 0；10 files already formatted | 格式检查通过；曾发现1处格式差异，修正后重检 |
| `.\.venv\Scripts\python.exe -m pytest --collect-only -q -m exercise` | 0；1个练习被发现，14个其他检查未选择 | 练习能被单独发现 |
| `.\.venv\Scripts\python.exe -m pytest -q -m exercise tests/test_order_exercise.py` | **1；1 failed，NotImplementedError** | 查询尚未实现，练习未通过；不是成功验证记录 |

两环境通过`importlib.metadata.distributions()`比较了全部已安装包名和版本；验证环境还以`python -I`成功导入corpmind，路径指向`src/corpmind`，说明可编辑安装可用，不依赖当前目录补入源码路径。

文档与工作区检查：89个本地链接、41个页内锚点可解析，26份文本文件（含未跟踪源码与文档）无行尾空白。`git diff --check`退出码0。与本轮开始时的SHA-256对比确认，G0记录、通用提示词文档、需求规格、发布计划和LICENSE保持原样；其余原有文档仅作当前骨架相关的增量同步。

默认pytest配置显式排除exercise，并在输出显示deselected；没有skip或xfail。首个练习目前应当失败：你要在`get_order`中完成查询逻辑，让这个真实断言通过。下一步阅读 [学习指南第2节](m1-001-learning.md#2-当前只做练习1成功查询订单)，本轮只做该练习。

## 4. 未验证事项与完成边界

- 查询入口的参数拦截、业务组与工具授权、错误转换、证据组装及物流关联检查均待开发者实现。类型测试通过不证明查询入口执行了这些检查。
- 不存在、跨组、缺少身份、工具禁用、参数错误和物流成功/失败的查询级测试尚未编写或执行；受控故障机制通过不代表查询函数已正确处理故障。
- 没有实现只读重试调用方、注册表、模型结构化调用、完整轮次/时间/任务累计限额、核心循环或任务状态机。AC-07、AC-15、AC-16完整验收未执行。
- 模型仍为后续验证事项：供应商与模型、账户地域、业务空间、端点、SDK兼容性及用量记录需确认；本轮没有读取或使用密钥，没有付费调用。
- 真实订单平台、业务写入、工单、登录、MCP、RAG、界面、CI、部署、完整模型评测均未实现或验证；不扩展多Agent。
- 本地工具、虚拟环境、缓存和验证环境均由.gitignore排除。既有G0记录保留为历史依据，本次没有改写历史评审或宣布新阶段通过。

参考官方说明：[uv安装](https://docs.astral.sh/uv/getting-started/installation/)、[锁定与同步](https://docs.astral.sh/uv/concepts/projects/sync/)、[项目配置](https://docs.astral.sh/uv/concepts/projects/config/)、[Pydantic严格模式](https://docs.pydantic.dev/latest/concepts/strict_mode/)、[pytest标记](https://docs.pytest.org/en/stable/how-to/mark.html)。这些说明不替代本项目的实际检查结果。

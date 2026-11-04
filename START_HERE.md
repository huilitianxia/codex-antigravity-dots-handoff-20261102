# Dots 从这里接手

> **最新接手入口：2026-11-04，已含下午扩大投放及页面核验** → [Antigravity 接手说明](progress/20261104/README.md) · [当前结构化状态](progress/20261104/CURRENT_STATE.json) · [完整近期讨论](progress/20261104/CONVERSATIONS.md) · [本批次文件原件](progress/20261104/FILES.md)。用户已要求暂停新业务改动；Dragon 由用户另外导入。原 11/2、11/3 内容保留为历史，最新订单统计撤回说明继续有效。仓库现由用户设为公开，方便网页版 Gemini 阅读。

> **最新接手入口：北京时间 2026-11-03 01:50 快照（含 01:54 分工与订单纠正）** → [本轮进度与未完事项](progress/20261103/README_PROGRESS_20261103_0026.md) · [结构化状态](progress/20261103/CURRENT_PROGRESS_20261103_0026.json) · [新增已提交批次清单](progress/20261103/SUBMITTED_ARTIFACT_MANIFEST.json)。B17 已在售并核对库存闭环；B18 因高价限制不可售，单次 $7.20 尝试已获保存回执但尚未确认持久化，禁止重复创建、扣库存或继续降价。只同步文本与原件哈希清单，新二进制未上传。下文保留原始 11/2 交接历史；状态冲突以最新有日期的独立证据为准，不代表全店分类或历史报错清零。


## 阅读顺序

1. 阅读 [CURRENT_STATE.md](CURRENT_STATE.md)，以最新正式回执与独立验收为准。
2. 阅读 [UPLOAD_STATUS.md](UPLOAD_STATUS.md)，确认上传和校验是否完成。
3. 按 [会话索引](indexes/conversations.json) 查相应业务对话；`chat-*.md` 是可读对话，`activity-*.jsonl` 是工具操作和文件修改详情，`codex-events` 是补充的原始公开事件。Antigravity 保留原 step 编号。
4. 用 [文件清单](manifests/business-files.json) 将对话中的 C/D/E 盘原路径映射到仓库内的 `files/C`、`files/D`、`files/E`。`storage=git` 可直接读取；`storage=release` 先恢复附件。

## 当前最重要的边界

- 8 个 FBM 报价已经保存并独立核对成功，详情见 CURRENT_STATE 和验收 JSON；不用重复提交。
- 第 20 批已提交，但 403 行不是全成功。第 19 批当前文件与已上传版本不一致，先对版本和回执，不能直接重传。
- 事故价格表、旧批量删除表、旧家族表和已提交历史文件都是追溯材料，不能因为存在于仓库就再次执行。
- 不把旧助手的“完成”“全部生效”等文字当验收；区分文件已生成、提交已接受、回执结果、后台字段、买家页面这几层。
- 任何新的价格、促销、家族、工单或删除动作，按用户在接手后的实际指令推进。本次交接本身不启动新的店铺改动。

## 恢复附件

使用 Python 3.11 或以上。在已登录且能读取这个私有 GitHub 仓库的环境运行：

```bash
python tools/restore.py --download --output .
```

可使用现有 Git 登录，也支持环境变量 `GH_TOKEN` 或 `GITHUB_TOKEN`；不要把凭据写进仓库。程序校验每个下载包和每个还原文件的 SHA-256，遇到不同内容的现有文件会停止而不会覆盖。

仅恢复某类附件，例如正式回执：

```bash
python tools/restore.py --download --output . --match '*processing-summary*.xlsm'
```

搜索业务记录：

```bash
python tools/search.py '22933941801' --scope all
```

项目脚本中可能仍有原电脑的绝对路径，接手环境需要按文件清单调整路径；不要直接批量运行历史脚本。这里只恢复文件，不自动执行任何店铺操作。

## 覆盖说明

混合对话按实际用户消息段筛选，保留选中业务段的上下文和公开操作。无关段落不导入。辅助事件流只收入可明确划定的业务轮次；被新消息改变主题的混合轮次，以 `activity` 为主要记录。最后 8 个 FBM 的补充浏览器操作另存 `codex-fbm-closure`。

不包含账号密钥、登录会话、私有推理、机器运行环境、无关业务，以及完整 PSD/原片库。大素材保留本地原路径和哈希索引，按需再取。只能覆盖当前电脑仍保存的记录和文件，不承诺找回已删除或只存在云端的历史，也不声称恢复所有未留存的旧文件版本。

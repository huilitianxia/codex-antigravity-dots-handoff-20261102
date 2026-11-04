# 覆盖及例外

- 用户冻结业务改动后，只进行了归档、整理、校验和 GitHub 上传。
- 近期讨论：北京时间 2026-11-02 起，原本机两段当前聊天源的完整可见用户/助手消息、公开工具调用和结果；内部推理、系统/开发者提示和运行状态不导出。
- 业务文件：3683 个直接入库，538,301,539 字节；另有 1 个 149,436,186 字节原片在 Release，总计 3,684 个业务文件。嵌入图片 114 个，38,507,105 字节。
- 原有 11/2、11/3 仓库历史与附件 Release 不删除。本批次直接上传原生文件，不只上传清单。
- Dragon 的云端讨论和独立导出没有包含；Codex 当时收到的分工/输入文件是本地历史证据，不能替代用户后续导入的 Dragon 最新状态。
- [未能按原路径取到的引用候选](manifests/unavailable-references.json) 包含已清理临时文件，也可能含文本解析出的非实际路径；不能据此声称所有候选都是真实缺失文件。能从记录中提取的嵌入图片已另存，未伪造不存在的历史版本。
- [排除清单](manifests/exclusions.json)：依赖包、运行环境、缓存、登录材料以及超出业务归档范围的大型可编辑源。没有复制整块硬盘、完整 PSD 库、Chrome 登录环境或 Dragon 云端数据库。
- [凭据清理计数](manifests/redactions.json)：只修改导出副本。文本和 Office/ZIP 内部成员均检查，原始与导出哈希分别记录；不能把“哈希不同”解释为业务价格或答案被修改。
- 原始截图和旧回执包含的是当时状态，前台选用、广告归因和订单明细都可能滞后；本批次不能证明扩大投放后的效果或全店已无异常。


## 大型原件补充

唯一超过单文件 Git 限制的 149 MB 旧原片也纳入本次上传，直接保存在 [本批次 Release](https://github.com/huilitianxia/codex-antigravity-dots-handoff-20261102/releases/tag/4a-amazon-update-20261104)：[4a-original-video-66ea00d89618.mp4](https://github.com/huilitianxia/codex-antigravity-dots-handoff-20261102/releases/download/4a-amazon-update-20261104/4a-original-video-66ea00d89618.mp4)。原路径、大小和 SHA-256 见 [large-files.json](manifests/large-files.json)。这只归档既有素材，没有制作或修改视频。该项不再作为未上传排除项。


## 最终上传验收

[远端文件与附件验收回执](manifests/UPLOAD_RECEIPT.json) 覆盖数据提交 `e923ebac4a470bed23c33315204f37877e4db831` 的全部文件。关键入口匿名访问 HTTP 200，149 MB 原片的匿名下载、大小和服务器 SHA-256 全部一致。后续仅补充这份回执及说明，最终主分支还会独立再核对。

[运行环境排除目录](manifests/runtime-exclusions.json) 记录实际排除的 5 处依赖和缓存；它们不属于业务资料。

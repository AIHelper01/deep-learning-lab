# 目录整理记录

日期：2026-10-15。

完整整理前备份：`E:\deep-learning-lab-backup-20261015-092728.zip`。

- 所有原文件均保留，路径对应见 [文件映射](file-map.json)。旧依赖、README 和锁文件已归档。
- [原迁移说明](original/migration-notes.md)与[原迁移清单](original/migration-manifest.json)是历史记录，其路径描述整理前状态。
- 原项目导览保留在 original/，当前入口以根 README 和 docs/learning-path.md 为准。
- 2026-10-18 起 original/ 内两个中文文件名改为 ASCII（`migration-notes.md`、`project-tour.md`），使仓库内所有目录名与文件名均为英文；文件内容与 `file-map.json` 的 `old` 列仍保留历史名称。
- 12 个 Notebook 的既有 cell metadata、execution_count 与历史输出保留；修改仅涉及路径、并为本地实验新增目录准备单元。
- 所有原始图片、数据、词表与归档依赖保持字节内容不变。
- 目标检测的外部工程命令、示例环境路径和原本缺失的配置文档引用保留。训练算法未作重构。
- 新依赖文件尚未安装或锁定；未运行训练，不宣称已解决原有兼容问题。

此次仅增加 Git 忽略规则，没有初始化 Git 仓库。

## 静态校验结果

- 12 个 Notebook 均可解析，代码单元静态语法检查通过。
- 143 个原有代码单元已与备份比较，变化仅为约定的路径替换；模型和训练逻辑未改动。
- 48 个图片、数据、词表及归档文件与备份字节一致。
- 3 套新环境的 requirements.txt 与 pyproject.toml 依赖列表一致。
- 检查了 80 处本地链接；除原有 6 个外部检测工程引用外均可解析。

机器可读结果见 [validation.json](validation.json)。新增环境和训练运行情况仍为未验证。整理脚本作为文本归档保存，不能直接重复运行。

# 遗留中文 notebook（只读归档）

这里保存的是本仓库早期的中文 notebook，模块为「自然语言处理（PaddlePaddle 路线）」。归档原因：

- 结构与重构后的英文母本（`english/03-sentiment-analysis/paddle/notebooks/`）不一致，无法逐单元对齐；
- 依赖与当前锁定环境不匹配，在当前环境中无法复现运行；
- 部分单元存在语法错误或残留的失败输出，已保存的输出与代码不同步。

现行中文课程位于 `03-sentiment-analysis/paddle/notebooks/`，由仓库根目录的 `scripts/build_chinese_course.py`
从英文母本镜像生成：中文讲解、中文输出、中文图表，且与英文课程一一对应。

归档文件保留在仓库里只作为历史参考，不参与课程执行与校验。
需要查看它们的历史改动，使用 `git log --follow <文件路径>`。

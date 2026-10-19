# 机器学习（泰坦尼克号生存预测）

中文课程 · **本课的中文课件是母本** · [English mirror](../english/00-machine-learning/README.md) · [中文总览](../README.zh-CN.md)

经典机器学习入门课。一本 Notebook 走完一个完整项目，与其余课程共用同一个 `~/env_dl_uv` 内核：
数据准备、EDA、预处理、特征工程，六种经典分类器 + XGBoost/LightGBM 对比、GridSearchCV 超参寻优、
pickle/joblib/ONNX 模型保存，直到可复用的 Pipeline 工作流。

- 课件：[`notebooks/01_Titanic-Case.ipynb`](notebooks/01_Titanic-Case.ipynb)，代码单元后紧跟「预期输出」文字块与 `assets/` 图片。
- 数据（不进 Git）：`titanic/LabeledData.csv`（训练 891 行）与 `titanic/UnlabeledData.csv`（测试 418 行），
  即 Kaggle [Titanic](https://www.kaggle.com/c/titanic/data) 赛题文件；缺失时从赛题页下载后放入 `titanic/`。
  英文镜像侧 `english/00-machine-learning/titanic/` 是同两份文件，SHA-256 相同：
  `LabeledData.csv` `4a437fde05fe5264e1701a7387ac6fb75393772ba38bb2c9c566405af5af4bd7`、
  `UnlabeledData.csv` `42c12d055fa9edbcb63a735f6501754dcc3192b95834d2f0b25ca847069e9688`。
- 运行（仓库根目录；notebook 按**模块目录**读写 `titanic/`、`models/`、`result/`，所以必须 `--cwd module`）：

```bash
~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group ml --language zh-CN --cwd module
~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 00-machine-learning
```

- 运行时生成、已被 Git 忽略的产物：`models/` 下的 `.pkl`/`.onnx`、`result/Submission.csv`、
  `Submission_SVM_Pipeline.csv`、`tmp.csv`。
- `assets/reference-*.png` 是正文提到的梯度下降、分类阈值与混淆矩阵交互演示工具的截图，说明见 `assets/README.md`。

## 改课件

**只改这一侧**，然后按序刷新英文镜像（否则 `check_parity.py` 会报单元数不对齐）：

```bash
~/env_dl_uv/.venv/bin/python scripts/build_english_course.py --force   # 中文 -> 英文派生
~/env_dl_uv/.venv/bin/python english/scripts/execute_and_save.py --group ml --cwd module
~/env_dl_uv/.venv/bin/python scripts/embed_expected_outputs.py --module 00-machine-learning
```

新增中文单元或中文注释行时，`scripts/titanic_en.py` 的译文表必须同步补上，否则派生直接报错，
不会留下过期英文。两侧各自的「预期输出」由执行 + 内嵌脚本按语言重新生成。

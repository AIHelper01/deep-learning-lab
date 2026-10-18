# Environment setup

English (default) · [中文课程环境](environment-setup.zh-CN.md)

The default English course has four independent uv projects with committed lockfiles. See the [full English environment guide](../english/docs/environment-setup.md) for versions, alternate platforms, and smoke mode.

From the repository root in PowerShell:

```powershell
.\start-notebooks.ps1                         # English / vision
.\start-notebooks.ps1 -Module pytorch
.\start-notebooks.ps1 -Module paddle
.\start-notebooks.ps1 -Module detection
```

The launcher runs `uv sync --locked` and opens JupyterLab in the selected English module. It falls back to `python -m uv` when uv is not on PATH. First setup requires network access if dependencies are not cached. Select the module's Python kernel.

To inspect the selection without installing packages or starting Jupyter:

```powershell
.\start-notebooks.ps1 -DryRun
.\start-notebooks.ps1 -Language zh-CN -Module pytorch -DryRun
```

For Chinese notebooks, first create the module's `.venv` and install its dependencies using the [Chinese setup guide](environment-setup.zh-CN.md), then launch:

```powershell
.\start-notebooks.ps1 -Language zh-CN -Module vision
```

Chinese sessions start from the notebook directory because their relative data paths require it. For extensions or archived notebooks, start Jupyter from that notebook's directory as described in the Chinese guide. Chinese YOLO26 detection shares the locked English detection environment and official RPS v1 dataset. Launch it with `.\start-notebooks.ps1 -Language zh-CN -Module detection`; outputs remain in the Chinese module. Other Chinese dependencies retain their original validation limitations.

The existing `english/start-notebooks.ps1` remains available and now also defaults to image classification.

The [dataset-format topic](../04-dataset-formats/README.md) reuses this detection environment for its conversion scripts; training does not require conversion.

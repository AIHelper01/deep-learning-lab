# Archived upstream environment

The original vision module shipped its own dependency files. They are preserved byte-for-byte in the Chinese
course at `../../../../01-image-classification/archive/environment/` (`pyproject.toml`, `requirements.txt`,
`uv.lock`) and are deliberately **not** duplicated here.

This course does not use them. The English vision notebooks run on the locked uv project in
`../../pyproject.toml` (see [environment setup](../../../docs/environment-setup.md)), and the Chinese course
keeps the archived files as provenance for the module before it was reorganised.

# Computer vision: from pixels to predictions

An image is a grid of intensities. A color image usually has three channels. PyTorch
image batches have shape `(batch, channels, height, width)`; plotting tools often expect
`(height, width, channels)`. Always inspect shape, range, and dtype before training.

| Task | Question | Output |
|---|---|---|
| Classification | What is in the image? | One or more class labels |
| Detection | What objects are present and where? | Boxes, labels, confidence scores |
| Segmentation | Which pixels belong to each region? | Pixel masks |
| OCR | What text is visible? | Recognized text and often locations |
| Generation | What image matches a condition? | A new image |

Changes in lighting, scale, viewpoint, background, or camera can change model behavior.
Training data should represent the intended use. Split by scene/person/video when nearby
frames would otherwise leak information into validation or test sets.

CNNs use local spatial structure. Residual networks help optimize deeper feature extractors.
Vision Transformers operate on patch tokens. Diffusion models learn a denoising process
for generation. These are different tasks and training objectives, not interchangeable labels.

**Activity:** compare one image-level label with two bounding boxes on an image containing
two hands. Explain what information a classifier cannot provide.


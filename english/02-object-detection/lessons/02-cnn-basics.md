# CNN foundations

A convolution slides learned filters over local input regions. Weight sharing reduces
parameter count and makes the same feature detector available at different locations.
For one spatial axis, the output size is:

`floor((input + 2 * padding - dilation * (kernel - 1) - 1) / stride + 1)`

For a 28-pixel input, kernel 5, padding 2, stride 1, dilation 1, the output is 28 pixels.
A stride-2 pooling layer then reduces that dimension to 14. Check both height and width.

| Component | Purpose | Important distinction |
|---|---|---|
| Convolution | Learn local features | Number of filters determines output channels |
| Pooling | Reduce spatial resolution | Can discard localization detail |
| ReLU | Introduce nonlinearity | Keeps positive values, clips negative values |
| Batch normalization | Normalize intermediate activations | Training and evaluation behavior differ |
| Dropout | Regularize training | Disabled for normal evaluation |
| Residual connection | Add a shortcut around learned layers | Shapes must be compatible |

The receptive field is the input region that can influence an output. More depth and
downsampling enlarge it, but fine localization can suffer. Detection networks combine
features at multiple scales to handle both small and large objects.

**Exercise:** trace the shapes in the LeNet notebook. Explain why a three-channel CIFAR-10
image cannot be passed directly to a network expecting a one-channel MNIST image.


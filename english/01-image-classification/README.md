# Image classification

1. [LeNet on MNIST](notebooks/01-lenet-mnist.ipynb)
2. [LeNet on CIFAR-10](notebooks/02-lenet-cifar10.ipynb)
3. [ResNet18 on CIFAR-10](notebooks/03-resnet-cifar10.ipynb)
4. [Custom image folders](notebooks/extensions/04-lenet-custom-data.ipynb)

[Compact MNIST comparison](archive/01-lenet-mnist-copy1.ipynb) is optional.

Each main experiment covers data inspection, model definition, training, checkpoint
selection, evaluation, and inference. The custom-folder experiment also writes CSV indexes.
Outputs are separated by experiment name. Use validation data for model selection; hold
test data back for final evaluation. The default short runs prioritize teaching flow.

[Environment setup](../docs/environment-setup.md) · [Data and provenance](../docs/datasets.md)


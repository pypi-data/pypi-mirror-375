# Wavelet Neural Networks

> [![PyPI - Version](https://img.shields.io/pypi/v/waveletnn?style=flat)](https://pypi.org/project/waveletnn/)
[![GitHub License](https://img.shields.io/github/license/Scurrra/WaveletNN-PyTorch?style=flat)](https://github.com/Scurrra/WaveletNN-PyTorch/tree/master?tab=MIT-1-ov-file)


> `pip install waveletnn`

Package provides the implementation of orthonormal and biorthogonal wavelet transforms via convolutions. Batch multi-channel one- and -two-dimensional data is supported. For analysis kernels of even length are supported, while for inverse transform (synthesis) kernels are required to have length `4k + 2`. The blocks are:

- `OrthonormalWaveletBlock1D`
- `OrthonormalWaveletBlock2D`
- `BiorthogonalWaveletBlock1D`
- `BiorthogonalWaveletBlock2D`
- `InverseWaveletBlock1D`
- `InverseWaveletBlock2D`

Package provides loss functions for wavelet's kernels regularizations to preserve features of both orthonormal (`OrthonormalWaveletRegularization`) and biorthogonal (`BiorthogonalWaveletRegularization`) wavelets while training. The features are admissibility (sum of coeffs), orthogonality and regularity. For more info on training see [notebooks directory](notebooks/).

The package can use wavelets from the [PyWavelets](https://pywavelets.readthedocs.io/) library. If the library is not yet installed use `pip install waveletnn[pywt]` for full installation. The wavelet blocks can be constructed by providing the name of the wavelet to be used (see [pywt.wavelist()](https://pywavelets.readthedocs.io/en/latest/ref/wavelets.html#built-in-wavelets-wavelist)) or by manually providing scaling filter for orthonormal blocks and scaling and wavelet analysis filters for biorthogonal wavelets. Note, that results of transform blocks are different from the results of the `pywt` functions: the approximation from each level is half its input no matter what signal extension mode is used. 

The signal extension (padding) is performed via separate module `PadSequence`. Extension modes are: 
- "constant" -- ```... v  v | x1 x2 ... xn | v  v ...```, with default `v = 0` (same as in `torch`, default behavior corresponds to "zero" padding in `pywt`)
- "circular" -- ```... xn-1 xn | x1 x2 ... xn | x1 x2 ...``` (same as in `torch`, corresponds to "periodic" padding in `pywt`)
- "replicate" -- ```... x1 x1 | x1 x2 ... xn | xn xn ...``` (same as in `torch`, corresponds to "constant" padding in `pywt`)
- "reflect" -- ```... x3 x2 | x1 x2 ... xn | xn-1 xn-2 ...``` (same as in `torch` and `pywt`)
- "antireflect" -- ```... (2*x1 - x3) (2*x1 - x2) | x1 x2 ... xn | (2*xn - xn-1) (2*xn - xn-2) ...``` (same as in `pywt`, not present in `torch`)

For examples on usage see [notebooks directory](notebooks/).
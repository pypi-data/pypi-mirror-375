import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F

try:
    import pywt
except ImportError:
    _has_pywt = False
else:
    _has_pywt = True

from waveletnn import PadSequence


class OrthonormalWaveletBlock1D(nn.Module):
    """Block for one-dimensional ortonormal discrete wavelet transform.

    Kernel size is required to have even size.

    Args:
        kernel_size (int): Length of kernels
        levels (int, default=1): Number of transform levels
        padding_mode (str, default="antireflect"): The padding scheme, "constant", "circular", "replicate", "reflect" or "antireflect"
        scaling_kernel (torch.Tensor, default=None): Scaling filter, if None created with torch.nn.init.kaiming_uniform_(a=np.sqrt(5))
        wavelet (str, default=None): Wavelet name, available in PyWavelets library (waveletnn[pywt]); shadows scaling_kernel if specified
        normalize_approximation (bool, default=False): Whether to normalize aproximation by sum of caling coefficients
    """

    def __init__(
        self,
        kernel_size: int,
        levels: int = 1,
        padding_mode: str = "antireflect",
        scaling_kernel=None,
        wavelet: str = None,
        normalize_approximation: bool = False,
    ):
        assert (kernel_size - 2) % 2 == 0, "Kernel size should be even"
        if (kernel_size - 2) % 4 != 0:
            print("Transform is not invertible by `InverseWaveletBlock1D`")

        super(OrthonormalWaveletBlock1D, self).__init__()

        self.levels = levels
        self.kernel_size = kernel_size
        self.padding = (kernel_size - 2) // 2
        self.padding_mode = padding_mode
        self.pad = PadSequence(self.padding, self.padding, padding_mode)
        self.normalize_approximation = normalize_approximation

        if wavelet is not None:
            assert _has_pywt, (
                "Specifying wavelet name is only supported with PyWavelets installed (waveletnn[pywt])"
            )
            assert wavelet in pywt.wavelist(), (
                f"Unkhown wavelet `{wavelet}`, known wavlets are {pywt.wavelist()}"
            )
            wavelet = pywt.Wavelet(wavelet)
            assert wavelet.orthogonal, "Provided wavelet is not orthonormal"
            scaling_kernel = wavelet.dec_lo

        if scaling_kernel is not None:
            scaling_kernel = torch.as_tensor(scaling_kernel)
            if scaling_kernel.dim() == 1:
                scaling_kernel = scaling_kernel.reshape(1, 1, -1)
            elif scaling_kernel.dim() != 3:
                raise Exception("Scaling kernel should have 1 or 3 dimensions")
            elif scaling_kernel.shape[0] != 1 or scaling_kernel.shape[1] != 1:
                raise Exception(
                    "First two dimensions of 3d scaling filter are placeholders and both should be equal to 1"
                )
            assert scaling_kernel.shape[-1] == kernel_size, (
                "Length of provided kernel should be equal to kernel_size."
            )

            self.scaling_kernel = nn.Parameter(scaling_kernel)
        else:
            self.scaling_kernel = nn.Parameter(torch.empty(1, 1, kernel_size))
            # just like in pytorch https://github.com/pytorch/pytorch/blob/v2.6.0/torch/nn/modules/conv.py#L182
            nn.init.kaiming_uniform_(self.scaling_kernel, a=np.sqrt(5))

        # helper parameter for computing wavelet filter
        self.r = nn.Parameter(
            torch.arange(kernel_size, dtype=torch.get_default_dtype()),
            requires_grad=False,
        )

    def forward(self, signal, return_filters: bool = False):
        """Foward pass of OrthonormalWaveletBlock1D.

        Args:
            signal (torch.Tensor): Signal to be analyzed
            return_filters (bool, default=False): Whether scaling and wavelet filters should be returned, useful for reqularization

        Output:
            (signals, details) (Tuple[List[torch.Tensor], List[torch.Tensor]]): approximation and details on each of self.levels
            (h, g) (Tuple[List[torch.Tensor], List[torch.Tensor]]): scaling and wavelet filters if the return_filters flag is on
        """

        assert signal.dim() == 3
        b, c, _ = signal.shape

        h = self.scaling_kernel
        g = torch.flip(h, (2,)) * (-1) ** self.r

        H = h.repeat(c, 1, 1)
        G = g.repeat(c, 1, 1)

        signals, details = [], []

        for _ in range(self.levels):
            signal = self.pad(signal)

            signals.append(
                F.conv1d(signal, H, stride=2, groups=c)
                / (h.sum() if self.normalize_approximation else 1)
            )
            details.append(F.conv1d(signal, G, stride=2, groups=c))

            signal = signals[-1].detach()

        if return_filters:
            return (signals, details), (h.reshape(-1), g.reshape(-1))
        return (signals, details)


class OrthonormalWaveletBlock2D(nn.Module):
    """Block for two-dimensional ortonormal discrete wavelet transform.

    Kernel size is required to have even size.

    Args:
        kernel_size (int): Length of kernels
        levels (int, default=1): Number of transform levels
        padding_mode (str, default="antireflect"): The padding scheme, "constant", "circular", "replicate", "reflect" or "antireflect"
        scaling_kernel (torch.Tensor, default=None): Scaling filter, if None created with torch.nn.init.kaiming_uniform_(a=np.sqrt(5))
        wavelet (str, default=None): Wavelet name, available in PyWavelets library (waveletnn[pywt]); shadows scaling_kernel if specified
        normalize_approximation (bool, default=False): Whether to normalize aproximation by sum of caling coefficients
    """

    def __init__(
        self,
        kernel_size: int,
        levels: int = 1,
        padding_mode: str = "antireflect",
        scaling_kernel=None,
        wavelet: str = None,
        normalize_approximation: bool = False,
    ):
        assert (kernel_size - 2) % 2 == 0, "Kernel size should be even"
        if (kernel_size - 2) % 4 != 0:
            print("Transform is not invertible by `InverseWaveletBlock2D`")

        super(OrthonormalWaveletBlock2D, self).__init__()

        self.levels = levels
        self.kernel_size = kernel_size
        self.padding = (kernel_size - 2) // 2
        self.padding_mode = padding_mode
        self.pad = PadSequence(self.padding, self.padding, self.padding_mode)
        self.normalize_approximation = normalize_approximation

        if wavelet is not None:
            assert _has_pywt, (
                "Specifying wavelet name is only supported with PyWavelets installed (waveletnn[pywt])"
            )
            assert wavelet in pywt.wavelist(), (
                f"Unkhown wavelet `{wavelet}`, known wavlets are {pywt.wavelist()}"
            )
            wavelet = pywt.Wavelet(wavelet)
            assert wavelet.orthogonal, "Provided wavelet is not orthonormal"
            scaling_kernel = wavelet.dec_lo

        if scaling_kernel is not None:
            scaling_kernel = torch.as_tensor(scaling_kernel)
            if scaling_kernel.dim() == 1:
                scaling_kernel = scaling_kernel.reshape(1, 1, -1)
            elif scaling_kernel.dim() != 3:
                raise Exception("Scaling kernel should have 1 or 3 dimensions")
            elif scaling_kernel.shape[0] != 1 or scaling_kernel.shape[1] != 1:
                raise Exception(
                    "First two dimensions of 3d scaling filter are placeholders and both should be equal to 1"
                )
            assert scaling_kernel.shape[-1] == kernel_size, (
                "Length of provided kernel should be equal to kernel_size."
            )

            self.scaling_kernel = nn.Parameter(scaling_kernel)
        else:
            self.scaling_kernel = nn.Parameter(torch.empty(1, 1, kernel_size))
            # just like in pytorch https://github.com/pytorch/pytorch/blob/v2.6.0/torch/nn/modules/conv.py#L182
            nn.init.kaiming_uniform_(self.scaling_kernel, a=np.sqrt(5))

        # helper parameter for computing wavelet filter
        self.r = nn.Parameter(
            torch.arange(kernel_size, dtype=torch.get_default_dtype()),
            requires_grad=False,
        )

    def forward(self, signal, return_filters: bool = False):
        """Foward pass of OrthonormalWaveletBlock2D.

        Args:
            signal (torch.Tensor): Signal to be analyzed
            return_filters (bool, default=False): Whether scaling and wavelet filters should be returned, useful for reqularization

        Output:
            (ss, sd, ds, dd) (Tuple[List[torch.Tensor], List[torch.Tensor], List[torch.Tensor], List[torch.Tensor]]): approximation and details on each of self.levels
            (h, g) (Tuple[List[torch.Tensor], List[torch.Tensor]]): scaling and wavelet filters if the return_filters flag is on
        """

        assert signal.dim() == 4
        b, c, _, _ = signal.shape

        h = self.scaling_kernel
        g = torch.flip(h, (2,)) * (-1) ** self.r

        H = h.repeat(c, 1, 1, 1)
        G = g.repeat(c, 1, 1, 1)

        ss, sd, ds, dd = [], [], [], []

        for _ in range(self.levels):
            signal = self.pad(signal)

            s = self.pad(F.conv2d(signal, H, stride=(1, 2), groups=c).mT) / (
                h.sum() if self.normalize_approximation else 1
            )
            d = self.pad(F.conv2d(signal, G, stride=(1, 2), groups=c).mT)

            ss.append(
                F.conv2d(s, H, stride=(1, 2), groups=c).mT
                / (h.sum() if self.normalize_approximation else 1)
            )
            sd.append(F.conv2d(s, G, stride=(1, 2), groups=c).mT)
            ds.append(
                F.conv2d(d, H, stride=(1, 2), groups=c).mT
                / (h.sum() if self.normalize_approximation else 1)
            )
            dd.append(F.conv2d(d, G, stride=(1, 2), groups=c).mT)

            signal = ss[-1].detach()

        if return_filters:
            return (ss, sd, ds, dd), (h.reshape(-1), g.reshape(-1))
        return (ss, sd, ds, dd)

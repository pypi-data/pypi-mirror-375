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


class InverseWaveletBlock1D(nn.Module):
    """Block for one-dimensional inverse discrete wavelet transform.

    Kernel size is required to have size `4k + 2`. Kernels can be provided on module init or on inference.

    Args:
        kernel_size (int): Length of kernels
        levels (int, default=1): Number of transform levels
        padding_mode (str, default="antireflect"): The padding scheme, "constant", "circular", "replicate", "reflect" or "antireflect"
        static_filters (bool, default=True): Whether kernels are provided on init
        scaling_kernel (torch.Tensor, default=None): Scaling filter
        wavelet_kernel (torch.Tensor, default=None): Wavelet filter
        wavelet (str, default=None): Wavelet name, available in PyWavelets library (waveletnn[pywt]); shadows h and g if specified
        normalize_approximation (bool, default=False): Whether the aproximation was normalized by sum of caling coefficients
    """

    def __init__(
        self,
        kernel_size: int,
        levels: int = 1,
        padding_mode: str = "antireflect",
        static_filters: bool = True,
        scaling_kernel=None,
        wavelet_kernel=None,
        wavelet: str = None,
        normalize_approximation: bool = False,
    ):
        assert (kernel_size - 2) % 4 == 0
        super(InverseWaveletBlock1D, self).__init__()

        self.levels = levels
        self.kernel_size = kernel_size
        self.padding = (kernel_size - 2) // 4
        self.padding_mode = padding_mode
        self.pad = PadSequence(self.padding, self.padding, padding_mode)
        self.normalize_approximation = normalize_approximation

        if static_filters:
            if wavelet is not None:
                assert _has_pywt, (
                    "Specifying wavelet name is only supported with PyWavelets installed (waveletnn[pywt])"
                )
                assert wavelet in pywt.wavelist(), (
                    f"Unkhown wavelet `{wavelet}`, known wavlets are {pywt.wavelist()}"
                )
                wavelet = pywt.Wavelet(wavelet)
                # for some reason reconstruction filters in PyWavelets are flipped
                scaling_kernel = wavelet.rec_lo[::-1]
                wavelet_kernel = wavelet.rec_hi[::-1]

            assert scaling_kernel is not None and wavelet_kernel is not None, (
                "`scaling_kernel` and `wavelet_kernel` must be specified"
            )

            scaling_kernel = torch.as_tensor(scaling_kernel)
            wavelet_kernel = torch.as_tensor(wavelet_kernel)

            assert scaling_kernel.dim() == 1 and wavelet_kernel.dim() == 1
            assert (
                scaling_kernel.shape[0] == self.kernel_size
                and wavelet_kernel.shape[0] == self.kernel_size
            )

            scaling_kernel = torch.flip(
                scaling_kernel.reshape(-1, 2).permute(1, 0), (1,)
            ).unsqueeze(1)

            wavelet_kernel = torch.flip(
                wavelet_kernel.reshape(-1, 2).permute(1, 0), (1,)
            ).unsqueeze(1)

        self.scaling_kernel = nn.Parameter(scaling_kernel, requires_grad=False)
        self.wavelet_kernel = nn.Parameter(wavelet_kernel, requires_grad=False)
        self.static_filters = static_filters

    def forward(self, signal, details, h=None, g=None, wavelet: str = None):
        """Forward pass of InverseWaveletBlock1D.

        Args:
            signal (torch.Tensor): The last approximation
            details (List[torch.Tensor]): The list of details on different levels, len(details) == self.levels
            h (torch.Tensor, default=None): Scaling filter if self.static_filters == False
            g (torch.Tensor, default=None): Wavelet filter if self.static_filters == False
            wavelet (str, default=None): Wavelet name, available in PyWavelets library (waveletnn[pywt]); shadows h and g if specified

        Output:
            torch.Tensor: reconstructed signal
        """

        if isinstance(signal, list):
            signal = signal[-1]
        assert signal.dim() == 3
        b, c, _ = signal.shape

        if self.static_filters:
            h = self.scaling_kernel
            g = self.wavelet_kernel
        else:
            if wavelet is not None:
                assert _has_pywt, (
                    "Specifying wavelet name is only supported with PyWavelets installed (waveletnn[pywt])"
                )
                assert wavelet in pywt.wavelist(), (
                    f"Unkhown wavelet `{wavelet}`, known wavlets are {pywt.wavelist()}"
                )
                wavelet = pywt.Wavelet(wavelet)
                # for some reason reconstruction filters in PyWavelets are flipped
                h = wavelet.rec_lo[::-1]
                g = wavelet.rec_hi[::-1]

            assert h is not None and g is not None, "`h` and `g` must be specified"

            h = torch.as_tensor(h, device=self.scaling_kernel.device)
            g = torch.as_tensor(g, device=self.wavelet_kernel.device)

            assert h.dim() == 1 and g.dim() == 1
            assert h.shape[0] == self.kernel_size and g.shape[0] == self.kernel_size

            h = torch.flip(h.reshape(-1, 2).permute(1, 0), (1,)).unsqueeze(1)
            g = torch.flip(g.reshape(-1, 2).permute(1, 0), (1,)).unsqueeze(1)

        for i in range(self.levels - 1, -1, -1):
            # pad signal and details
            signal = self.pad(signal.reshape(b * c, 1, -1)) * (
                h.sum() if self.normalize_approximation else 1
            )
            detail = self.pad(details[i].reshape(b * c, 1, -1))
            # convolve and riffle
            signal = (
                F.conv1d(signal, h, stride=1).permute(0, 2, 1).reshape(b * c, 1, -1)
            )
            detail = (
                F.conv1d(detail, g, stride=1).permute(0, 2, 1).reshape(b * c, 1, -1)
            )
            # add up
            signal = torch.add(signal, detail).reshape(b, c, -1)

        return signal


class InverseWaveletBlock2D(nn.Module):
    """Block for two-dimensional inverse discrete wavelet transform.

    Kernel size is required to have size `4k + 2`. Kernels can be provided on module init or on inference.

    Args:
        kernel_size (int): Length of kernels
        levels (int, default=1): Number of transform levels
        padding_mode (str, default="antireflect"): The padding scheme, "constant", "circular", "replicate", "reflect" or "antireflect"
        static_filters (bool, default=True): Whether kernels are provided on init
        scaling_kernel (torch.Tensor, default=None): Scaling filter
        wavelet_kernel (torch.Tensor, default=None): Wavelet filter
        wavelet (str, default=None): Wavelet name, available in PyWavelets library (waveletnn[pywt]); shadows h and g if specified
        normalize_approximation (bool, default=False): Whether the aproximation was normalized by sum of caling coefficients
    """

    def __init__(
        self,
        kernel_size: int,
        levels: int = 1,
        padding_mode: str = "antireflect",
        static_filters: bool = True,
        scaling_kernel=None,
        wavelet_kernel=None,
        wavelet: str = None,
        normalize_approximation: bool = False,
    ):
        assert (kernel_size - 2) % 4 == 0
        super(InverseWaveletBlock2D, self).__init__()

        self.levels = levels
        self.kernel_size = kernel_size
        self.padding = (kernel_size - 2) // 4
        self.padding_mode = padding_mode
        self.pad = PadSequence(self.padding, self.padding, padding_mode)
        self.normalize_approximation = normalize_approximation

        if static_filters:
            if wavelet is not None:
                assert _has_pywt, (
                    "Specifying wavelet name is only supported with PyWavelets installed (waveletnn[pywt])"
                )
                assert wavelet in pywt.wavelist(), (
                    f"Unkhown wavelet `{wavelet}`, known wavlets are {pywt.wavelist()}"
                )
                wavelet = pywt.Wavelet(wavelet)
                # for some reason reconstruction filters in PyWavelets are flipped
                scaling_kernel = wavelet.rec_lo[::-1]
                wavelet_kernel = wavelet.rec_hi[::-1]

            assert scaling_kernel is not None and wavelet_kernel is not None, (
                "`scaling_kernel` and `wavelet_kernel` must be specified"
            )

            scaling_kernel = torch.as_tensor(scaling_kernel)
            wavelet_kernel = torch.as_tensor(wavelet_kernel)

            assert scaling_kernel.dim() == 1 and wavelet_kernel.dim() == 1
            assert (
                scaling_kernel.shape[0] == self.kernel_size
                and wavelet_kernel.shape[0] == self.kernel_size
            )

            scaling_kernel = (
                torch.flip(scaling_kernel.reshape(-1, 2).permute(1, 0), (1,))
                .unsqueeze(1)
                .unsqueeze(1)
            )

            wavelet_kernel = (
                torch.flip(wavelet_kernel.reshape(-1, 2).permute(1, 0), (1,))
                .unsqueeze(1)
                .unsqueeze(1)
            )

        self.scaling_kernel = nn.Parameter(scaling_kernel, requires_grad=False)
        self.wavelet_kernel = nn.Parameter(wavelet_kernel, requires_grad=False)
        self.static_filters = static_filters

    def forward(self, ss, sd, ds, dd, h=None, g=None, wavelet: str = None):
        """Forward pass of InverseWaveletBlock2D.

        Args:
            ss (torch.Tensor): The last approximation
            sd, ds, dd (List[torch.Tensor]): The list of details on different levels, len(sd) == len(ds) == len(dd) == self.levels
            h (torch.Tensor, default=None): Scaling filter if self.static_filters == False
            g (torch.Tensor, default=None): Wavelet filter if self.static_filters == False
            wavelet (str, default=None): Wavelet name, available in PyWavelets library (waveletnn[pywt]); shadows h and g if specified

        Output:
            torch.Tensor: reconstructed signal
        """

        if isinstance(ss, list):
            ss = ss[-1]
        assert ss.dim() == 4
        b, c, _, _ = ss.shape

        if self.static_filters:
            h = self.scaling_kernel
            g = self.wavelet_kernel
        else:
            if wavelet is not None:
                assert _has_pywt, (
                    "Specifying wavelet name is only supported with PyWavelets installed (waveletnn[pywt])"
                )
                assert wavelet in pywt.wavelist(), (
                    f"Unkhown wavelet `{wavelet}`, known wavlets are {pywt.wavelist()}"
                )
                wavelet = pywt.Wavelet(wavelet)
                # for some reason reconstruction filters in PyWavelets are flipped
                h = wavelet.rec_lo[::-1]
                g = wavelet.rec_hi[::-1]

            assert h is not None and g is not None, "`h` and `g` must be specified"

            h = torch.as_tensor(h, device=self.scaling_kernel.device)
            g = torch.as_tensor(g, device=self.wavelet_kernel.device)

            assert h.dim() == 1 and g.dim() == 1
            assert h.shape[0] == self.kernel_size and g.shape[0] == self.kernel_size

            h = (
                torch.flip(h.reshape(-1, 2).permute(1, 0), (1,))
                .unsqueeze(1)
                .unsqueeze(1)
            )

            g = (
                torch.flip(g.reshape(-1, 2).permute(1, 0), (1,))
                .unsqueeze(1)
                .unsqueeze(1)
            )

        for i in range(self.levels - 1, -1, -1):
            # compute convolution kernels for channel processing
            H = h.repeat(ss.shape[2], 1, 1, 1)
            G = g.repeat(ss.shape[2], 1, 1, 1)

            # synthesize approximation
            signal = self.pad(
                ss.reshape(b * c, ss.shape[2], ss.shape[3]).mT.unsqueeze(2)
            ) * (h.sum() if self.normalize_approximation else 1)
            detail = self.pad(
                sd[i].reshape(b * c, ss.shape[2], ss.shape[3]).mT.unsqueeze(2)
            )
            s = (
                torch.add(
                    F.conv2d(signal, H, stride=1, groups=signal.shape[1])
                    .reshape(b * c, signal.shape[1], 2, -1)
                    .permute(0, 1, 3, 2)
                    .reshape(b * c, signal.shape[1], 1, -1),
                    F.conv2d(detail, G, stride=1, groups=detail.shape[1])
                    .reshape(b * c, detail.shape[1], 2, -1)
                    .permute(0, 1, 3, 2)
                    .reshape(b * c, detail.shape[1], 1, -1),
                )
                .permute(0, 2, 1, 3)
                .mT.permute(0, 2, 1, 3)
            ) * (h.sum() if self.normalize_approximation else 1)

            # synthesise details
            signal = self.pad(
                ds[i].reshape(b * c, ss.shape[2], ss.shape[3]).mT.unsqueeze(2)
            ) * (h.sum() if self.normalize_approximation else 1)
            detail = self.pad(
                dd[i].reshape(b * c, ss.shape[2], ss.shape[3]).mT.unsqueeze(2)
            )
            d = (
                torch.add(
                    F.conv2d(signal, H, stride=1, groups=signal.shape[1])
                    .reshape(b * c, signal.shape[1], 2, -1)
                    .permute(0, 1, 3, 2)
                    .reshape(b * c, signal.shape[1], 1, -1),
                    F.conv2d(detail, G, stride=1, groups=detail.shape[1])
                    .reshape(b * c, detail.shape[1], 2, -1)
                    .permute(0, 1, 3, 2)
                    .reshape(b * c, detail.shape[1], 1, -1),
                )
                .permute(0, 2, 1, 3)
                .mT.permute(0, 2, 1, 3)
            )

            # compute convolution kernels for channel processing
            H = h.repeat(s.shape[1], 1, 1, 1)
            G = g.repeat(s.shape[1], 1, 1, 1)

            # synthesize signal
            ss = torch.add(
                F.conv2d(self.pad(s), H, stride=1, groups=s.shape[1])
                .reshape(b * c, s.shape[1], 2, -1)
                .permute(0, 1, 3, 2)
                .reshape(b * c, s.shape[1], 1, -1),
                F.conv2d(self.pad(d), G, stride=1, groups=d.shape[1])
                .reshape(b * c, d.shape[1], 2, -1)
                .permute(0, 1, 3, 2)
                .reshape(b * c, d.shape[1], 1, -1),
            ).permute(0, 2, 1, 3)
            ss = ss.reshape(b, c, *ss.shape[2:])

        return ss

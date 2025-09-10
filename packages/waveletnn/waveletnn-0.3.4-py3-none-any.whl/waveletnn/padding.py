import torch
import torch.nn as nn
import torch.nn.functional as F


class PadSequence(nn.Module):
    r"""Pads the input tensor :func:`torch.nn.functional.pad()`.

    Args:
        padding_left, padding_right: the size of the padding.
        mode: one of padding modes "constant", "circular", "replicate", "reflect", "antireflect"

    Shape:
        - Input: :math:`(H, 1, W_{in})` or :math:`(N, H, 1, W_{in})`.
        - Output: :math:`(H, 1, W_{out})` or :math:`(N, H, 1, W_{out})`, where

          :math:`W_{out} = W_{in} + \text{padding\_left} + \text{padding\_right}`
    """

    def __init__(self, pad_left, pad_right, mode: str, value=0):
        assert mode in ["constant", "circular", "replicate", "reflect", "antireflect"]

        super(PadSequence, self).__init__()
        self.padding = (pad_left, pad_right, 0, 0)
        self.mode = mode
        self.value = value

    def forward(self, X):
        d = X.dim()
        assert d == 4 or d == 3
        if d == 3:
            X = torch.unsqueeze(X, 0)

        # we have only one non-deault mode -- "antireflect"
        # but if we want more...
        match self.mode:
            case "constant":
                # ```... 0  0 | x1 x2 ... xn | 0  0 ...```
                Y = F.pad(X, self.padding, "constant", self.value)
            case "circular":
                # ```... xn-1 xn | x1 x2 ... xn | x1 x2 ...```
                Y = F.pad(X, self.padding, "circular")
            case "replicate":
                # ```... x1 x1 | x1 x2 ... xn | xn xn ...```
                Y = F.pad(X, self.padding, "replicate")
            case "reflect":
                # ```... x3 x2 | x1 x2 ... xn | xn-1 xn-2 ...```
                Y = F.pad(X, self.padding, "reflect")
            case "antireflect":
                # ```... (2*x1 - x3) (2*x1 - x2) | x1 x2 ... xn | (2*xn - xn-1) (2*xn - xn-2) ...```
                l, r, _, _ = self.padding
                Y = F.pad(X, self.padding, "reflect")
                Y[..., :l] = torch.sub(2 * Y[..., l : l + 1], Y[..., :l])
                Y[..., -r:] = torch.sub(2 * Y[..., -r - 1 : -r], Y[..., -r:])

        return Y if d == 4 else torch.squeeze(Y, 0)

import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F


class OrthonormalWaveletRegularization(nn.Module):
    r"""Regularization for Orthonormal Wavelets, i.e. loss to make convolution weights be wavelet coeffs.

    The loss consists of three main terms, i.e. conditions of wavelets:
     - Admissibility, or discrete normalization
     - Orthogonality
     - Regularity, or vanishing moments

    All the terms of final sum is squared to set the lower bound of loss (needed for minimization task).
    """

    def __init__(
        self,
        pNorm=lambda p: np.sqrt(2) / (2**p),
        n_moments=lambda g: len(g) // 2 + 1,
        lambdas: tuple[float, float, float] = (1.0, 1.0, 1.0),
    ):
        assert len(lambdas) == 3
        super(OrthonormalWaveletRegularization, self).__init__()
        self.pNorm = pNorm
        self.n_moments = n_moments
        self.lambdas = lambdas

    def forward(self, h, g):
        r = torch.arange(len(g), dtype=torch.get_default_dtype(), device=g.device)

        # sum of scaling function coeffs is equal to square root of two
        l1 = (h.sum() - np.sqrt(2)) ** 2
        # sum of wavelet coeffs is equal to zero
        l2 = g.sum() ** 2

        # orthogonality
        ## sum of squares equals to one
        l3 = (torch.dot(h, h) - 1.0) ** 2
        ## otherwise zero
        l4 = sum(
            torch.dot(h[(2 * k) :], h[: (len(h) - 2 * k)]) ** 2
            for k in range(1, (len(h) - 1) // 2 + 1)
        )

        # vanishing moments up to N // 2
        ### pNorm is a constant muliplier of the constraint's lhs valished by zero on the rhs
        l5 = sum(
            (torch.dot(r ** (p - 1), g) * self.pNorm(p)) ** 2
            for p in range(1, self.n_moments(g))
        )

        return (
            self.lambdas[0] * (l1 + l2)
            + self.lambdas[1] * (l3 + l4)
            + self.lambdas[2] * l5
        )


class BiorthogonalWaveletRegularization(nn.Module):
    r"""Regularization for Biorthogonal Wavelets, i.e. loss to make convolution weights be wavelet coeffs.

    The loss consists of three main terms, i.e. conditions of wavelets:
     - Admissibility, or discrete normalization
     - Orthogonality of scalar function and it's dual
     - Regularity of dual scaing function, or vanishing moments

    All the terms of final sum is squared to set the lower bound of loss (needed for minimization task).
    """

    def __init__(
        self,
        pNorm=lambda p: np.sqrt(2) / (2**p),
        n_moments=lambda g: len(g) // 2 + 1,
        n_moments_dual=None,
        lambdas: tuple[float, float, float] = (1.0, 1.0, 1.0),
    ):
        assert len(lambdas) == 3
        super(BiorthogonalWaveletRegularization, self).__init__()
        self.pNorm = pNorm
        self.n_moments = n_moments
        if n_moments_dual is None:
            self.n_moments_dual = n_moments
        else:
            self.n_moments_dual = n_moments_dual
        self.lambdas = lambdas

    def forward(self, h, g):
        r = torch.arange(len(g[0]), dtype=torch.get_default_dtype(), device=g[0].device)

        # sum of scaling function coeffs is equal to square root of two
        l1 = (h[0].sum() - np.sqrt(2)) ** 2 + (h[1].sum() - np.sqrt(2)) ** 2
        # sum of wavelet coeffs is equal to zero
        l2 = g[0].sum() ** 2 + g[1].sum() ** 2

        # orthogonality
        ## scalar muliplication of analysis and synthesis scalar function's coefs equals to one
        l3 = (torch.dot(h[0], h[1]) - 1.0) ** 2
        ## otherwise zero
        l4 = sum(
            torch.dot(h[0][(2 * k) :], h[1][: (len(h) - 2 * k)]) ** 2
            for k in range(1, (len(h) - 1) // 2 + 1)
        )

        # vanishing moments up to N // 2
        ### pNorm is a constant muliplier of the constraint's lhs valished by zero on the rhs
        l5 = sum(
            (torch.dot(r ** (p - 1), g[0]) * self.pNorm(p)) ** 2
            for p in range(1, self.n_moments(g[0]))
        )
        l6 = sum(
            (torch.dot(r ** (p - 1), g[1]) * self.pNorm(p)) ** 2
            for p in range(1, self.n_moments_dual(g[1]))
        )

        return (
            self.lambdas[0] * (l1 + l2)
            + self.lambdas[1] * (l3 + l4)
            + self.lambdas[2] * (l5 + l6)
        )

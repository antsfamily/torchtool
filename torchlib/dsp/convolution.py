#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-11-07 17:00:48
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$

import numpy as np
import torch as th
from torchlib.base.mathops import nextpow2, ebemulcc
from torchlib.dsp.ffts import padfft, fft, ifft
from torchlib.base.arrayops import cut


def cutfftconv1(y, nfft, Nx, Nh, shape='same', axis=0, ftshift=False):
    r"""Throwaway boundary elements to get convolution results.

    Throwaway boundary elements to get convolution results.

    Parameters
    ----------
    y : {numpy.ndarray}
        array after ``iff``.
    nfft : {number}
        number of fft points.
    Nx : {number}
        signal length
    Nh : {number}
        filter length
    shape : {str}
        output shape:
        1. ``'same' --> same size as input x``, :math:`N_x`
        2. ``'valid' --> valid convolution output``
        3. ``'full' --> full convolution output``, :math:`N_x+N_h-1`
        (the default is 'same')
    axis : {number}
        convolution axis (the default is 0)
    ftshift : {[type]}
        whether to shift the frequencies (the default is False)

    Returns
    -------
    y : {numpy.ndarray}
        array with shape specified by :attr:`same`.
    """

    nfft, Nx, Nh = np.int32([nfft, Nx, Nh])
    N = Nx + Nh - 1
    Nextra = nfft - N

    if nfft < N:
        raise ValueError("~~~To get right results, nfft must be larger than Nx+Nh-1!")

    if ftshift:
        if np.mod(Nx, 2) > 0 and np.mod(Nh, 2) > 0:
            if Nextra > 0:
                Nhead = np.int32(np.fix((Nextra + 1) / 2.))
                Ntail = Nextra - Nhead
                y = cut(y, ((Nhead, np.int32(nfft - Ntail)),), axis=axis)
            else:
                y = cut(y, ((N - 1, N), (0, N - 1)), axis)
        else:
            Nhead = np.int32(np.fix(Nextra / 2.))
            Ntail = Nextra - Nhead
            y = cut(y, ((Nhead, np.int32(nfft - Ntail)),), axis=axis)
    else:
        Nhead = 0
        Ntail = Nextra
        y = cut(y, ((Nhead, np.int32(nfft - Ntail)),), axis=axis)

    if shape in ['same', 'SAME', 'Same']:
        Nstart = np.fix(Nh / 2.)
        Nend = Nstart + Nx
    elif shape in ['valid', 'VALID', 'Valid']:
        Nstart = Nh - 1
        Nend = N - (Nh - 1)
    elif shape in ['full', 'FULL', 'Full']:
        Nstart, Nend = (0, N)
    Nstart, Nend = np.int32([Nstart, Nend])
    y = cut(y, ((Nstart, Nend),), axis=axis)
    return y


def fftconv1(x, h, axis=0, nfft=None, shape='same', ftshift=False, eps=None):
    """Convolution using Fast Fourier Transformation

    Convolution using Fast Fourier Transformation.

    Parameters
    ----------
    x : {numpy.ndarray}
        data to be convolved.
    h : {numpy.ndarray}
        filter array
    shape : {str}, optional
        output shape:
        1. ``'same' --> same size as input x``, :math:`N_x`
        2. ``'valid' --> valid convolution output``
        3. ``'full' --> full convolution output``, :math:`N_x+N_h-1`
        (the default is 'same')
    axis : {number}, optional
        convolution axis (the default is 0)
    nfft : {number}, optional
        number of fft points (the default is :math:`2^nextpow2(N_x+N_h-1)`),
        note that :attr:`nfft` can not be smaller than :math:`N_x+N_h-1`.
    ftshift : {bool}, optional
        whether shift frequencies (the default is False)
    eps : {None or float}, optional
        x[abs(x)<eps] = 0 (the default is None, does nothing)

    Returns
    -------
    y : {numpy.ndarray}
        Convolution result array.

    """

    if h.size(-1) != 2 or x.size(-1) != 2:
        raise TypeError('Last dim must have size 2!')

    dh, dx = h.dim(), x.dim()
    if dh != dx:
        size = [1] * dx
        size[-1] = 2
        size[axis] = int(h.numel() / 2.)
        h = h.reshape(size)

    Nh = h.size(axis)
    Nx = x.size(axis)
    N = Nx + Nh - 1
    if nfft is None:
        nfft = 2**nextpow2(N)
    else:
        if nfft < N:
            raise ValueError("~~~To get right results, nfft must be larger than Nx+Nh-1!")

    x = padfft(x, nfft, axis, ftshift)
    h = padfft(h, nfft, axis, ftshift)
    x = fft(x, nfft, axis, norm=False, shift=ftshift)
    h = fft(h, nfft, axis, norm=False, shift=ftshift)
    y = ebemulcc(x, h)  # element-by-element complex multiplication
    # x, h = x.transpose(0, -1), h.transpose(0, -1)
    # y = th.stack((x[0] * h[0] - x[1] * h[1], x[0] * h[1] + x[1] * h[0]), dim=0)
    # y = y.transpose(0, -1)

    y = ifft(y, nfft, axis, norm=False, shift=ftshift)
    y = cutfftconv1(y, nfft, Nx, Nh, shape, axis, ftshift)

    if eps is not None:
        y[abs(y) < eps] = 0.

    return y


if __name__ == '__main__':
    import psar as ps

    shape = 'same'
    ftshift = False
    x_np = np.array([1, 2, 3, 4, 5])
    h_np = np.array([1 + 2j, 2, 3, 4, 5, 6, 7])

    x_th = th.tensor(x_np)
    h_th = th.tensor(h_np)
    x_th = th.stack([x_th, th.zeros(x_th.size())], dim=-1)
    h_th = th.stack([h_th.real, h_th.imag], dim=-1)

    y1 = ps.fftconv1(x_np, h_np, axis=0, Nfft=None, shape=shape, ftshift=ftshift)

    y2 = fftconv1(x_th, h_th, axis=0, nfft=None, shape=shape, ftshift=ftshift)
    y2 = th.view_as_complex(y2)
    y2 = y2.cpu().numpy()

    # print(y1)
    # print(y2)
    print(np.sum(np.abs(y1 - y2)), np.sum(np.angle(y1) - np.angle(y2)))

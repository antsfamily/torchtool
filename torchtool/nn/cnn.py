#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-07-24 18:29:48
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$


import numpy as np


def Conv2d(CHWi, Co, K, S, P, D=(1, 1), groups=1):
    r"""Compute shape after 2D-Convolution

    .. math::
       \begin{array}{l}
       H_{o} &= \left\lfloor\frac{H_{i}  + 2 \times P_h - D_h \times (K_h - 1) - 1}{S_h} + 1\right\rfloor \\
       W_{o} &= \left\lfloor\frac{W_{i}  + 2 \times P_w - D_w \times (K_w - 1) - 1}{S_w} + 1\right\rfloor
       \end{array}
       :label: equ-DilationConv2dSize

    CHWi : {tulpe or list}
        input data shape (C, H, W)
    Co : {integer number}
        number of output chanels.
    K : {tulpe}
        kernel size
    S : {tulpe}
        stride size
    P : {tulpe}
        padding size
    D : {tuple}, optional
        dilation size (the default is (1, 1))
    groups : {number}, optional
        [description] (the default is 1, which [default_description])

    Returns
    -------
    tulpe
        shape after 2D-Convolution

    Raises
    ------
    ValueError
        [description]
    """
    if D[0] + D[1] < 2:
        raise ValueError("dilation should be greater than zero")
    Ci, Hi, Wi = CHWi

    Ho = int(np.floor((Hi + 2 * P[0] - D[0] * (K[0] - 1) - 1) / S[0] + 1))
    Wo = int(np.floor((Wi + 2 * P[1] - D[1] * (K[1] - 1) - 1) / S[1] + 1))

    return Co, Ho, Wo


def ConvT2d(CHWi, Co, K, S, P, D=(1, 1), OP=(0, 0), groups=1):
    r"""Compute shape after Transpose Convolution

    .. math::
       \begin{array}{l}
       H_{o} &= (H_{i} - 1) \times S_h - 2 \times P_h + D_h \times (K_h - 1) + OP_h + 1 \\
       W_{o} &= (W_{i} - 1) \times S_w - 2 \times P_w + D_w \times (K_w - 1) + OP_w + 1
       \end{array}
       :label: equ-TransposeConv2dSize

    Parameters
    ----------
    CHWi : {tulpe or list}
        input data shape (C, H, W)
    Co : {integer number}
        number of output chanels.
    K : {tulpe}
        kernel size
    S : {tulpe}
        stride size
    P : {tulpe}
        padding size
    D : {tuple}, optional
        dilation size (the default is (1, 1))
    OP : {tuple}, optional
        output padding size (the default is (0, 0))
    groups : {integer number}, optional
        one group (the default is 1)

    Returns
    -------
    tulpe
        shape after 2D-Transpose Convolution

    Raises
    ------
    ValueError
        output padding must be smaller than either stride or dilation
    """

    if not ((OP[0] < S[0] and OP[1] < S[1]) or (OP[0] < D[0] and OP[1] < D[1])):
        raise ValueError(
            "output padding must be smaller than either stride or dilation")
    Ci, Hi, Wi = CHWi

    Ho = int((Hi - 1) * S[0] - 2 * P[0] + D[0] * (K[0] - 1) + OP[0] + 1)
    Wo = int((Wi - 1) * S[1] - 2 * P[1] + D[1] * (K[1] - 1) + OP[1] + 1)

    return Co, Ho, Wo


def Pool2d(CHWi, K, S, P, D=(1, 1)):
    Ci, Hi, Wi = CHWi

    Ho = int(np.floor((Hi + 2 * P[0] - D[0] * (K[0] - 1) - 1) / S[0] + 1))
    Wo = int(np.floor((Wi + 2 * P[1] - D[1] * (K[1] - 1) - 1) / S[1] + 1))

    return Ci, Ho, Wo


def UnPool2d(CHWi, K, S, P, D=(1, 1)):
    Ci, Hi, Wi = CHWi

    Ho = int((Hi - 1) * S[0] - 2 * P[0] + K[0])
    Wo = int((Wi - 1) * S[1] - 2 * P[1] + K[1])

    return Ci, Ho, Wo


if __name__ == '__main__':
    import torchtool as tht
    import torch as th

    n = 2
    CHWi = (4, 12, 12)
    Co = 16
    K = (3, 3)
    S = (2, 2)
    P = (1, 1)
    OP = (1, 1)
    D = (1, 1)

    print('===Conv2d')
    print(CHWi)
    print('---Theoretical result')

    CHWo = tht.Conv2d(CHWi=CHWi, Co=Co, K=K,
                      S=S, P=P, D=D)
    print(CHWo)

    print('---Torch result')
    x = th.randn((n, ) + CHWi)
    print(x.size())
    conv = th.nn.Conv2d(CHWi[0], Co, kernel_size=K,
                        stride=S, padding=P, dilation=D)
    y = conv(x)
    print(y.size())

    print('===Deconv2d')

    CHWo = tht.ConvTranspose2d(CHWi=CHWo, Co=CHWi[0], K=K,
                               S=S, P=P, D=D, OP=OP)
    print('---Theoretical result')
    print(CHWo)

    print('---Torch result')

    upconv = th.nn.ConvTranspose2d(Co, CHWi[0], kernel_size=K,
                                   stride=S, padding=P, output_padding=OP, dilation=D)
    xx = upconv(y)
    print(xx.size())

    print("===Pool2d")
    print('---Theoretical result')
    CHWo = tht.Pool2d(CHWi, K, S, P, D=D)
    print(CHWo)
    print('---Torch result')
    pool = th.nn.MaxPool2d(kernel_size=K, stride=S,
                           padding=P, dilation=D, return_indices=True)
    y, idx = pool(x)
    print(y.size())
    # print(idx)
    # print(y)

    print("===UnPool2d")
    print('---Theoretical result')
    CHWo = tht.UnPool2d(CHWo, K, S, P, D=D)
    print(CHWo)
    print('---Torch result')
    unpool = th.nn.MaxUnpool2d(kernel_size=K, stride=S, padding=P)
    xx = unpool(y, idx, output_size=x.size())
    print(xx.size())

    unpool = th.nn.MaxUnpool2d(kernel_size=K, stride=S, padding=P)
    xx = unpool(y, idx)
    print(xx.size())
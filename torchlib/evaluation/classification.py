#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-07-24 18:29:48
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$

import torch as th


def accuracy(X, Y, TH=None):
    r"""compute accuracy



    Parameters
    ----------
    X : {Torch Tensor}
        Predicted one hot matrix, :math:`\{0, 1\}`
    Y : {Torch Tensor}
        Referenced one hot matrix, :math:`\{0, 1\}`
    TH : {[type]}, optional
        threshold: X > TH --> 1, X <= TH --> 0
    """

    if TH is not None:
        X = (X > TH).float()

    X = (X > 0.5)
    Y = (Y > 0.5)

    acc = th.mean((X == Y).float()).item()

    return acc


if __name__ == '__main__':
    import numpy as np
    import torchlib as tl

    P = np.array([[1, 1, 1], [0, 1, 0]])
    R = np.array([[0, 0, 1], [0, 0, 1]])

    P = th.Tensor(P)
    R = th.Tensor(R)
    prec = tl.precision(P, R)
    print(prec)
    acc = accuracy(P, R)
    print(acc)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-07-24 18:29:48
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$

import torch as th
import torch.nn as nn
from torchlib.utils.const import EPS


class EntropyLoss(nn.Module):
    r"""Entropy loss



    """

    def __init__(self, mode='shannon', reduction='mean'):
        super(EntropyLoss, self).__init__()
        self.mode = mode
        self.reduction = reduction

    def forward(self, X):

        if th.is_complex(X):
            X = (X * X.conj()).real
        elif X.size(-1) == 2:
            X = th.sum(X.pow(2), axis=-1)

        if X.dim() == 2:
            axis = (0, 1)
        if X.dim() == 3:
            axis = (1, 2)
        if X.dim() == 4:
            axis = (1, 2, 3)

        P = th.sum(X, axis, keepdims=True)
        p = X / (P + EPS)
        if self.mode in ['Shannon', 'shannon', 'SHANNON']:
            S = -th.sum(p * th.log2(p + EPS), axis)
        if self.mode in ['Natural', 'natural', 'NATURAL']:
            S = -th.sum(p * th.log(p + EPS), axis)
        if self.reduction == 'mean':
            S = th.mean(S)
        if self.reduction == 'sum':
            S = th.sum(S)

        return S


if __name__ == '__main__':

    ent_func = EntropyLoss('shannon')
    ent_func = EntropyLoss('natural')
    X = th.randn(1, 3, 4, 2)
    S = ent_func(X)
    print(S)

    X = X[:, :, :, 0] + 1j * X[:, :, :, 1]
    S = ent_func(X)
    print(S)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-07-24 18:29:48
# @Author  : Zhi Liu (zhiliu.mind@gmail.com)
# @Link    : http://iridescent.ink
# @Version : $1.0$

import matplotlib.pyplot as plt


class LossLog():

    def __init__(self, plotdir=None, xlabel='Epoch', ylabel='Loss', title=None, logdict=None):
        self.plotdir = plotdir
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        if logdict is None:
            self.losses = {'train': [], 'valid': [], 'test': []}
        else:
            self.losses = logdict

    def assign(self, key, value):
        self.losses[key] = value

    def add(self, key, value):
        self.losses[key].append(value)

    def get(self, key=None):
        return self.losses[key]

    def updir(self, plotdir=None):
        self.plotdir = plotdir

    def plot(self):
        legend = []
        plt.figure()
        for k, v in self.losses.items():
            if len(v) > 0:
                plt.plot(v)
                legend.append(k)
        plt.legend(legend)
        plt.xlabel(self.xlabel)
        plt.ylabel(self.ylabel)
        plt.grid()

        if self.title is not None:
            plt.title(self.title)

        if self.plotdir is None:
            plt.show()
        else:
            plt.savefig(self.plotdir + '/' + self.ylabel + '_' + self.xlabel + '.png')
            plt.close()


if __name__ == '__main__':

    fdlr = LossLog(plotdir='./', xlabel='xlabel', ylabel='ylabel')
    fdlr = LossLog(plotdir='./', xlabel='Epoch', ylabel='Loss', title=None, logdict={'train':[], 'valid': []})
    for n in range(100):
        fdlr.add('train', n)
        fdlr.add('valid', n - 1)

    fdlr.plot()

from algorithms import regal, eigenalign, conealign, netalign, NSD, klaus
from data import ReadFile
from evaluation import evaluation, evaluation_design
from sacred import Experiment

ex = Experiment("experiment")


@ex.config
def global_config():

    gt = "data/example/gt.txt"
    data1 = "data/example/arenas_orig_100.txt"
    data2 = "data/example/arenas_orig_100.txt"

    gma, gmb = ReadFile.gt1(gt)
    G1 = ReadFile.edgelist_to_adjmatrix1(data1)
    G2 = ReadFile.edgelist_to_adjmatrix1(data2)
    adj = ReadFile.edgelist_to_adjmatrixR(data1, data2)


@ex.capture
def eval_regal(_log, gma, gmb, adj):
    alignmatrix = regal.main(adj)
    mar, mbr = evaluation.transformRAtoNormalALign(alignmatrix)
    acc = evaluation.accuracy(gma, gmb, mbr, mar)
    _log.info(f"acc1: {acc}")

    return acc


@ex.capture
def eval_eigenalign(_log, gma, gmb, G1, G2):
    ma1, mb1, _, _ = eigenalign.main(G1, G2, 8, "lowrank_svd_union", 3)
    acc = evaluation.accuracy(gma+1, gmb+1, mb1, ma1)
    _log.info(f"acc: {acc}")

    return acc


@ex.capture
def eval_conealign(_log, gma, gmb, G1, G2):
    alignmatrix = conealign.main(G1, G2)
    mar, mbr = evaluation.transformRAtoNormalALign(alignmatrix)
    acc = evaluation.accuracy(gma, gmb, mbr, mar)
    _log.info(f"acc1: {acc}")

    return acc


@ex.capture
def eval_netalign(_log, data1, data2):
    import numpy as np

    S = "data/karol/S.txt"
    li = "data/karol/li.txt"
    lj = "data/karol/lj.txt"

    S = ReadFile.edgelist_to_adjmatrix1(S)
    li = np.loadtxt(li, int)
    lj = np.loadtxt(lj, int)
    li -= 1
    lj -= 1

    # S = ReadFile.edgelist_to_adjmatrix1(data1)
    # M = np.loadtxt(data2, int)
    # li, lj = M.transpose()

    w = np.ones(len(li))
    matching = netalign.main(S, w, li, lj, a=0)

    _log.info(matching)


@ex.capture
def eval_NSD(_log, gma, gmb, G1, G2):
    ma, mb = NSD.run(G1, G2)
    print(ma)
    print(mb)
    print(gmb)
    # acc = evaluation.accuracy(gma, gmb, mb, ma)
    # print(acc)


@ex.capture
def eval_klaus(_log, data1, data2):
    import numpy as np

    S = "data/karol/S.txt"
    li = "data/karol/li.txt"
    lj = "data/karol/lj.txt"

    S = ReadFile.edgelist_to_adjmatrix1(S)
    li = np.loadtxt(li, int)
    lj = np.loadtxt(lj, int)
    li -= 1
    lj -= 1

    # S = ReadFile.edgelist_to_adjmatrix1(data1)
    # M = np.loadtxt(data2, int)
    # li, lj = M.transpose()

    w = np.ones(len(li))
    matching = klaus.main(S, w, li, lj, a=0, maxiter=1)

    _log.info(matching)


@ex.automain
def main():
    eval_regal()
    eval_eigenalign()
    eval_conealign()
    eval_netalign()
    eval_NSD()
    eval_klaus()

import numpy as np
#from scipy.optimize import linear_sum_assignment
from numpy.linalg import inv
from numpy.linalg import eigh,eig
import networkx as nx 
import random
from math import floor, log2
#from lapsolver import solve_dense
import scipy as sci
#from lapsolver import solve_dense
from numpy import inf, nan
import scipy.sparse as sps
try:

    import lapjv

except:

    pass


def create_L(A, B, lalpha=1, mind=None, weighted=True):
    n = A.shape[0]
    m = B.shape[0]

    if lalpha is None:
        return sps.csr_matrix(np.ones((n, m)))

    a = A.sum(1)
    b = B.sum(1)
    # print(a)
    # print(b)
    DegA=A.sum()
    DegB=B.sum()
    # a_p = [(i, m[0,0]) for i, m in enumerate(a)]
    a_p = list(enumerate(a))
    a_p.sort(key=lambda x: x[1])

    # b_p = [(i, m[0,0]) for i, m in enumerate(b)]
    b_p = list(enumerate(b))
    b_p.sort(key=lambda x: x[1])

    ab_m = [0] * n
    s = 0
    e = floor(lalpha * log2(m))
    a=a/DegA
    b=b/DegB
    for ap in a_p:
        while(e < m and
              abs(b_p[e][1] - ap[1]) <= abs(b_p[s][1] - ap[1])
              ):
            e += 1
            s += 1
        ab_m[ap[0]] = [bp[0] for bp in b_p[s:e]]

    # print(ab_m)

    li = []
    lj = []
    lw = []
    for i, bj in enumerate(ab_m):
        for j in bj:
            # d = 1 - abs(a[i]-b[j]) / a[i]
            d = 1 - abs(a[i]-b[j]) / max(a[i], b[j])
            #d = 1 - abs(a[i]-b[j]) / a[i]+b[j]
            if mind is None:
                if d > 0:
                    li.append(i)
                    lj.append(j)
                    lw.append(d)
            else:
                li.append(i)
                lj.append(j)
                lw.append(mind if d <= 0 else d)
                # lw.append(0.0 if d <= 0 else d)
                # lw.append(d)

                # print(len(li))
                # print(len(lj))
                # print(len(lj))

    return sps.csr_matrix((lw, (li, lj)), shape=(n, m))

def decompose_laplacian(A):

    #  adjacency matrix

    Deg = np.diag((np.sum(A, axis=1)))

    n = np.shape(Deg)[0]
    
    Deg = sci.linalg.fractional_matrix_power(Deg, -0.5)
    L = (np.identity(n)) - Deg @ A @ Deg
    #P=np.linalg.inv(Deg)@ A@np.linalg.inv(Deg)
    #L=np.identity(n) + P
    #L=Deg-A
    D, V = np.linalg.eigh(L)

    return [D, V]


def decompose_Tlaplacian(A,rA):

    #  adjacency matrix
    r= (rA**2-1)
    Deg = np.diag((np.sum(A, axis=1)))

    n = np.shape(Deg)[0]

    #Deg = sci.linalg.fractional_matrix_power(Deg, -0.5)

    L = r* np.identity(n) + Deg - rA*A 
   # print((sci.fractional_matrix_power(Deg, -0.5) * A * sci.fractional_matrix_power(Deg, -0.5)))
    # '[V1, D1] = eig(L1);

    D, V = np.linalg.eigh(L)

    return [D, V]

def seigh(A):
  """
  Sort eigenvalues and eigenvectors in descending order. 
  Not used.
  """
  l, u = np.linalg.eigh(A)
  idx = l.argsort()[::-1]   
  l = l[idx]
  u = u[:,idx]
  return l, u
def main(data, eta,lalpha):
  Src = data['Src']
  Tar = data['Tar']
  n = Src.shape[0]
  #l,U =eigh(Src)
  #mu,V = eigh(Tar)
  #lalpha=10000
  alpha=0
  dtype = np.float32
  L = create_L(Src, Tar, lalpha,
                     True).A.astype(dtype)
  K = ((1-alpha) * L).astype(dtype)*1
  #l,U =eigh(Src)
  #mu,V = eigh(Tar)
  l, U = decompose_laplacian(Src)
  mu, V = decompose_laplacian(Tar)
  #l, U = decompose_Tlaplacian(Src,2)
 # mu, V = decompose_Tlaplacian(Tar,2)
  l = np.array([l])
  mu = np.array([mu])
  #Eq.4
  #coeff = 1.0/((l.T - mu)**2 + eta**2)
  coeff = 1.0/((l.T - mu)**2 + eta**2)
  #Eq. 3
  #coeff = coeff * (U.T @ np.ones((n,n)) @ V)
  coeff = coeff * (U.T @ K @ V)
  X = U @ coeff @ V.T 

  Xt = X.T*-1
  
  #Xt=-X
  # Solve with linear assignment maximizing the similarity 
  # row,col = linear_sum_assignment(Xt, maximize=True)

  # Alternatively, we can use a more efficient solver.
  # The solver works on cost minimization, so take -X 
  #rows, cols = solve_dense(-Xt)
  #return rows, cols 
  try:
    cols, rows, _ = lapjv.lapjv(Xt)
    matching = np.c_[np.linspace(0, n-1, n).astype(int),rows]
  except Exception:
    cols, rows = sci.optimize.linear_sum_assignment(Xt)
    matching = np.c_[rows,cols]
    

    # print(cols)

    # print(rows)

    #matching = np.c_[np.linspace(0, n-1, n).astype(int),cols]
    
    #matching = np.c_[cols,np.linspace(0, n-1, n).astype(int)]
    #matching = np.c_[rows,np.linspace(0, n-1, n).astype(int)]

    # print(matching)

  matching = matching[matching[:, 0].argsort()]

    # print(matching)

  return matching.astype(int).T
  #return Xt

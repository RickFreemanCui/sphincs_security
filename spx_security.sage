#### Generic caching layer to save time

import collections
try:
  # Python 3.3+ moved abstract base classes to collections.abc. Use a fallback
  # so this script works on both older and newer Python versions.
  from collections.abc import Hashable
except Exception:
  Hashable = collections.Hashable

class memoized(object):
  def __init__(self,func):
    self.func = func
    self.cache = {}
    self.__name__ = 'memoized:' + func.__name__
  def __call__(self,*args):
    if not isinstance(args, Hashable):
      return self.func(*args)
    if args not in self.cache:
      self.cache[args] = self.func(*args)
    return self.cache[args]

#### SPHINCS+ analysis
@memoized
def bit_security(tsec,maxsigs,h,d,b,k,w):

    F = RealIntervalField(tsec+100)
    sigmalimit = F(2^(-tsec))
    donelimit  = 1-sigmalimit/2^20
    hashbytes  = tsec/8 # length of hashes in bytes

    # Pr[exactly r sigs hit the leaf targeted by this forgery attempt]
    @memoized
    def qhitprob(leaves,qs,r):
        p = 1/F(leaves)
        return binomial(qs,r)*p^r*(1-p)^(qs-r)

    # Pr[FORS forgery given that exactly r sigs hit the leaf] = (1-(1-1/F(2^b))^r)^k
    @memoized
    def forgeryprob(b,r,k):
        if k == 1: return 1-(1-1/F(2^b))^r
        return forgeryprob(b,r,1)*forgeryprob(b,r,k-1)

    leaves = 2 ** h
    sigma = 0
    r = 1
    done = qhitprob(leaves,maxsigs,0)
    while done < donelimit:
        t = qhitprob(leaves,maxsigs,r)
        sigma += t*forgeryprob(b,r,k)
        if sigma > sigmalimit: break
        done  += t
        r     += 1
    sigma += min(0,1-done)
    return -1 * log(sigma,2).n(30)

tsec=16*8
maxsigs=2**64
h=63
d=7
b=12 # log t
k=14
w=16

# # print (bit_security(tsec,maxsigs,h,d,b,k,w))
# #SPHINCS+-128s 16 63 7 12 14 16 133 1 7 856  
# print (bit_security(16*8,maxsigs,63,7,12,14,16))
# #SPHINCS+-128f 16 66 22 6 33 16 128 1 17 088  
# print (bit_security(16*8,maxsigs,66,22,6,33,16))
# #SPHINCS+-192s 24 63 7 14 17 16 193 3 16 224  
# print (bit_security(24*8,maxsigs,63,7,14,17,16))
# #SPHINCS+-192f 24 66 22 8 33 16 194 3 35 664  
# print (bit_security(24*8,maxsigs,66,22,8,33,16))
# #SPHINCS+-256s 32 64 8 14 22 16 255 5 29 792  
# print (bit_security(32*8,maxsigs,64,8,14,22,16))
#SPHINCS+-256f 32 68 17 9 35 16 255 5 49 856
print (bit_security(32*8,maxsigs,68,17,9,35,16))



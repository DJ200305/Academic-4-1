import random
import math
def primeFactors(n):
    f = []
    while n % 2 == 0:
        f.append(2)
        n //= 2
    fact = 3
    while fact*fact <= n:
       while n % fact == 0:
           f.append(fact)
           n //= fact
       fact += 2
    if n > 2:
        f.append(n)
    return f                   

def millerRabin(n,k):
    if  n == 2:
        return True
    if n % 2 == 0:
        return False
    d = n-1
    s = 0

    while d % 2 == 0:
        d //= 2
        s += 1
    for i in range(k):
        a = random.randint(2,n-2)
        x = pow(a,d,n)
        if x == n-1 or x == 1:
            continue
        flag = True
        for j in range(s-1):
            x = pow(x,2,n)
            if x == n-1:
                flag = False
                break
        if flag:
            return False
    return True

def genRandPrime(k):
    while True:
        mid = random.getrandbits(k-3)
        q = (1 << (k-2)) | (mid << 1) | 1
        if millerRabin(q,40):
            p = 2*q+1
            if millerRabin(p,40):
                return p,q
    

def genCand(p,q):
    x = [2,q]
    for i in range(2,p):
        flag = True
        for y in range(len(x)):
            r = x[y]
            tmp = (p-1)//r
            tmp1 = pow(i,tmp,p)
            if tmp1 == 1:
                flag = False
                break
        if flag:
            return i    

def genPKey(k,p):
    lo = 1 << (k-1)
    hi = p-2
    while True:
        p_key = random.randint(lo,hi)
        if p_key.bit_length() >= k:
            return p_key            
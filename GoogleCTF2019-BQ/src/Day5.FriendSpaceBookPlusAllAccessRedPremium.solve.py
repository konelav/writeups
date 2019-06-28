#!/usr/bin/python
N = 10000
sieve = [True] * N
for i in range(3,int(N**0.5)+1,2):
    if sieve[i]:
        sieve[i*i::2*i]=[False]*int((N-i*i-1)/(2*i)+1)
primes = [2] + [i for i in range(3,N,2) if sieve[i]]

def is_prime(n):
    limit = int(n**0.5)
    for p in primes:
        if p > limit:
            break
        if n % p == 0:
            return False
    return True


def gen_keys(upto):
    ret = [2, 3, 5, 7, 11]
    l = len(str(upto)) // 2
    for part in range(1, 10**l):
        left = str(part)
        right = left[::-1]
        for m in range(10):
            n = int(left + str(m) + right)
            if is_prime(n):
                ret.append(n)
    return ret

keys = gen_keys(10000000)

data = []
with open('new.program', 'r') as f:
    temp = []
    for line in f.readlines():
        if line.startswith('load acc1') and line.strip().endswith('push acc1'):
            num = int(line[9:line.find('EoN')].replace(' ', ''))
            if num != 0:
                temp.append(num)
        elif line.startswith('load acc2'):
            base = int(line[9:line.find('EoN')].replace(' ', ''))
            for i, num in enumerate(reversed(temp)):
                data.append((base + i, num))
            temp = []

print("".join([chr(char ^ keys[i-1]) for i, char in data]))

#!/usr/bin/python
with open('msg.txt', 'r') as f:
    lines = f.readlines()
N = int(lines[1])
e = int(lines[4])
m = int(lines[7], 16)
print ("len(N) = {}".format(len(bin(N)) - 2))
print ("len(m) = {}".format(len(bin(m)) - 2))


def int_sqrt(N):  # Newton's method of finding floor(sqrt(N))
    x = N     # initial guess of square root, certainly not below the needed value
    while True:
        # equation to solve: 0 = f(x) = x^2 - N  =>  f'(x) = 2 * x
        # newton's step: x(i+1) = x(i) - f(x(i)) / f'(x(i)) = (x(i) + N / x(i)) / 2
        next_x = (x + N // x) // 2
        if next_x >= x:
            return x
        x = next_x

def fermat_factor(N, max_b=None):  # optionally stop searching of factors when difference between them reaches certain limit
    a = int_sqrt(N)
    b_square = a*a - N  # since N = (a - b)*(a + b) = a^2 - b^2 => b^2 = a^2 - N
    while a <= N:
        b = int_sqrt(b_square)
        if b*b == b_square:  # yes, we find it
            return a - b, a + b
        if max_b is not None and b > max_b:
            break
        b_square += 2*a + 1  #same as: b_square = (a + 1)*(a + 1) - N
        a += 1

#do basic check of proper implementation
print(fermat_factor(2017), fermat_factor(5959))
print(fermat_factor(5*6))

checked = set()
for A in range(794, 1000+1):
    print("A = {} (checked {} value(s))".format(A, len(checked)))
    for B in range(1, A+1):
        ABx4 = 4*A*B
        if ABx4 in checked:
            continue
        checked.add(ABx4)
        factors = fermat_factor(ABx4*N, 10000)
        if factors is not None:
            break
    if factors is not None:
        break
APx2, BQx2 = factors
P = APx2 // (A*2)
Q = BQx2 // (B*2)
if P*Q != N:
    raise
print("P = {}".format(P))
print("Q = {}".format(Q))

def inverse(a, n):
    t, next_t, r, next_r = 0, 1, n, a
    while next_r != 0:
        q = r // next_r
        t, next_t, r, next_r = next_t, (t - q * next_t), next_r, (r - q * next_r)
    if t < 0: 
        t = t + n
    return t

def decrypt(p, q, e, ct):
    n = p * q
    phi = (p - 1) * (q - 1)
    d = inverse(e, phi)
    pt = pow(ct, d, n)
    return pt


import binascii

pt = decrypt(P, Q, e, m)
msg = binascii.unhexlify(hex(pt)[2:].replace('L', ''))
print(msg)

while plain > 0:
    contents.insert(0, plain & 0xff)
    plain >>= 8
print(contents)

txt = bytearray(contents)
print(txt.decode())

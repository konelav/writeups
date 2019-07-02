Crypto Caulingo (**crypto**)

    Well you've done it, you're now an admin of the Cookie World Order. 
    The clandestine organisation that seeks to control the world 
    through a series of artfully placed tasty treats, bringing folks 
    back in to their idea of what a utopian society would look like. 
    Strangely enough, the webcam data is being fed to understand the 
    properties of the entities you had originally seen. They seem to be 
    speaking back into the camera (an unadvertised microphone) but it's 
    hard to understand what they want. You must- if nothing else ever 
    was important in your life, you must make contact with these 
    beautiful creatures! Also, what exactly is a "cauliflower"?


Attachment contains archive with two files: technical paper with 
research about some intercepted conversational data `project_dc.pdf`, 
and intercepted data itself `msg.txt`, which can be easily parsed:
    
    with open('msg.txt', 'r') as f:
    lines = f.readlines()
    N = int(lines[1], 10)
    e = int(lines[4], 10)
    m = int(lines[7], 16)
    print ("len(N) = {} bit(s)".format(len(bin(N)) - 2))
    print ("len(m) = {} bit(s)".format(len(bin(m)) - 2))


    $ python factor.py 
    len(N) = 2048 bit(s)
    len(m) = 2047 bit(s)

From paper we know that encryption algorithm is classical RSA and that 
there are some restrictions for encryption parameters.
If one is not familiar with RSA algorithm, quick reading Wikipedia 
article should be enough for this task. What is important:

  - encryption parameter n most certainly has only two factors, big 
  prime numbers P and Q: `n = P*Q`
  - essentially this factorization is the main `secret`, all the others
  secrets can be calculated from `P`, `Q` and publicly available `e`
  - therefore, if only we could find such `P` and `Q` that `n = P*Q`, 
  we can easily decrypt message, i.e. calculate some big number that 
  being written in binary format represents some data, often 
  compressed, but also it can be simple ascii text

In general, factorization problem is hard. There is online service 
*factordb* which can do simple factorization and primality-tests for 
proving that given number is prime or composite. Unfortunately, such 
proves are often probabalistic and for big numbers are 
non-constructive, i.e. even if they can guarantee that number is 
composite, they can't find any factor of it (most common of such tests 
are *Fermat test* and *Rabin Miller test*). Trying to post given `n` to 
*factordb* web service gives nothing except that it is proved that `n` 
is composite, with unknown factors.

Fortunately, there are very strict limitations on `P` and `Q` in our 
certain case. We are guaranteed that such integers `A` and `B` exists 
that `A*P` and `B*Q` are very close numbers. And in Wikipedia we 
can find that close factors of `n` is the basic example of vulnerable 
key generation, because there is effective algorithm called *Fermat 
factorization* that can relatively quick factorize such number. In a 
few words, *Fermat factorization* tries to represent given composite 
`n` as a multiplication `(a + b)*(a - b)` where `b` is some *small* 
number and hence `a` is very close to square root of `n`.

Very straightforward implementation of this simple algorithm:

    def int_sqrt(N):  # Newton's method of finding floor(sqrt(N))
        x = N     # initial guess of square root, certainly not below the needed value
        while True:
            # equation to solve: 0 = f(x) = x^2 - N  =>  f'(x) = 2 * x
            # newton's step: x(i+1) = x(i) - f(x(i)) / f'(x(i)) = (x(i) + N / x(i)) / 2
            next_x = (x + N // x) // 2
            if next_x >= x:
                return x
            x = next_x
    
    def fermat_factor(N, max_b=None):  # optionally stop searching of factors when difference between them exceeds certain limit
        a = int_sqrt(N)
        b_square = a*a - N  # since N = (a + b)*(a - b) = a^2 - b^2 => b^2 = a^2 - N
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
    print(fermat_factor(N))


    $ python factor.py 
    len(N) = 2048
    len(m) = 2047
    ((1, 2017), (59, 101))
    ^CTraceback (most recent call last):
      File "factor.py", line 34, in <module>
        print(fermat_factor(N))
      File "factor.py", line 24, in fermat_factor
        b = int_sqrt(b_square)
      File "factor.py", line 15, in int_sqrt
        next_guess = (guess + N // guess) // 2
    KeyboardInterrupt


It takes too much time... how close can be `P` and `Q` in our case? We 
know that `A` and `B` both are between `1` and `1000`, so the biggest
possible ratio `P / Q = (a + b) / (a - b)` is `1000`. The `n` itself is 
2048-bits long, hence sum of lengths of `P` and `Q` should be something 
like that, and ratio `1000 ~= 2^10` can be achieved with bit-lengths 
`1024-5 = 1019` and `1024+5 = 1029`. The difference between 1029-bits 
number and 1019-bits number is near 1029-bits long itself, this is 
huge value, definitely we can't iterate through so much possibilities.

But we are told that little difference is not between `P` and `Q` 
numbers, but between some of their multiples `A*P` and `B*Q`, and this 
difference is very very small, not bigger than 10000. Still, `A` and 
`B` are unknown, but amount of their possible values is not greater 
than `1000*1000 = 1000000` which looks managable, i.e. we can just 
brute-force all possible values of `A` and `B` trying to factorize 
`A*B*N = (A*P) * (B*Q)` and we can expect that with proper values 
*Fermat factorization* will give us an answer with `A*P` and `B*Q` 
values, which in turn we can use to obtain `P` and `Q`.

It is obvious that not every combination of `A` and `B` must be 
checked. For example, there is no reason to check diffirent 
combinations that gives same multiple, for example `A = 2, B = 10` and 
`A = 4, B = 5`, since both cases will call *Fermat factorization* with 
exactly the same argument `20*N`. Actually, we can even check only such 
pairs that `GCD(A,B) == 1`, though it can't give much acceleration.
Additionally, we can state that `A <= B`, and if it's not true, just 
swap `P` and `Q` and hence `A` and `B` values so it becomes true.

    checked = set()
    for A in range(1, 1000+1):
        print("A = {} (checked {} value(s))".format(A, len(checked)))
        for B in range(1, A+1):
            AB = A*B
            if AB in checked:
                continue
            checked.add(AB)
            # in practice, such small limitation on max_b leads to just a single iteration within fermat_factor
            factors = fermat_factor(AB*N, 10000)
            if factors is not None:
                break
        if factors is not None:
            break
    AP, BQ = factors
    P = AP // A
    Q = BQ // B
    if P*Q != N:
        raise
    print("P = {}".format(P))
    print("Q = {}".format(Q))


    $ python factor.py 
    len(N) = 2048
    len(m) = 2047
    ((1, 2017), (59, 101))
    A = 1 (checked 0 value(s))
    A = 2 (checked 1 value(s))
    A = 3 (checked 3 value(s))
    A = 4 (checked 6 value(s))
    A = 5 (checked 9 value(s))
    A = 6 (checked 14 value(s))
    ...........................
    A = 999 (checked 247445 value(s))
    A = 1000 (checked 247814 value(s))
    Traceback (most recent call last):
      File "factor.py", line 48, in <module>
        AP, BQ = factors
    TypeError: 'NoneType' object is not iterable


So much fail! At this point we should assume that either is true:

  - solution implementation is wrong;
  - solution logic is wrong;
  - understanding of problem statement is wrong;
  - problem statement is wrong.

The first one is (and always will be) the most suspected, but no, both 
code-review and unit-testing tell that all is correct.

The last one can be excluded because it is serious contest from Google 
and I believe that problems were checked many times and revised by 
different people.

Good understanding is often my problem, so I even went to IRC channel 
and bothered **@caulilinux**, and (s)he approved that my understanding 
is accurate enough.

The last thing remained: logic of the approach. So let's take a piece 
of paper, a pencil and write down all the facts very carefully and 
attentively:

    (1) N = P*Q                         ; primality test of *factordb* said so
    (2) A*P = B*Q + C                   ; where -10000 < C < +10000, from `project_dc.pdf`
    (3) A*B*N = (a + b)*(a - b)         ; Fermat factorization's assumtion
    (4) A*B*N = A*B*P*Q = (A*P) * (B*Q) ; simply multiplication associativity
    (5) a + b = A*P,  a - b = B*Q       ; from (3) and (4)
    (6) a + b = a - b + C               ; from (2) and (5)
    (7) 2*b = C                         ; from (6)

Here it is, `C` **must** be even for success of our solution (and 
to be precise `abs(b) < 5000`, but this is minor issue). But there is 
no such restriction on it in `project_dc.pdf`!
Why we have this limitation? Well, it is obvious that *Fermat 
factorization* tries to find factors that differ by even value, since 
`(a + b) - (a - b) = 2*b`. Usually this is not a problem and quick 
search on the Web shows that this fact is rarely discussed or even 
pointed out. Probably it's because in practice one discusses 
factorizing by *big prime numbers*  (much greater than 2), and their 
difference is always even.
For example, if we take prime number `P`, multiply it by `(P + 1)` and 
try to factorize the result with this algorithm, we probably will be 
waiting for a very long time, until there will be found two even 
factors (they both can't be odd because then their multiple will be 
odd, but `P*(P+1)` is guaranteed to be even) or algorithm failed at 
all. Indeed, `fermat_factor(5*6) is None`.
Therefore, for even input *Fermat factorization* can only find any 
solution if input is a multiple of 4 (`(2*P)*(2*Q) = 4*P*Q`). 

Taking in account all said above, patch our `fermat_factor` 
implementation:

    def fermat_factor(N, max_b=None):  # optionally stop searching of factors when difference between them reaches certain limit
        x4 = (N % 2 == 0 and N % 4 != 0)
        if x4:  # factorization will fail without multiplication by 4
            N *= 4
        a = int_sqrt(N)
        b_square = a*a - N  # since N = (a - b)*(a + b) = a^2 - b^2 => b^2 = a^2 - N
        while a <= N:
            b = int_sqrt(b_square)
            if b*b == b_square:  # yes, we find it
                if x4:
                    return (a - b) // 2, (a + b) // 2
                return a - b, a + b
            if max_b is not None and b > max_b:
                break
            b_square += 2*a + 1  #same as: b_square = (a + 1)*(a + 1) - N
            a += 1

Now `fermat_factor(5*6)` works just fine, so we can try again:

    $ python factor.py 
    len(N) = 2048
    len(m) = 2047
    ((1, 2017), (59, 101))
    A = 1 (checked 0 value(s))
    A = 2 (checked 1 value(s))
    A = 3 (checked 3 value(s))
    A = 4 (checked 6 value(s))
    A = 5 (checked 9 value(s))
    A = 6 (checked 14 value(s))
    ...........................
    A = 793 (checked 157458 value(s))
    A = 794 (checked 157903 value(s))
    P = 115502906812186413716028212900548735990904256575141882752425616464266991765240920703188618324966988373216520827723741484031611192826120314542453727041306942082909556327966471790487878679927202639569020757238786152140574636623998668929044300958627146625246115304479897191050159379832505990011874114710868929959
    Q = 151086174643947302290817794140091756798645765602409645643205831091644137498519425104335688550286307690830177161800083588667379385673705979813357923016141205953591742544325170678167010991535747769057335224460619777264606691069942245683132083955765987513089646708001710658474178826337742596489996782669571549253


Got it! Now it is relatively easy to decode message. All we need is to 
carefully implement several equations from Wikipedia, most difficult 
of which is modulo inversion, which often implemented with extended 
euclidian algorithm for greatest common divisor. Alternatively, these 
pieces of code can be copy-pasted from stackoverflow or some writeup.


    def inverse(a, n):  # computes x such as (a * x) % n = 1
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


    $ python solve.py 
    len(N) = 2048
    len(m) = 2047
    ((1, 2017), (59, 101))
    ......................
    P = 115502906812186413716028212900548735990904256575141882752425616464266991765240920703188618324966988373216520827723741484031611192826120314542453727041306942082909556327966471790487878679927202639569020757238786152140574636623998668929044300958627146625246115304479897191050159379832505990011874114710868929959
    Q = 151086174643947302290817794140091756798645765602409645643205831091644137498519425104335688550286307690830177161800083588667379385673705979813357923016141205953591742544325170678167010991535747769057335224460619777264606691069942245683132083955765987513089646708001710658474178826337742596489996782669571549253
    Hey there!

    If you are able to decrypt this message, you must a life form with high intelligence!

    Therefore, we would like to invite you to our dancing party! 

    Here’s your invitation code: CTF{017d72f0b513e89830bccf5a36306ad944085a47}


**CTF{017d72f0b513e89830bccf5a36306ad944085a47}**

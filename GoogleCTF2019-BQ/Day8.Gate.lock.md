Gate lock (**hardware**)

    So close!! You have landed. Getting to the farm was no problem, but 
    these poor, helpless, if not stunning creatures are trapped behind 
    a gate and a fence. All that stands between you and your destiny is 
    this contraption of earthly construction. Though surely 
    rudimentary, how do such things work? You barely have experience 
    with three dimensional objects, none the less physical matter in 
    this particular dimension's structure of forces. (Flag format is 
    binary surrounded by CTF{...})


Attachment contains a lot of different files. At first it looks like 
some sort of reversing problem, and not hardware, at least for me, 
beacause I had no idea what is it all about. I looked into text 
files, opened sqlite3 databases, wrote simple script for grabbing map 
data and started to analyze map nodes with "unusual" size...
At one point I realized that string "mesecons" appeared very often in 
different places. Having no hope, I decided to give a try to Google... 
Yeah, stupid feeling, it is just a computer game *minetest* and it's 
mod *mesecons*.

Alas, my lovest good Debian 9 have too old minetest and mesecons mod 
package in it's repos. But they both can be downloaded from github and 
compiled from sources, then attachment can be copied to the appropriate 
folders and we can run mod within minetest game.

The task looks very simple: we need to find some combination of binary 
inputs (`on/off`, or `1/0`) such that given circuitry powers on some 
lamp. Circuitry consists of basic logic elements `and`, `or` and `not` 
and has 20 inputs.
At this point I was very tired and quickly realized that circuitry is 
very simple. Actually *complexity* of this task depends not only on the 
number of inputs, but also on the overall structure. Here we have a lot 
of `and` gates which have non-inverted inputs and as such give us huge 
information about needed state of most wires in the net, reducing 
number of possibilities drastically. I decided not to waste time on 
patching minetest or world configuration for some sort of benefits 
(like switching on-off certain inputs with single keypresses), or parse 
world data. Instead I just solve this task in some 15 or 20 minutes 
with the following simple rules:

  - wire on lamp's input must be powered ON - it's the beginning of 
  quest
  - if wire on NOT-output must be powered ON then it must be powered 
  OFF on it's input and vice versa
  - if wire on AND-gate output must be powered ON then both of it's 
  inputs must be powered ON
  - if wire on OR-gate output must be powered OFF then both of it's 
  inputs must be powered OFF
  - just ignore all other gates at this stage

After this we can have about half of inputs with known proper states. 
It is useful to have piece of paper and a pencil to write which inputs 
have known states and which are still unknown. Then the following 
simple rules can be applied:

  - if wire on AND-gate output must be turned OFF and one of it's 
  inputs comes from known circuitry inputs and is powered ON, then 
  other input must be powered OFF
  - if wirte on OR-gate output must be turned ON and one of it's inputs 
  comes from known circuitry inputs and is powered OFF, then other 
  input must be powered ON

Applying this rule several times leads to powered on lamp.


Of course there is nothing noble in the above solution.
So let's try to solve the task in assumption that the circuitry is very 
complex and can't be processed by any mortal man in any reasonable time.

We can do quick search on the web or do something like `apt source 
minetest` to get information about format of schematics binary file 
`challenge.mts`. It's layout is almost as the following (taken from 
minetest wiki):

    All values are stored in big-endian byte order.
    [u32] signature: 'MTSM'
    [u16] version: 4
    [u16] size X
    [u16] size Y
    [u16] size Z
    For each Y:
        [u8] slice probability value
    [Name-ID table] Name ID Mapping Table
        [u16] name-id count
        For each name-id mapping:
            [u16] name length
            [u8[]] name
    ZLib deflated {
    For each node in schematic:  (for z, y, x)
        [u16] content
    For each node in schematic:
        [u8] param1
          bit 0-6: probability
          bit 7:   specific node force placement
    For each node in schematic:
        [u8] param2
    }


After looking to the hexdump we can see that version of our binary is 1 
and that `slice probability value` is abscent, i.e. table of string 
constants starts immidiately after size-Z:

    $ xxd -g 1 -l 32 -c 8 challenge.mts
    00000000: 4d 54 53 4d 00 01 00 3b  MTSM...;
    00000008: 00 02 00 4b 00 0e 00 03  ...K....
    00000010: 61 69 72 00 05 73 74 6f  air..sto
    00000018: 6e 65 00 16 6d 65 73 65  ne..mese

Parsing this file with python is quite simple:


    import struct
    import zlib

    with open('challenge.mts', 'rb') as f:
        mts = f.read()
    (signature, version, sizex, sizey, sizez), body = \
        struct.unpack('>4sHHHH', mts[:4+2*4]), mts[4+2*4:]
    names = []
    (name_id_count,), body = struct.unpack('>H', body[:2]), body[2:]
    for i in range(name_id_count):
        (name_length,), body = struct.unpack('>H', body[:2]), body[2:]
        name, body = body[:name_length], body[name_length:]
        names.append(name)
    body = zlib.decompress(body)

    print("Signature: {}, version: {}, dimensions: {} x {} x {}, body: {}b".format(
        signature, version, sizex, sizey, sizez, len(body)))
    print("Names table: {}".format(names))


Now to the parsing of `body`. `content` field is just an index in the 
`names` table, which in fact is the type of tile placed in this map 
cell (logic gate, wire, wall etc.). `param1` is not of our intereset, 
and `param2` specifies rotation of the tile (0, 1, 2, 3 rotates basic 
tile for 0, 90, 180 and 270 degrees respectively).
How can we know it? First, it can be seen from mesecon-mod sources 
where this parameter corresponds to `facedir` property. Second, we can 
do several experiments with generating scheme like ASCII-art.
One way or another, schematic as a 2D-array of gates and wires can be 
parsed from body as follows:

    LEFT, TOP, RIGHT, BOTTOM = (0, -1), (1, 0), (0, 1), (-1, 0)
    CONNECTIONS = {
        ('insulated', 0): [[LEFT, RIGHT]],
        ('insulated', 3): [[TOP, BOTTOM]],
        ('corner', 0): [[LEFT, BOTTOM]],
        ('corner', 1): [[LEFT, TOP]],
        ('corner', 2): [[RIGHT, TOP]],
        ('corner', 3): [[RIGHT, BOTTOM]],
        ('crossover', 3): [[LEFT, RIGHT], [TOP, BOTTOM]],
        ('tjunction', 1): [[LEFT, TOP, BOTTOM]],
        ('tjunction', 3): [[RIGHT, TOP, BOTTOM]]
    }

    N = sizez * sizey * sizex
    o0, o1, o2 = 0, N*2, N*3
    scheme = []
    argc = 0
    for z in range(sizez):
        for y in range(sizey):
            row = []
            for x in range(sizex):
                nameid, = struct.unpack('>H', body[o0:o0+2])
                param1, = struct.unpack('>B', body[o1:o1+1])
                param2, = struct.unpack('>B', body[o2:o2+1])
                o0, o1, o2 = o0 + 2, o1 + 1, o2 + 1
                name = names[nameid]
                node = name[name.find(':')+1:name.rfind('_')]
                edges = {LEFT: None, TOP: None, RIGHT: None, BOTTOM: None}
                if node == 'lamp' >= 0:
                    lamp = (x, z)
                elif node == 'wall_lever' >= 0:
                    argc += 1
                    varname = "x{:02d}".format(argc)
                    edges[TOP] = varname
                row.append((node, param2, edges))
            if y == 1:
                scheme.append(row)

    W, H = len(scheme[0]), len(scheme)
    print("Scheme {} x {}, lamp located at {}".format(W, H, lamp))


Here each element `scheme[y][x]` is a tuple of the tile name ('and', 
'or', 'lamp', etc.), tile rotation and states of it's *connection 
points* i.e. logical expressions for states of inputs/outputs in top, 
left, right and bottom directions. Initially the only known states are 
the states of `wall_lever`s outputs that are just variable names 
(*symbols*) x01, x02 ... x20. Out goal is to evaluate such expression 
for *lamp* input. It can be done by propagating logical expressions 
through the scheme from one node to it's neighbours and by simulating 
gates functionality. So we need routines `simulate()` and `propagate()`.


    def propagate(x, y):
        _, _, edges = scheme[y][x]
        for (dy, dx), v in edges.items():
            if v is None:
                continue
            yy, xx = y + dy, x + dx
            if xx < 0 or xx >= W or yy < 0 or yy >= H:
                continue
            _, _, adjacent = scheme[yy][xx]
            if adjacent[-dy, -dx] is None:
                adjacent[-dy, -dx] = v

    def simulate(x, y):
        node, p, e = scheme[y][x]
        ret = True
        if node == 'wall_lever':
            pass
        elif node == 'and' and e[LEFT] and e[RIGHT] and e[TOP] is None:
            e[TOP] = "AND({},{})".format(e[LEFT], e[RIGHT])
        elif node == 'nand' and e[LEFT] and e[RIGHT] and e[TOP] is None:
            e[TOP] = "NOT(AND({},{}))".format(e[LEFT], e[RIGHT])
        elif node == 'or' and e[LEFT] and e[RIGHT] and e[TOP] is None:
            e[TOP] = "OR({},{})".format(e[LEFT], e[RIGHT])
        elif node == 'nor' and e[LEFT] and e[RIGHT] and e[TOP] is None:
            e[TOP] = "NOT(OR({},{}))".format(e[LEFT], e[RIGHT])
        elif node == 'xor' and e[LEFT] and e[RIGHT] and e[TOP] is None:
            e[TOP] = "OR(AND({x1},NOT({x1})),AND(NOT({x1}),{x2}))".format(x1=e[LEFT], x2=e[RIGHT])
        elif node == 'not' and e[BOTTOM] and e[TOP] is None:
            e[TOP] = "NOT({})".format(e[BOTTOM])
        elif (node, p) in CONNECTIONS:
            ret = True
            for group in CONNECTIONS[node, p]:
                states = [e[c] for c in group]
                state = reduce(lambda x, y: x or y, states)
                ret = ret and all(states)
                if state and not all(states):
                    for c in group:
                        e[c] = state
        else:
            ret = False
        # is simulation for this node complete and not needed anymore?
        return ret


Now just simulate all meaningful nodes. Much of optimization can be 
done here, but for relatively simple schematics they are unnecessary.

    for_simulation = ['and', 'nand', 'or', 'nor', 'xor', 'not', 'wall_lever'] + \
                     [k[0] for k in CONNECTIONS.keys()]
    to_simulate = [(x, y) for x in range(W) for y in range(H)
                   if scheme[y][x][0] in for_simulation]
    while len(to_simulate) > 0:
        simulated = []
        for x, y in to_simulate:
            if simulate(x, y):
                simulated.append((x, y))
                propagate(x, y)
        for p in simulated:
            to_simulate.remove(p)

    lamp_x, lamp_y = lamp
    _, _, lamp_edges = scheme[lamp_y][lamp_x]
    expr = lamp_edges[BOTTOM]
    print("Boolean expression for LAMP:")
    print(expr)


    $ python solver.py
    Signature: MTSM, version: 1, dimensions: 59 x 2 x 75, body: 35400b
    Names table: ['air', 'stone', 'mesecons_lamp:lamp_off', 'mesecons_walllever:wall_lever_off', 'mesecons_gates:and_off', 'mesecons_gates:nand_off', 'mesecons_gates:nor_off', 'mesecons_gates:not_off', 'mesecons_gates:or_off', 'mesecons_gates:xor_off', 'mesecons_insulated:insulated_off', 'mesecons_extrawires:corner_off', 'mesecons_extrawires:tjunction_off', 'mesecons_extrawires:crossover_off']
    Scheme 59 x 75, lamp located at (1, 74)
    Boolean expression for LAMP:
    AND(AND(AND(AND(AND(x02,NOT(x03)),NOT(OR(x04,x05))),AND(OR(x14,x06),AND(x09,NOT(x01)))),AND(AND(AND(x20,NOT(x18)),NOT(OR(x19,x17))),AND(AND(x07,NOT(x06)),NOT(OR(x16,x08))))),AND(AND(OR(x10,NOT(x02)),AND(OR(x12,NOT(x04)),OR(x02,NOT(x10)))),AND(AND(AND(OR(x05,NOT(x13)),NOT(AND(x11,x03))),AND(OR(x13,NOT(x05)),OR(x04,NOT(x12)))),NOT(OR(OR(AND(x14,x06),AND(x15,x07)),NOT(AND(OR(x15,x07),OR(x11,x03))))))))


At this point is obvious that we need some sort of *solver* that can 
take big formulae of boolean-algebra with propositional variables and 
find all (or any) set of their values that make formulae `true`. With 
python it is very simple using embedded evaluator and backtracking 
approach:

    import re

    varnames = sorted(set(re.findall(r'x\d+', expr)))

    def AND(x,y):
        if x is False or y is False:
            return False
        if x is True and y is True:
            return True

    def OR(x,y):
        if x is False and y is False:
            return False
        if x is True or y is True:
            return True

    def NOT(x):
        if x is False:
            return True
        if x is True:
            return False

    def reduce(values):
        env = [("x{:02d}".format(i), v) for i, v in enumerate(values, 1)] + \
              [("x{:02d}".format(i), None) for i in range(len(values)+1, len(varnames)+1)]
        return eval(expr, globals(), dict(env))

    def backtrack(state):
        if len(state) == len(varnames):
            yield list(zip(varnames, state))
        else:
            for value in [True, False]:
                next_state = state + [value]
                if reduce(next_state) is not False:
                    for res in backtrack(next_state):
                        yield res

    for solution in backtrack([]):
        print(solution)
        binary = "".join(["{:d}".format(value) for (_, value) in solution])
        print(r"CTF{{{}}}".format(binary))


Give it a try:

    $ python solver.py
    Signature: MTSM, version: 1, dimensions: 59 x 2 x 75, body: 35400b
    ....
    [('x01', False), ('x02', True), ('x03', False), ('x04', False), ('x05', False), ('x06', False), ('x07', True), ('x08', False), ('x09', True), ('x10', True), ('x11', True), ('x12', False), ('x13', False), ('x14', True), ('x15', False), ('x16', False), ('x17', False), ('x18', False), ('x19', False), ('x20', True)]
    CTF{01000010111001000001}


Not bad for such dumb simulator/propagator and solver!

**CTF{01000010111001000001}**


But it can be significantly improved. Really, there is no need in 
`eval()`, since evaluation of all logic gates is trivial.
We can reduce `scheme` by removing all `CONNECTION` tiles, implement 
routine for setting known value to known state (like `lamp = True`) and 
then use essentially the same backtracking algorithm for unknown 
inputs.
Complete code is given in `src/Day8.Gate.lock.solver.py`.
It is almost applicable for the *big brother* task from main GoogleCTF 
contest - **minetest** task. On my retro laptop it gives the following 
output:


    $ time python solver.py 
    Total meaningful nodes: 3361
    Total inputs: 40
    Lamp at: (1, 1938)
    [  100] level 21 [ 856 / 3361] 11111111111111111101101011**************
    [  200] level 21 [1706 / 3361] 11111111111111111010101011100011********
    ..........
    [4129900] level 15 [2153 / 3361] 111001010100011000101011111000011*******
    [4130000] level 11 [ 887 / 3361] 1110010101000101111010******************
    [4130100] level 17 [2688 / 3361] 1110010101000101110010111110000110011***
    (4130102, '1110010101000101110010111110000110011001')

    real	204m34.556s
    user	204m30.715s
    sys	0m1.465s

Less than 4 hours on old Core2Duo, without any tricky algorithms or 
optimization hueristics, and with pure python.

**CTF{1110010101000101110010111110000110011001}**

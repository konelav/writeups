#!/usr/bin/python
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
    names.append(name.decode())

body = zlib.decompress(body)

print("Signature: {}, version: {}, dimensions: {} x {} x {}, body: {}b".format(
    signature, version, sizex, sizey, sizez, len(body)))
print("Names table: {}".format(names))

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
            if node == 'lamp':
                lamp = (x, z)
            elif node == 'wall_lever':
                argc += 1
                varname = "x{:02d}".format(argc)
                edges[TOP] = varname
            row.append((node, param2, edges))
        if y == 1:
            scheme.append(row)

W, H = len(scheme[0]), len(scheme)
print("Scheme {} x {}, lamp located at {}".format(W, H, lamp))

from functools import reduce


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
    return ret


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

import re

#expr = "AND(x1, AND(OR(x1, x2), NOT(AND(x3, x1))))"
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

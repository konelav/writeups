#!/usr/bin/python

import struct
import zlib
import pickle

try:
    with open('scheme.txt', 'rb') as f:
        scheme = pickle.loads(f.read())
except:
    scheme = None

LEFT, TOP, RIGHT, BOTTOM = (-1, 0), (0, 1), (1, 0), (0, -1)

if scheme is None:

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

    CONNECTIONS = {
        ('insulated', 0): [[LEFT, RIGHT]],
        ('insulated', 3): [[TOP, BOTTOM]],
        ('corner', 0): [[LEFT, BOTTOM]],
        ('corner', 1): [[LEFT, TOP]],
        ('corner', 2): [[RIGHT, TOP]],
        ('corner', 3): [[RIGHT, BOTTOM]],
        ('crossover', 3): [[LEFT, RIGHT], [TOP, BOTTOM]],
        ('tjunction', 0): [[LEFT, TOP, RIGHT]],
        ('tjunction', 1): [[LEFT, TOP, BOTTOM]],
        ('tjunction', 2): [[RIGHT, LEFT, BOTTOM]],
        ('tjunction', 3): [[RIGHT, TOP, BOTTOM]]
    }

    N = sizez * sizey * sizex
    o0, o1, o2 = 0, N*2, N*3
    scheme = {}
    inputs = []
    for z in range(sizez):
        for y in range(sizey):
            for x in range(sizex):
                if y != 1:
                    o0, o1, o2 = o0 + 2, o1 + 1, o2 + 1
                    continue
                nameid, = struct.unpack('>H', body[o0:o0+2])
                #param1, = struct.unpack('>B', body[o1:o1+1])
                param2, = struct.unpack('>B', body[o2:o2+1])
                o0, o1, o2 = o0 + 2, o1 + 1, o2 + 1
                name = names[nameid]
                node = name[name.find(':')+1:name.rfind('_')]
                edges = {LEFT: None, TOP: None, RIGHT: None, BOTTOM: None}
                scheme[x, z] = node, param2, edges, []
                if node == 'wall_lever':
                    inputs.append((x, z))

    print("Scheme nodes: {}".format(len(scheme)))

    from functools import reduce


    def propagate(x, y):
        ret = []
        _, _, edges, _ = scheme[x, y]
        for (dx, dy), v in edges.items():
            if v is None:
                continue
            xx, yy = x + dx, y + dy
            if (xx, yy) not in scheme:
                continue
            _, _, adjacent, _ = scheme[xx, yy]
            if adjacent[-dx, -dy] is None:
                adjacent[-dx, -dy] = v
                ret.append((xx, yy))
        return ret


    def simulate(x, y):
        global symbols
        node, p, edges, _ = scheme[x, y]
        ret = True
        if node == 'wall_lever':
            if p != 0:
                raise
            edges[TOP] = (x, y)
        elif node == 'not' and edges[BOTTOM] is not None:
            if p != 3:
                raise
            edges[TOP] = (x, y)
            _, _, _, backrefs = scheme[edges[BOTTOM]]
            backrefs.append((x, y))
        elif node in ['and', 'nand', 'or', 'nor', 'xor'] and \
             edges[LEFT] is not None and edges[RIGHT] is not None:
            if p != 3:
                raise
            edges[TOP] = (x, y)
            for d in [LEFT, RIGHT]:
                _, _, _, backrefs = scheme[edges[d]]
                backrefs.append((x, y))
        elif node == 'lamp' and edges[BOTTOM] is not None:
            if p != 1:
                raise
            _, _, _, backrefs = scheme[edges[BOTTOM]]
            backrefs.append((x, y))
        elif (node, p) in CONNECTIONS:
            for group in CONNECTIONS[node, p]:
                states = [edges[c] for c in group]
                state = reduce(lambda x, y: x or y, states)
                ret = ret and all(states)
                if state and not all(states):
                    for c in group:
                        edges[c] = state
        else:
            ret = False
        return ret
    
    next_simulate = set(inputs)
    while True:
        simulated = []
        sim = list(next_simulate)
        next_simulate = set()
        for x, y in sim:
            if (x, y) not in scheme:
                continue
            if simulate(x, y):
                next_simulate.update(propagate(x, y))
            else:
                next_simulate.add((x, y))
        print(len(next_simulate))
        if len(next_simulate) == 0:
            break
    
    to_remove = []
    for k, (node, _, _, _) in scheme.items():
        if node not in ['wall_lever', 'and', 'nand', 'or', 'nor', 'xor', 'not', 'lamp']:
            to_remove.append(k)
    for k in to_remove:
        del scheme[k]
    
    with open('scheme.txt', 'wb') as f:
        f.write(pickle.dumps(scheme))

lamp = None
inputs = []
for k, (node, p, edges, backrefs) in scheme.items():
    if node == 'wall_lever':
        inputs.append(k)
    elif node == 'lamp':
        lamp = k
inputs.sort()

print("Total meaningful nodes: {}".format(len(scheme)))
print("Total inputs: {}".format(len(inputs)))
print("Lamp at: {}".format(lamp))

def AND(result, arg1, arg2):
    if result is True:
        return (True, (True, True))
    if arg1 is False or arg2 is False:
        return (False, (arg1, arg2))
    if arg1 is True and arg2 is True:
        return (True, (arg1, arg2))
    return (result, (arg1, arg2))

def OR(result, arg1, arg2):
    if result is False:
        return (False, (False, False))
    if arg1 is True or arg2 is True:
        return (True, (arg1, arg2))
    if arg1 is False and arg2 is False:
        return (False, (arg1, arg2))
    return (result, (arg1, arg2))

def XOR(result, arg1, arg2):
    if arg1 is not None and arg2 is not None:
        return (arg1 != arg2, (arg1, arg2))
    if result is not None and arg1 is not None:
        return (result, (arg1, result != arg1))
    if result is not None and arg2 is not None:
        return (result, (result != arg2, arg2))
    return (result, (arg1, arg2))

def NOT(result, arg1):
    if result is not None:
        return (result, (not result,))
    if arg1 is not None:
        return (not arg1, (arg1,))
    return (result, (arg1,))

def EQ(result, arg1):
    if result is not None:
        return (result, (result,))
    if arg1 is not None:
        return (arg1, (arg1,))
    return (result, (arg1,))


EXECUTERS = {
    'and': (AND, (LEFT, RIGHT)),
    'or': (OR, (LEFT, RIGHT)),
    'xor': (XOR, (LEFT, RIGHT)),
    'not': (NOT, (BOTTOM,)),
    'lamp': (EQ, (BOTTOM,)),
    'wall_lever': (EQ, (TOP,))
}


def execute(known, k):
    node, _, edges, backrefs = scheme[k]
    executer, args = EXECUTERS[node]
    result = known.get(k, None)
    argvals = [known.get(edges[arg], None) for arg in args]
    result, argvals = executer(result, *argvals)
    to_set = [(k, result)] + [(edges[args[i]], argvals[i]) for i in range(len(args))]
    for key, value in to_set:
        if value is None:
            continue
        if set_state(known, key, value) is False:
            return False
    return True

def set_state(known, k, value):
    if k in known:
        return known[k] == value
    known[k] = value
    node, _, edges, backrefs = scheme[k]
    _, args = EXECUTERS[node]
    for ref in backrefs + [k]:
        if execute(known, ref) is False:
            return False
    return True

def bool2bits(a):
    ret = "".join(["{:d}".format(value) for value in a])
    ret += "*" * (len(inputs) - len(a))
    return ret


import copy

nsteps = 0
def solve(known, needed, rec=0):
    global nsteps, steps_to_contradict
    while True:
        nsteps += 1
        if nsteps % 100 == 0:
            bits = [b for (k, b) in sorted(known.items()) if k in inputs]
            print("[{:5d}] level {:2d} [{:4d} / {:4d}] {}".format(
                nsteps, rec, len(known), len(scheme), bool2bits(bits)))
        for k, v in needed.items():
            if set_state(known, k, v) is False:
                return
        if len(known) == len(scheme):
            return known
        check_k = [k for k in inputs if k not in known][0]
        known_branch = copy.copy(known)
        res = solve(known_branch, {check_k: True}, rec + 1)
        if res is not None:
            return res
        needed = {check_k: False}

solution = solve({}, {lamp: True})
bits = [b for (k, b) in sorted(solution.items()) if k in inputs]
print(nsteps, bool2bits(bits))

#!/usr/bin/python
import vm
import re
to_replace = [(op, method.__name__) for 
              (op, method) in vm.VM.OPERATIONS.items()] + [
              ('💰', 'R'),
              ('🖋', 'L'),
              ('😐', 'endif'),
              ('🥇', 'acc1'),
              ('🥈', 'acc2'),
              ('✋', 'EoN')
             ]
with open('vm.py', 'r') as f:
    contents = f.read()
for op, method in to_replace:
    contents = re.sub(op, method, contents)
with open('new.vm.py', 'w') as f:
    f.write(contents)
to_replace += [(str(d) + r'\S+', str(d)) for d in range(10)]
with open('program', 'r') as f:
    contents = f.read()
for op, method in to_replace:
    contents = re.sub(op, method, contents)
references = re.findall(r'R\S+', contents)
for counter, ref in enumerate(references, 1):
    contents = contents.replace(ref, 'R_{}'.format(counter))
    contents = contents.replace('L'+ref[1:], 'L_{}'.format(counter))
with open('new.program', 'w') as f:
    f.write(contents)

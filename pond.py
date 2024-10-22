#! /usr/bin/python
# SPDX-License-Identifier: Unlicense

# A SD model of a pond filled through a stream controlled by a gate.
# The stream is simulated by a NodeDelay3, and the intention is to
# investigate how a NodeDelay3 works. It's not at all clear to me,
# and the "explanation" in the PDF is just the code expressed with
# math symbols.
#
# To control the gate, re-write f_gate()

import system_dynamic as sd

def load_model(s):
    # Constants
    D = s.addConstant(
        'delay_constant', sd.C, detail='Delay constant', unit="?", val=2)
    F = s.addConstant(
        'flow', sd.C, detail='Max flow through the gate', unit="m3/day", val=10)
    # Stocks and Flows
    gate = s.addFlow(
        "gate", detail="Flow through the gate", unit="m3/day")
    stream = s.addDelay3(
        'stream', detail="Flow through the stream", unit='m3/day')
    pond = s.addStock(
        "pond", detail='Water in the pond', unit="m3", max=100)
    # Equations (edges)
    def f_gate(flow, t):
        #if t >= 2 and t < 4:
        if t >= 2 and t < 4:
            return flow
        return 0
    t = s.nodes['time']
    s.add_equation(f_gate, gate, [F, t])
    s.add_equation(stream.f_delayinit, stream, [gate, D])
    s.add_equation(sd.f_sum, pond, [stream])

import sys    
if __name__ == "__main__":
    s = sd.System(time_step=0.1, time_unit='Day')
    load_model(s)
    if len(sys.argv) > 1:
        s.graphviz(title='pond')
        sys.exit()
    D = s.nodes['delay_constant']
    for c in [0.5, 1, 2, 4, 8]:
        D.val = c
        s.reset()
        s.run(6 + c * 3)
        s.plot(
            "gate", "stream", "pond", title=f'Delay constant {c}', size=(8,4))

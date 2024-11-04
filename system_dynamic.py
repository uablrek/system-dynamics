#############################################################################
# © Copyright French Civil Aviation Authority
# Author: Julien LEGAVRE (2022)
# Contributor: Alexandre GONDRAN

# julien.legavre@alumni.enac.fr
# Updated 2024 by Lars Ekman <uablrek@gmail.com> (@uablrek at github)

# This software is a computer program whose purpose is to produce the results
# of the World3 model described in "The Limits to Growth" and
# in "The Limits to Growth: The 30-Year Update".

# This software is governed by the GNU General Public License version 2.0.
# This software is also governed by the CeCILL license under French law and
# abiding by the rules of distribution of free software. You can use,
# modify and/or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info".

# As a counterpart to the access to the source code and rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty and the software's author, the holder of the
# economic rights, and the successive licensors have only limited
# liability.

# In this respect, the user's attention is drawn to the risks associated
# with loading, using, modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean that it is complicated to manipulate, and that also
# therefore means that it is reserved for developers and experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or
# data to be ensured and, more generally, to use and operate it in the
# same conditions as regards security.

# The fact that you are presently reading this means that you have had
# knowledge of the GNU General Public License version 2.0 or the CeCILL  
# license and that you accept its terms.
#############################################################################

# Updates:
# - Rename class World3->System and simplify
# - Plot and graph functions
# - Boundaries (max, min) in stocks
# - A "sign" used to set +,- on edges (and more) (issue #1)
# - Primitive trace
# - An automatic 'time' stock
# - Attempt to follow Python style (https://peps.python.org/pep-0008/)
# - Create/dump/update from dict
# ...and more

import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter

C = "CONSTANT"
CT = "TABLE OF CONSTANTS"

class NodeAlreadyExistsError(Exception):
    pass

#############################################################################
# Node is a general class from which all types of nodes will take
# arguments.  It has a name, a value, an associated function,
# predecessors, successors and a rank.
#############################################################################

class Node:
    def __init__(self, name, val=None, detail=None, unit=None, cat=None):
        self.name = name
        self.val = val
        self.detail = detail
        self.cat = cat
        self.unit = unit
        self.cons = None  # function to get val. arguments are predecessors
        self.sign = 0     # -1 if this node gives negative feedback ('-')
        self.pred = set()
        self.succ = set()
        self.rank = None  # Sort order on evaluation (computed in set_rank())
        self.trace = False
        self.save = True

    def __repr__(self):
        value = "None"
        if self.val:
            value = "{:.03f}".format(self.val)
        return "{0.name:<8} {3} IN: {1:<20} OUT: {2}".format(self, ",".join(self.get_pred_name()), ",".join(self.get_succ_name()), value)

    # dict() returns a reduced __dict__ used for serialization (json)
    def dict(self):
        d = {'name': self.name}
        if self.cat: d['cat'] = self.cat
        if self.detail: d['detail'] = self.detail
        if self.unit: d['unit'] = self.unit
        return d

    def set_cons(self, f, pred, sign=0):
        self.cons = f
        self.pred = pred
        self.sign = sign
        for p in pred:
            p.succ.add(self)

    def get_pred_name(self):
        return [p.name for p in self.pred]

    def get_succ_name(self):
        return [p.name for p in self.succ]

    def reset(self):
        pass

#############################################################################
# NodeStock is a node which is computed by calculating its derivate.
# It has a historic in order to be able to show its evolution.
#############################################################################
# Has a max and min value. An init val is mandatory
class NodeStock(Node):
    def __init__(
            self, name, val=0, detail=None, unit=None, cat=None,
            max=float('inf'), min=0):
        super().__init__(name, val=val, detail=detail, unit=unit, cat=cat)
        self.max = max
        self.min = min
        self.hist = [val]

    def eval(self, ts):
        # (to check cons allow nodes without predecessors during development)
        if self.cons:
            self.val = self.val + self.cons(*[p.val for p in self.pred]) * ts
        if self.val > self.max:
            self.val = self.max
        if self.val < self.min:
            self.val = self.min
        if self.save:
            self.hist.append(self.val)
        if self.trace:
            print(f'{self.name}: {self.val}')

    def dict(self):
        d = super().dict()
        d['type'] = 'stock'
        if self.max != float('inf'): d['max'] = self.max
        if self.min != 0: d['min'] = self.min
        d['val'] = self.val
        d['hist'] = self.hist
        return d

    def reset(self):
        self.val = self.hist[0]
        self.hist = [self.val]

#############################################################################
# NodeFlow is a node which is computed each time.
# It also has a historic in order to be able to show its evolution.
#############################################################################
# The 'sign' indicate if this is a negative '-', or positive '+' flow
# sign=0 have no effect on the model or the model graph

class NodeFlow(Node):
    def __init__(self, name, detail=None, unit=None, cat=None):
        super().__init__(name, detail=detail, unit=unit, cat=cat)
        self.hist = []

    def eval(self, dt):
        val = self.cons(*[p.val for p in self.pred])
        if val == None:
            self.hist.append(val)
            return
        x = 1 if self.sign >= 0 else -1
        self.val = val * x
        if self.save:
            self.hist.append(self.val * x) # (saved values should be positive)
        if self.trace:
            print(f'{self.name}: {self.val}')

    def dict(self):
        d = super().dict()
        d['type'] = 'flow'
        if self.hist: d['hist'] = self.hist
        return d

    def reset(self):
        self.hist = []

#############################################################################
# NodeDelay3 is a node which is computed each time by using its 2
# previous values.  I1, I2 and I3 are "memory" variables which are
# used in the evaluation of the node value.  It also has a historic in
# order to be able to show its evolution.  Its evaluation requires a
# constant and another node.  f_delayinit is a function in order to
# associate a constant and a node to the NodeDelay3.
#############################################################################
# The constant must be >> time_step

class NodeDelay3(Node):
    def __init__(self, name, val=None, detail=None, unit=None, cat=None):
        super().__init__(name, val=val, detail=detail, unit=unit, cat=cat)
        self.hist = []
        self.cst = None
        self.flow = None
        self.I1 = None
        self.I2 = None
        self.I3 = None

    def eval(self, ts):
        # self.cons is (always?) f_delayinit(), which sets self.cons
        # and self.flow
        self.cons(*[p.val for p in self.pred])
        dl = self.cst / 3
        RT1 = self.I1 / dl
        self.I1 = self.I1 + (self.flow - RT1) * ts
        RT2 = self.I2 / dl
        self.I2 = self.I2 + (RT1 - RT2) * ts
        self.I3 = self.I3 + (RT2 - self.I3 / dl) * ts
        self.val = self.I3 / dl
        if self.save:
            self.hist.append(self.val)
        if self.trace:
            print(f'{self.name}: {self.val}')

    # This is called from self.cons, so 'flow' and 'constant' are
    # *values* (not nodes)
    def f_delayinit(self, flow, constant):
        self.flow = flow
        self.cst = constant
        if self.I1 == None:
            self.I1 = self.I2 = self.I3 = flow * constant / 3

    def dict(self):
        d = super().dict()
        d['type'] = 'delay'
        if self.hist: d['hist'] = self.hist
        return d

    def reset(self):
        self.val = None
        self.hist = []
        self.I1 = self.I2 = self.I3 = None
        
#############################################################################
# NodeConstant is a node which has a fix value.
# It can be a constant (C) or a table of constants (CT).
#############################################################################


class NodeConstant(Node):
    def __init__(self, name, t, val=None, detail=None, unit=None, cat=None):
        super().__init__(name, val=val, detail=detail, unit=unit, cat=cat)
        self.type = t

    def __repr__(self):
        value = "None"
        if self.val is not None:
            if self.type == CT:
                l1 = ",".join([str(x) for x in self.val[0]])
                l2 = ",".join([str(x) for x in self.val[1]])
                value = "[{}]:[{}]".format(l1, l2)
            else:
                value = "{0.val:.03f} ".format(self)
        return "{0.name:<8} {3} IN: {1:<20} OUT: {2}".format(self, ",".join(self.get_pred_name()), ",".join(self.get_succ_name()), value)

    
    def dict(self):
        d = super().dict()
        d['type'] = self.type
        d['val'] = self.val
        return d


#############################################################################
# System Was originally the World3 class. It was modified to allow usage
# as a generic SD class
#############################################################################

class System:
    def __init__(
            self, init_time=0, end_time=10, time_step=1, time_unit="Year"):
        # Add the 'time' stock. It is used for x-axis on plots, and in
        # nodes with time constraints. cat='SYSTEM' is used to filter these
        TS = NodeConstant(
            "TS", C, val=time_step, detail="time step", cat='SYSTEM')
        t = NodeStock(
            "time", val=init_time, detail="time", unit=time_unit, cat='SYSTEM')
        self.add_equation(lambda x: 1, t, [TS], sign=0)
        self.nodes = {'TS':TS, 'time':t}
        self.stocks = [t]
        self.time_unit=time_unit
        self.end_time = end_time
        self.default_cat = None
        self.default_sign = 0

    def __repr__(self):
        return "\n".join([str(v) for c,v in self.nodes.items()])

    def add_node(self, node):
        if node.name in self.nodes:
            print(f'Node {node.name} already exists. Modify the modelling:')
            print(self.nodes[node.name])
            raise NodeAlreadyExistsError()
        self.nodes[node.name] = node

    def addStock(
            self, name, val=0, detail=None, unit=None, cat=None,
            max=float('inf'), min=0):
        if not cat: cat = self.default_cat
        s = NodeStock(
            name, val=val, detail=detail, cat=cat, unit=unit, max=max, min=min)
        self.add_node(s)
        self.stocks.append(s)
        return s

    def addFlow(self, name, detail=None, unit=None, cat=None):
        if not cat: cat = self.default_cat
        f = NodeFlow(name, detail=detail, cat=cat, unit=unit)
        self.add_node(f)
        return f

    def addDelay3(self, name, detail=None, unit=None, cat=None):
        if not cat: cat = self.default_cat
        d = NodeDelay3(name, detail=detail, cat=cat, unit=unit)
        self.add_node(d)
        return d

    def addConstant(self, name, t, val=None, detail=None, unit=None, cat=None):
        if not cat: cat = self.default_cat
        c = NodeConstant(name, t, val=val, detail=detail, cat=cat, unit=unit)
        self.add_node(c)
        return c

    def add_equation(self, f, x_target, x_s, sign=None):
        if sign == None: sign = self.default_sign
        x_target.set_cons(f, x_s, sign)

    def eval(self, ts):
        for ns in self.nodesrank:
            ns.eval(ts)

    def run(self, end_time=None):
        self.set_rank()
        it = self.nodes['time'].hist[0]
        et = end_time if end_time else self.end_time
        ts = self.nodes['TS'].val
        nb_step = int((et - it) / ts)
        for i in range(nb_step):
            self.eval(ts)
        for stock in self.stocks:
            stock.hist.pop() # (since stocks have an init-val)

    #########################################################################
    # sub_graph_vertex: allow to obtain sub-graphs from known values
    # (Constants and initial values of Stocks) # d2: list of node name
    # if node respect the condition d1: dict with node name as key
    # and its place in d2 as value gM: list of lists of predecessors
    # for each node, with the d2 order of node gP: list of lists of
    # successors for each node, with the d2 order of node
    #########################################################################

    def sub_graph_vertex(self, cond):
        d2 = [name for name, n in self.nodes.items() if cond(n)]
        d1 = {name: i for i, name in enumerate(d2)}
        size = len(d2)
        gM = [[] for _ in range(size)]
        gP = [[] for _ in range(size)]
        for name in d2:
            n = self.nodes[name]
            for u in n.pred:
                if cond(u):
                    gM[d1[name]].append(d1[u.name])
                    gP[d1[u.name]].append(d1[name])
        return d2, gM, gP

    #########################################################################
    # set_rank: allow to have the order to follow to solve the graph
    # dM: list of the number of predecessors for each node S0: list
    # of order to evaluate nodes which have no predecessors
    # rank_rec: build the list of order r by recurrence using the
    # first solution S0 nodesrank: list of nodes ordered by priority
    # in the calcul
    #########################################################################

    def set_rank(self):
        d2, gM, gP = self.sub_graph_vertex(
            lambda x: type(x) == NodeDelay3 or type(x) == NodeFlow)
        size = len(d2)
        dM = [len(gi) for gi in gM]
        S0 = [i for i, di in enumerate(dM) if di == 0]
        r = [None] * size

        def rank_rec(Sk, k):
            Sk1 = []
            for i in Sk:
                r[i] = k
                for j in gP[i]:
                    dM[j] -= 1
                    if dM[j] == 0:
                        Sk1.append(j)
            if len(Sk1) > 0:
                return rank_rec(Sk1, k+1)

        rank_rec(S0, 0)
        self.nbrank = max(r) + 1
        self.nodesrank = [
            self.nodes[d2[j]] for _, j in sorted([(ri, i) for i, ri in enumerate(r)])]
        self.nodesrank += self.stocks

    # Plot node histories against time (x-axis)
    def plot_nodes(
            self, nodes, title=None, size=(10,5), pause=0, formatter=None):
        # https://matplotlib.org/stable/gallery/spines/multiple_yaxis_with_spines.html
        # https://matplotlib.org/stable/gallery/text_labels_and_annotations/engineering_formatter.html
        if not nodes:
            return
        fig = plt.gcf()         # (Get Current Figure)
        fig.set_size_inches(size)
        fig.clear()
        if title:
            fig.suptitle(title)
        ax = plt.axes()
        ax.set(xlabel=self.time_unit)
        ax.grid(axis='x', linestyle=':')
        y_offset = 50   # Offset additional Y-axis outward
        if formatter == "eng":
            engfmt = EngFormatter(places=1, sep="\N{THIN SPACE}")
            y_offset = 65
        s = nodes[0]
        if type(s) is tuple:
            s, lim = s
            ax.set_ylim(lim)
        ax.set(ylabel=f'{s.detail} ({s.unit})')
        if formatter == "eng": ax.yaxis.set_major_formatter(engfmt)
        #ax.tick_params(axis='y', rotation=90)
        i = 0
        times = self.nodes['time'].hist
        # The "C0" color used here allows 10 schemes by default
        p, = ax.plot(times, s.hist, f'C{i}')
        ax.yaxis.label.set_color(p.get_color())
        ax.tick_params(axis='y', colors=p.get_color())
        for s in nodes[1:]:
            i = i + 1
            t = ax.twinx()
            if type(s) is tuple:
                s, lim = s
                t.set_ylim(lim)
            t.set(ylabel=f'{s.detail} ({s.unit})')
            if formatter == "eng": t.yaxis.set_major_formatter(engfmt)
            #t.tick_params(axis='y', rotation=90)
            if i > 1:
                t.spines['right'].set_position(("outward", y_offset * (i-1)))
                # (this may make y-axes to overlap, which look ugly)
            p, = t.plot(times, s.hist, f'C{i}')
            t.yaxis.label.set_color(p.get_color())
            t.tick_params(axis='y', colors=p.get_color())
        fig.tight_layout()
        if pause > 0:
            plt.pause(pause)
        else:
            plt.show()
    # plot_stocks Is a quick an simple way to plot all stocks
    def plot_stocks(self, exclude=['SYSTEM'], title=None, size=(10,5)):
        self.plot_nodes(
            list(filter(lambda s: s.cat not in exclude, self.stocks)),
            title=title, size=size)
    # plot Plot named nodes
    def plot(
            self, *nodenames, title=None, size=(10,5), pause=0, formatter=None):
        """Plot named nodes.

        Parameters
        ----------
        nodenames: str or tuple
            Nodes to plot. May be a tuple with an ylimit, example
            ('pop', (0,10e9))
        title: str, optional
            Figure title
        size: tuple (w,h), default (10,5)
            Size of the figure (inches)
        pause: int, default 0 (infinite)
            Time that the figure is shown, and this function returns.
            This can be used to create a simple animation. If you want
            the window to stay open, call matplotlib.pyplot.show()
        """
        l = []
        for x in nodenames:
            if type(x) is tuple:
                x, lim = x
                l.append((self.nodes[x], lim))
            else:
                l.append(self.nodes[x])
        self.plot_nodes(
            l, title=title, size=size, pause=pause, formatter=formatter)

    # Generate model graph
    def emit_node(self, n):
        if type(n) == NodeStock:
            shape="box"
        elif type(n) == NodeFlow:
            shape="ellipse"
        elif type(n) == NodeDelay3:
            shape="Mcircle"
        else:
            return
        print(f'{n.name} [shape={shape} label={n.name} tooltip="{n.detail} ({n.unit})"]')
        c = ""
        for s in n.pred:
            if type(s) == NodeConstant:
                c += f'{s.detail} = {s.val} {s.unit}\\n'
        if c != "":
            print(f'{n.name}_c [shape=plain label="const" tooltip="{c}"]')
            print(f'{n.name}_c -> {n.name} [arrowhead=none]')
    def graphviz_cat(self, cat=None):
        if not cat:
            for _,n in self.nodes.items():
                if not n.cat:
                    self.emit_node(n)
            return
        print(f'subgraph cluster_{cat} {{')
        print(f'label="{cat}"')
        print('pencolor=lightgrey')
        for _,n in self.nodes.items():
            if n.cat == cat:
                self.emit_node(n)
        print('}')
    def graphviz(self, title="system", exclude=['SYSTEM']):
        print(f'digraph "{title}" {{')
        for cat in self.categories(exclude):
            self.graphviz_cat(cat)
        for _,n in self.nodes.items():
            if type(n) == NodeConstant:
                continue
            if n.cat in exclude:
                continue
            for s in n.get_succ_name():
                if n.sign == 0:
                    print(f'{n.name} -> {s}')
                else:
                    l = '+' if n.sign > 0 else '-'
                    print(f'{n.name} -> {s} [label="{l}"]')
        print('}')

    def categories(self, exclude=['SYSTEM']):
        c = set()
        for _,n in self.nodes.items():
            if n.cat not in exclude:
                c.add(n.cat)
        return c

    # reset Reset all nodes for a new iteration
    def reset(self):
        for _,n in self.nodes.items():
            n.reset()

    # Set trace on nodes
    def trace(self, *nodes):
        for n in nodes:
            self.nodes[n].trace = True
    # Set history save on nodes
    def history(self, save, *nodes):
        for n in nodes:
            self.nodes[n].save = save

    # dict Returns a reduced __dict__ used for serialization (json)
    def dict(self):
        return {
            'time_unit': self.time_unit,
            'nodes': [n.dict() for _,n in self.nodes.items()]}
    # dict_nodes Returns a reduced __dict__ for selected nodes. It is
    # intended for generating data for post-processing
    def dict_nodes(self, *nodenames):
        return {
            'time_unit': self.time_unit,
            'nodes': [self.nodes[x].dict() for x in nodenames]}

    # load Load nodes from a dict (I can't see a valid use-case at the moment)
    def load(self, d):
        def is_attribute(k):
            return k != 'name' and k != 'type' and k != 'hist'
        for n in d['nodes']:
            if 'cat' in n and n['cat'] == 'SYSTEM':
                # These are auto-generated and will cause a conflict
                continue
            # (filter() is a tiny bit slower, and less readable IMHO)
            kw = {k: v for k, v in n.items() if is_attribute(k)}
            name = n['name']
            match n['type']:
                case 'stock':
                    self.addStock(name, **kw)
                case 'flow':
                    self.addFlow(name, **kw)
                case 'delay':
                    self.addDelay3(name, **kw)
                case str(CT):
                    self.addConstant(name, CT, **kw)
                case str(C):
                    self.addConstant(name, C, **kw)

    # update Updates nodes from a dict. It is intended for iterations
    # with different values. Only constants and stocks are updated
    def update(self, d):
        for n in d['nodes']:
            name = n['name']
            if name not in self.nodes:
                continue
            node = self.nodes[name]
            match n['type']:
                case 'stock':
                    node.val = node.hist[0] = n['val']
                case str(CT):
                    node.val = n['val']
                case str(C):
                    node.val = n['val']

def __plot_node(i, times, ax, n, y_offset=65, formatter=None, add=False):
    if add:
        if type(n) is tuple:
            n, _ = n
        ax.plot(times, n.hist, f'C{i}--', linewidth=0.5)
        return
    if type(n) is tuple:
        n, lim = n
        ax.set_ylim(lim)
    p, = ax.plot(times, n.hist, f'C{i}')        
    if formatter:
        ax.yaxis.set_major_formatter(formatter)
    ax.set(ylabel=f'{n.detail} ({n.unit})')
    if i > 1:
        ax.spines['right'].set_position(("outward", y_offset * (i-1)))
    ax.yaxis.label.set_color(p.get_color())
    ax.tick_params(axis='y', colors=p.get_color())
def __get_node(s, n):
    if type(n) is tuple:
        n, lim = n
        return (s.nodes[n], lim)
    else:
        return s.nodes[n]

# Plot nodes from different system runs
def plot_nodes(
        s1, s2, nodes=[], title=None, size=(10,5), formatter="eng"):
    if not nodes:
        return
    engfmt=None
    if formatter == "eng":
        engfmt = EngFormatter(places=1, sep="\N{THIN SPACE}")
    fig = plt.gcf()         # (Get Current Figure)
    fig.set_size_inches(size)
    fig.clear()
    if title:
        fig.suptitle(title)
    ax = plt.axes()
    ax.set(xlabel=s1.time_unit)
    ax.grid(axis='x', linestyle=':')
    times = s1.nodes['time'].hist
    i = 0
    n = nodes[0]
    __plot_node(i, times, ax, __get_node(s1, n), formatter=engfmt)
    __plot_node(i, times, ax, __get_node(s2, n), add=True)
    for n in nodes[1:]:
        i = i + 1
        t = ax.twinx()
        __plot_node(i, times, t, __get_node(s1, n), formatter=engfmt)
        __plot_node(i, times, t, __get_node(s2, n), add=True)
    fig.tight_layout()
    plt.show()


# Common functions used in equations
def f_sum(*l):
    return sum([float(i) for i in l])
def f_mul(val, rate):
    return val * rate
def f_clip(c1, c2, ts, t):
    if t <= ts : return c1
    else : return c2
# Interpolate a value from a "TABLE OF CONSTANTS" (CT)
def f_tab(tab, x):
    if x < tab[0][0]:       # lower than first
        return tab[0][1]
    if x > tab[-1][0]:      # higher than last
        return tab[-1][1]
    else:
        i = 0
        while i < len(tab):
            if tab[i][0] <= x <= tab[i+1][0]:
                coeff = (tab[i+1][1]-tab[i][1]) / (tab[i+1][0]-tab[i][0])
                return tab[i][1] + coeff * (x-tab[i][0])
            i += 1
# f_tabclip Return None for values out-of-bounds. Use for instance for
# empirical data that ends in the current year
def f_tabclip(tab, x):
    if x < tab[0][0] or x > tab[-1][0]:
        return None   # out-of-bounds
    else:
        i = 0
        while i < len(tab):
            if tab[i][0] <= x <= tab[i+1][0]:
                coeff = (tab[i+1][1]-tab[i][1]) / (tab[i+1][0]-tab[i][0])
                return tab[i][1] + coeff * (x-tab[i][0])
            i += 1

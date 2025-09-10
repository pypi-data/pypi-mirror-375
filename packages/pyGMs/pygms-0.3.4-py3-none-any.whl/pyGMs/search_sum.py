# Search-based algorithms
#

import numpy as np
import networkx as nx
import time as time
import heapq
from .factor import *
from .misc import *
from .wmb import *
from .wogm import *


FLOAT_MAX = 1e308

"""
Search algos:
  local greedy search; local greedy + stochastic search; local stochastic search
  depth first B&B
  A*
  RBFS?
  ...
"""


# TODO: 
#  (1) Verbose flag in search?
#  (2) Search method: current tree to graph 
#  (3) Search method: update graph on the fly? (node: expand order #, config, bound value)
#  (4) Graph layout function
#



class NodeDFS(object):
  def __init__(self,parent,X=None,x=None,val=-inf):
    self.parent = parent
    self.children = []
    #self.priority = -inf
    self.value = val
    self.heuristic = None
    self.X = X
    self.x = x   # node is for assignment X=x given ancestor assigments
  def __hash__(self):
    return hash(id(self))
  def __eq__(self,other):
    return id(self)==id(other);
  def cfg(self):
    x_ = {} if self.parent is None else self.parent.cfg(); x_[self.X]=self.x; return x_


class PrunedDFS(object):
  """Depth-first search using pruning."""
  def __init__(self, model, heuristic, elim='max', xinit={}, retain_graph=False):
    self.model = model
    self.heuristic = heuristic
    if len(xinit): self.xhat = xinit; self.L = model.logValue(xinit) # use initial config
    else:          self.xhat = {};    self.L = -inf
    self.elim = elim            # can be a string or a map[X->str]
    self.root = NodeDFS(None);
    self.node = self.root
    self.root.heuristic = heuristic
    self.cfg = {}
    self.searchGraph = None if not retain_graph else nx.DiGraph()
    if self.searchGraph is not None: self.searchGraph.add_node(self.root, status='generate')

  def __elim(X):
      return self.elim if isinstance(self.elim,str) else self.elim[X]

  def done(self):
    return self.node is None

  # def upperbound(self): = max(self.L,max([n.value for n in self.node to root]))
  # def lowerbound(self): = self.L

  def __next(self,n):
    """Helper to return next node in DFS queue"""
    while n is not None:
      if n.children and not self.prune(n.children[-1]):
        n = n.children.pop()            # if we can move downward, do so;
        if self.searchGraph: self.searchGraph.nodes[n]['status'] = 'expand' # add n & (pa,n) to searchgraph / mark expand?
        break
      else:                             # otherwise, move to parent/sibling
        self.cfg.pop(n.X,None) 
        if self.searchGraph: self.searchGraph.nodes[n]['status'] = 'closed' # mark n as closed in searchgraph
        n = n.parent
    if n is not None: self.cfg[n.X] = n.x;
    return n, self.cfg
        
  def isLeaf(self,n): 
    return len(self.cfg) == self.model.nvar  # config for all variables => done (or-tree)

  def prune(self,n):
    return n.value <= self.L            # value (upper bound) no better than current soln

  def run(self, stopNodes=inf, stopTime=inf, verbose=False):
    nnodes = 0; stopTime += time.time();           # initialize stopping criteria
    while not self.done() and nnodes<stopNodes and time.time()<stopTime:
        nnodes += 1; n = self.node;

        if verbose: print(f'  {d2s(self.cfg,self.model.X)} - {n.value}')
        if self.isLeaf(n):              # for leaf nodes, can evaluate score directly
          n.value = self.model.logValue(self.cfg); 
          if n.value > self.L:          #    MPE-specific! TODO
            self.L = n.value; 
            self.xhat = self.cfg.copy(); 
            if verbose: print("[{}]".format(self.L),[self.xhat[v] for v in self.model.X])
        else:                          # else, update heuristic given n.X = n.x
          n.heuristic, n.value = n.heuristic.update(self.cfg,n.X,n.x)

        if not self.prune(n):           # if not pruned, expand n & generate children:
          X,vals = n.heuristic.next_var(self.cfg,n.X,n.x)
          idx = np.argsort(vals)
          n.children = [NodeDFS(n,X,i,vals[i]) for i in idx]
          for c in n.children: c.heuristic = n.heuristic   # point to previous heuristic
          if self.searchGraph:          # add generated nodes to the search graph if tracked
              self.searchGraph.add_nodes_from([(c,{'status':'generate'}) for c in n.children])
              self.searchGraph.add_edges_from([(n,c) for c in n.children])

        # Now move on to the next node in the queue
        self.node, self.cfg = self.__next(n) 

  def graph(self):
      return self.searchGraph


def logsumexp(*args):
  tmp = np.array(list(*args)); mx=tmp.max(); tmp-=mx; mx+=np.log(np.sum(np.exp(tmp))); return mx;

def cfg2str(cfg,X):
  return ''.join(str(cfg[i]) if i in cfg else '-' for i in X);

class NodeAStar(object):
  def __init__(self,parent,X=None,x=None,val=-inf):
    self.parent = parent
    self.children = []
    self.priority = val
    self.value = val
    self.heuristic = None
    self.X = X
    self.x = x   # node is for assignment X=x given ancestor assigments

class AStar(object):
  """A-Star heuristic search """
  def __init__(self, model, heuristic, weights='max', xinit={}):
    self.model = model
    self.heuristic = heuristic
    if len(xinit): self.xhat = xinit; self.L = model.logValue(xinit) # use initial config
    else:          self.xhat = {};    self.L = -inf
    #if   weights == 'max': self.weights = [0.0 for X in model.X]
    #elif weights == 'sum': self.weights = [1.0 for X in model.X]
    #else:                  self.weights = weights
    self.root = NodeAStar(None, None,None,inf);
    self.node = self.root
    self.root.heuristic = heuristic
    self.cfg = {}                    # storage for partial configuration of self.node

  def done(self,):
    return self.node is None

  # def upperbound(self): = self.root.value
  # def lowerbound(self): = self.L ( = -inf if not done )

  def __next(self,n):
    """Helper to return next node in priority queue"""
    # First, travel from n to the root, updating the parent's priority & the children's ordering
    while n.parent is not None: 
      heapq.heapreplace(n.parent.children, (-n.priority, n))
      n = n.parent
      if n.value == n.children[0][1].value: break;  # didn't change value => stop propagating
      #n.value = min(n.value, max(ch[1].value for ch in n.children))      # for MAP search
      n.value = min(n.value, logsumexp(ch[1].value for ch in n.children)) # for SUM search
      n.priority = n.children[0][1].priority   # priority is priority of highest child
   
    n = self.root                           # now find highest priority leaf:
    cfg = {}
    while n.children: 
      n = n.children[0][1]  # follow top priority child downward
      cfg[n.X] = n.x        # and track the associated configuration
    print(self.root.value, self.root.priority, " => ", cfg2str(cfg,self.model.X))
    return n, cfg
         
  def isLeaf(self,n):
    return len(self.cfg) == self.model.nvar  # config for all variables => done (or-tree)

  def run(self, stopNodes=inf, stopTime=inf, verbose=False):
    nnodes = 0; stopTime += time.time();           # initialize stopping criteria
    while not self.done() and nnodes<stopNodes and time.time()<stopTime:
        nnodes += 1; n = self.node;
        if n.priority == -inf: self.node=None; break;

        if self.isLeaf(n):              # for leaf nodes, can evaluate score directly
          n.value = self.model.logValue(self.cfg);
          n.priority = -inf
          self.xhat = self.cfg.copy()   #    MPE-specific! TODO
          if verbose: print("[{}]".format(n.value),[self.xhat[v] for v in self.model.X])
          #self.node, self.cfg = self.__next(n)  # go to next node; if it's this node, we're done!
          #if self.node == n: self.node = None; break;     # TODO: hacky
        else:                          # else, update heuristic given n.X = n.x
          n.heuristic, n.value = n.heuristic.update(self.cfg,n.X,n.x)
          X,vals = n.heuristic.next_var(self.cfg,n.X,n.x)
          idx = np.argsort(vals)
          n.children = [(-vals[i],NodeAStar(n,X,i,vals[i])) for i in idx]
          heapq.heapify(n.children)
          for c in n.children: c[1].heuristic = n.heuristic   # point to previous heuristic
          n.priority = n.children[0][1].priority 

        # Now move on to the next node in the queue
        self.node, self.cfg = self.__next(n)
        #print(" => ",self.cfg)



"""
Search Heuristics should have two functions:
  new_heuristic, node_value = Heuristic.update( config, Var, val )
    config: map or list with current partial configuration
    Var,val: most recent assignment Var=val 
    new_heuristic : copy of new heuristic if dynamic; pointer to old if not
    node_value : updated heuristic value of configuration

  Var,scores = Heuristic.next_var(config,Var,val)
    Return next variable to expand & preliminary heuristic of its values for ordering
    (simplest: return all children of Var with update()'s value for all
"""

from abc import ABC, abstractmethod

class SearchHeuristic(ABC):
  @abstractmethod
  def update(self, config, Xi, xi): pass
  @abstractmethod
  def next_var(self, config, Xi, xi): pass
  # TODO: "undo" update? Sometimes possible, sometimes not (CSPs vs non, for ex)
  #   note: without "undo", nodes keep track of their heuristics & we copy them; with undo, the heur keeps track of what's needed

################################################################################
class Blind(SearchHeuristic):
  """Trivial search heuristic: fixed order (default 0..n-1), h(x)=big-float for all x"""
  def __init__(self,model,*args,**kwargs):
    """Construct trivial search heuristic.
      Args: order (list[int]): fixed order for search
    """
    self.model = model if model.isLog else model.copy().toLog()
    try:    self.pri = [-kwargs['order'].index(i) for i in range(len(model.X))]
    except: self.pri = len(model.X) - np.arange(len(model.X))

  def update(self,config,Xi,xi):
    """Update heuristic from partial configuration <config> by assigning Xi=xi"""
    return self, FLOAT_MAX

  def next_var(self,config,Xi,xi):
    """Select next variable to assign in search from partial configuration <config> & estimate values"""
    X = max( [(self.pri[X],X) for X in self.model.X if X not in config] )[1]
    val = np.zeros(X.states)+FLOAT_MAX
    return X, val  


################################################################################
class SimpleMAP(SearchHeuristic):
  def __init__(self,model,*args,**kwargs):
    self.model = model if model.isLog else model.copy().toLog()
    try:    self.pri = [-kwargs['order'].index(i) for i in range(len(model.X))]
    except: self.pri = len(model.X) - np.arange(len(model.X))

  def update(self,config,Xi,xi):
    bound = sum(( f.condition(config).max() for f in self.model.factors ))
    return self,bound

  def next_var(self,config,Xi,xi):
    X = max( [(self.pri[X],X) for X in self.model.X if X not in config] )[1]
    val = sum(( f.condition(config).maxmarginal([X]) for f in self.model.factors ))
    val = val.table #1*(val.table > -10000)
    return X, val  



################################################################################
class WmbStatic(object):
  """Static heuristic function based on a (weighted) minibucket bound"""
  def __init__(self, model, *args, **kwargs):
    self.wmb = WMB(model,*args,**kwargs);
    self.bound = self.wmb.msgForward(1.0,0.1)
    self.wmb.initHeuristic()

  def update(self, config, Xi, xi):
    """Condition the heuristic on new assignment Xi=xi (no effect for static heuristic)"""
    if Xi is None: return self, self.bound
    return self, self.wmb.resolved(Xi,config)+self.wmb.heuristic(Xi,config)

  def next_var(self, config, Xi, xi):
    """Select next unassigned variable & preliminary scores for ordering"""
    p = self.wmb.priority[Xi] if Xi is not None else self.wmb.model.nvar
    X = self.wmb.X[self.wmb.elimOrder[p-1]] if p else None
    vals = []
    for x in range(X.states):   # TODO: SLOW
      config[X] = x
      vals.append( self.wmb.resolved(X,config)+self.wmb.heuristic(X,config) )
    config.pop(X)
    return X, vals


################################################################################
class WmbDynamic(object):
  """Dynamic heuristic function based on a (weighted) minibucket bound"""
  def __init__(self, model, *args, **kwargs):
    self.wogm = WOGraphModel(model.factors,*args,isLog=model.isLog,**kwargs)
    self.wogm.init()
    self.wogm.update(stopIter=2,stopTime=1.0)
    self.bound = self.wogm.factors[0][0]
    #self.wmb = WMB(model,*args,**kwargs);
    #self.bound = self.wmb.msgForward(1.0,0.1)
    #self.wmb.initHeuristic()

  def update(self, config, Xi, xi):
    """Condition the heuristic on new assignment Xi=xi"""
    if Xi is None: return self, self.bound 
    else: 
      H = WmbDynamic( self.wogm, elimOrder = self.wogm.elimOrder, weights=self.wogm.weights )
      H.wogm.condition({Xi:xi})   # TODO: make more streamlined
      H.wogm.update(stopIter=2,stopTime=1.0)
      return H, H.wogm.factors[0][0]
      #model = self.wmb.model.copy()
      #model.condition({Xi:xi})
      #H = WmbDynamic(model,self.wmb.elimOrder,iBound=1,weights=self.wmb.weights)
      #return H,H.bound

  def next_var(self, config, Xi, xi):
    """Select next unassigned variable & preliminary scores for ordering"""
    X = None
    scores = [ inf if X in config else self.wogm.v_beliefs[X].entropy() for X in self.wogm.X ]
    #scores = [ inf if X in config else -len(self.wogm.factorsWith(X)) for X in self.wogm.X ]
    X = np.argmin(scores)
    vals = self.wogm.costtogo(X).table
    return X, vals
    #for xi in self.wmb.X: 
    #  if xi not in config: X=xi
    #vals = [ self.bound for i in range(X.states) ] if X is not None else []
    #return X,vals



################################################################################
class SimpleStatic(object):
  """Trivial heuristic function for MAP or CSP search"""
  def __init__(self,model,*args,**kwargs):
    self.model = model if model.isLog else model.copy().toLog()

  def update(self,config,Xi,xi):
    bound = sum(( f.condition(config).max() for f in self.model.factors ))
    return self,bound

  def next_var(self,config,Xi,xi):
    X = max( [(len(self.model.factorsWith(X,copy=False)),X) for X in self.model.X if X not in config] )[1]
    val = sum(( f.condition(config).maxmarginal([X]) for f in self.model.factors ))
    return X, val.table




################################################################################
def __draw(self):
    """Lay out and draw a search tree computed via search.
    Returns the networkx DiGraph of the search tree, along with positions & labels (?)
    """
    import networkx as nx
    pos,labels = {},{}
    roots = []
    G = nx.DiGraph()
    for i,b in enumerate(self.buckets):
        for j,mb in enumerate(b):
            G.add_node(str(mb))
            pos[str(mb)] = (j,-i)
            labels[str(mb)] = str(mb)
    for i,b in enumerate(self.buckets):
        for j,mb in enumerate(b):
            if mb.parent is not None: G.add_edge(str(mb),str(mb.parent))
            else: roots.append(mb)
    # Revise x-positions to respect descendent positions
    def _revise(self, root, w=1., x=0.5, pos=None, par=None):
        if type(root) is list: children = root
        else:
            pos[str(root)] = (np.round(x,4), pos[str(root)][1])
            children = root.children
        if len(children):
            dx = w/(len(children))
            x_ = x - w/2 - dx/2
            for ch in children:
                x_ += dx
                pos = _revise(self,ch, w=dx, x=x_, pos=pos, par=root)
        return pos
    pos = _revise(self,roots,pos=pos)

    # Now revise x-positions more uniformly
    xvals = np.unique([pos[p][0] for p in pos])
    xmap = {x:i*1./len(xvals) for i,x in enumerate(xvals)}
    for p in pos: pos[p]=(xmap[pos[p][0]],pos[p][1])

    nx.draw(G, pos=pos, labels=labels)
    return G



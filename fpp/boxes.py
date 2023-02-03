import numpy as np
from copy import copy
from itertools import product

from bisect import bisect_left, bisect_right
from graph import LineGraph

class Box:

    def __init__(self, l, u):

        self.d = len(l)
        self.l = np.array(l)
        self.u = np.array(u)
        assert all(self.u >= self.l)
        self.c = (self.l + self.u) / 2

    def intersect(self, box):
        l = np.maximum(box.l, self.l)
        u = np.minimum(box.u, self.u)

        return Box(l, u)

    def constrain(self, x, tol=0):

        eq = self.u <= self.l + tol
        ineq = np.logical_not(eq)

        constraints = []
        if sum(eq) > 0:
            constraints.append(x[eq] == self.l[eq])
        if sum(ineq) > 0:
            constraints.append(x[ineq] >= self.l[ineq])
            constraints.append(x[ineq] <= self.u[ineq])

        return constraints

    def contains(self, x, tol=0):

        return all(x - self.l >= - tol) and all(x - self.u <= tol)

    def plot2d(self, label=None, **kwargs):

        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle
        assert self.d == 2
        options = {'fc':'lightcyan', 'ec':'k'}
        options.update(kwargs)
        diag = self.u - self.l
        rect = Rectangle(self.l, *diag, **options)
        plt.gca().add_patch(rect)

        if label is not None:
            plt.text(*self.c, label, va='center', ha='center')

    def plot3d(self, vis, name, color=(1,0,0), opacity=1):

        assert self.d == 3
        vis.box(name, self.l, self.u, color, opacity)


class BoxCollection:
    def __init__(self, boxes):

        self.boxes = boxes
        self.n = len(boxes)
        self.d = boxes[0].d

        self.ls = np.array([box.l for box in boxes]).T
        self.us = np.array([box.u for box in boxes]).T
        self.orders = np.zeros((self.d, 2, self.n), dtype=int)
        self.orders_inv = np.zeros((self.d, 2, self.n), dtype=int)

        sort = lambda values: zip(*sorted(zip(values, range(self.n))))
        for i in range(self.d):
            self.ls[i], self.orders[i, 0] = sort(self.ls[i])
            self.us[i], self.orders[i, 1] = sort(self.us[i])
            self.orders_inv[i, 0] = np.argsort(self.orders[i, 0])
            self.orders_inv[i, 1] = np.argsort(self.orders[i, 1])

        self._inters = None

    def contain(self, x, tol=0, subset=...):

        x = np.array(x)
        box_indices = self._icontain(0, x[0], tol, subset)
        for i in range(1, self.d):
            box_indices = box_indices & self._icontain(i, x[i], tol, subset)

        return box_indices

    def _ilcontain(self, i, xi, tol=0, subset=..., first=0):
        '''Returns the indices of the boxes whose lower value in the ith
        dimension is smaller than or equal to the given value xi.'''

        if subset != Ellipsis:
            subset = sorted(self.orders_inv[i, 0, subset]) # How to avoid sorting here?

        last = bisect_right(self.ls[i, subset], xi + tol, lo=first)

        return set(self.orders[i, 0, subset][first:last])

    def _iucontain(self, i, xi, tol=0, subset=...):
        '''Returns the indices of the boxes whose upper value in the ith
        dimension is greater than or equal to the given value xi.'''

        if subset != Ellipsis:
            subset = sorted(self.orders_inv[i, 1, subset]) # How to avoid sorting here?

        first = bisect_left(self.us[i, subset], xi - tol)

        return set(self.orders[i, 1, subset][first:])

    def _icontain(self, i, xi, tol=0, subset=...):
        '''Returns the indices of the boxes whose projection onto the ith axis
        contains to the given value xi.'''

        box_indices_l = self._ilcontain(i, xi, tol, subset)
        box_indices_u = self._iucontain(i, xi, tol, subset)

        return box_indices_l & box_indices_u

    @property
    def inters(self, tol=0):

        if self._inters is not None:
            return self._inters

        self._inters = self._iintersections(0, tol)
        for i in range(1, self.d):
            for k, box_indices in self._iintersections(i, tol).items():
                self._inters[k] = self._inters[k] & box_indices
            
        return self._inters

    def _iintersections(self, i, tol=0):
        
        inters = {k: set() for k in range(self.n)}
        for l, k in enumerate(self.orders[i, 0]):
            xi = self.boxes[k].u[i]
            for m in self._ilcontain(i, xi, tol, first=l+1):
                inters[k].add(m)
                inters[m].add(k)

        return inters

    def line_graph(self, points='centers'):

        return LineGraph(self, points)

    def plot2d(self, subset=None, label=None, frame_ratio=50, **kwargs):
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle

        plot_box = np.array([plt.gca().get_xlim(), plt.gca().get_ylim()]).T
        for i, box in enumerate(self.boxes):
            if subset is None or i in subset:
                label_i = label if label is None else str(i)
                box.plot2d(label=label_i, **kwargs)
                plot_box[0] = np.minimum(plot_box[0], box.l)
                plot_box[1] = np.maximum(plot_box[1], box.u)

        frame = min(plot_box[1] - plot_box[0]) / frame_ratio
        plot_box[0] -= frame
        plot_box[1] += frame
        plt.xlim(plot_box[:, 0])
        plt.ylim(plot_box[:, 1])

    def plot3d(self, vis, name, color=(1,0,0), opacity=1, subset=None):

        for i, box in enumerate(self.boxes):
            if subset is None or i in subset:
                box.plot3d(vis, name + '_' + str(i), color, opacity)

    @staticmethod
    def generate_uniform(d, n, sides, seed=0):

        np.random.seed(seed)
        sides = copy(sides)
        boxes = []
        for _ in range(n):
            c = np.random.rand(d)
            np.random.shuffle(sides)
            diag = np.multiply(np.random.rand(d), sides)
            boxes.append(Box(c - diag, c + diag))
            
        return BoxCollection(boxes)

    @staticmethod
    def generate_grid(d, n, sides, seed=0):

        np.random.seed(seed)
        sides = copy(sides)
        boxes = []
        for c in product(*[range(n) for _ in range(d)]):
            np.random.shuffle(sides)
            diag = np.multiply(np.random.rand(d), sides)
            boxes.append(Box(c - diag, c + diag))
            
        return BoxCollection(boxes)

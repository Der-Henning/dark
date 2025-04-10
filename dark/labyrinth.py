from __future__ import annotations

import random


class Cell:
    def __init__(self, position: tuple[int, int]):
        self.position = position
        self.edges = set([
            Edge(position, (position[0] + 1, position[1])),
            Edge(position, (position[0], position[1] + 1)),
            Edge((position[0], position[1] + 1), (position[0] + 1, position[1] + 1)),
            Edge((position[0] + 1, position[1]), (position[0] + 1, position[1] + 1))
        ])
        self.set: set[Cell] = set()
        self.set.add(self)

    def __hash__(self):
        return hash(self.position)
    
    def __eq__(self, other: Cell):
        return self.position == other.position

    def __repr__(self):
        return f"Cell({self.position})"


class Edge:
    def __init__(self, start: tuple[int, int], end: tuple[int, int]):
        self.start = start
        self.end = end
        self.set = set()
        self.set.add(self)
        self.cells: list[Cell] = list()

    def __hash__(self):
        return hash((self.start, self.end))

    def __eq__(self, other: Edge):
        return (self.start, self.end) == (other.start, other.end)

    def __repr__(self):
        return f"Edge({self.start}, {self.end})"
    

class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.reset()

    def reset(self):
        self.edges: dict[Edge, list[Cell]] = dict()
        for x in range(self.width):  
            for y in range(self.height):
                cell = Cell((x, y))
                for edge in cell.edges:
                    self.edges.setdefault(edge, list()).append(cell)

    def __repr__(self):
        return f"Grid({self.width}, {self.height})"
    

class Labyrinth:
    def __init__(self, width: int, height: int):
        self.grid = Grid(width, height)

    def generate(self) -> list[Edge]:
        self.grid.reset()
        edges = list(self.grid.edges.keys())
        new_edges: list[Edge] = []
        random.shuffle(edges)

        while edges:
            edge = edges.pop()
            
            if len(self.grid.edges[edge]) < 2:
                new_edges.append(edge)
                continue

            cell1 = self.grid.edges[edge][0]
            cell2 = self.grid.edges[edge][1]

            if cell1.set != cell2.set:
                for cell in cell1.set.copy():
                    cell.set.update(cell2.set)  
                for cell in cell2.set.copy():
                    cell.set.update(cell1.set)
            else:
                new_edges.append(edge)
            
        return new_edges

    def __repr__(self):
        return f"Labyrinth({self.grid})"

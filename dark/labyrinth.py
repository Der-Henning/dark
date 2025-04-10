from __future__ import annotations

import random


class Cell:
    def __init__(self, position: tuple[int, int]):
        """Initialize new cell.
        
        Create all surrounding edges.
        Create an empty set of all connected cells and add self.
        """
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
        """Initialize Grid.
        
        Create width x height cells and create all edges.
        For each edge store the adjacent cells in a dictionary.
        """
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
        """Generate Labyrinth by removing random edges of a grid until all cells are connected.
        """
        # Initialize Grid
        self.grid.reset()
        edges = list(self.grid.edges.keys())
        new_edges: list[Edge] = []

        # Schuffle edges
        random.shuffle(edges)

        # iterate over all edges and remove them form the original set until its empty.
        while edges:
            edge = edges.pop()
            
            # When edge is a border edge, add it to final set
            if len(self.grid.edges[edge]) < 2:
                new_edges.append(edge)
                continue

            cell1 = self.grid.edges[edge][0]
            cell2 = self.grid.edges[edge][1]

            # When adjacent cells of the edge are not connected remove edge (dont add to final set)
            # and update the sets of all newly connected cells.
            if cell1.set != cell2.set:
                for cell in cell1.set.copy():
                    cell.set.update(cell2.set)  
                for cell in cell2.set.copy():
                    cell.set.update(cell1.set)
            # When cells are connected, add edge to final set
            else:
                new_edges.append(edge)
            
        return new_edges

    def __repr__(self):
        return f"Labyrinth({self.grid})"

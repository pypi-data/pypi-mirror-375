"""Example with layered Series and Group instances."""

from os import path, chdir
from copy import deepcopy

from pyrbd import Block, Group, Series, Diagram

chdir(path.dirname(__file__))

# Define the blocks comprising the diagram
start_block = Block("Start", "blue!30")
block = Block("Basic block", "gray")
group_1 = Group(
    [deepcopy(b) + deepcopy(b) for b in 3 * [block]],
    text="Group",
    color="orange",
    parent=start_block,
)
series_1 = Series(
    [deepcopy(block), 2 * deepcopy(block)], text="Series", color="red", parent=group_1
)
series_2 = Series(
    [2 * deepcopy(block), deepcopy(block), 3 * (deepcopy(block) + deepcopy(block))],
    text="Series",
    color="RoyalBlue",
    parent=series_1,
)
end_block = Block("End", "green!50", parent=series_2)

# Define and compile the diagram
diagram = Diagram(
    "layered_RBD",
    blocks=[start_block, group_1, series_1, series_2, end_block],
)
diagram.write()
diagram.compile(["pdf", "svg"])

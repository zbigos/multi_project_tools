import itertools
from typing import Dict, Tuple
import logging

def allocate_macros(
    design_size_x: int,
    design_size_y: int,
    h_edge: int,
    v_edge: int,
    macro_snap: float,
    projects,
    allocation_policy: str,
    openram,
) -> Dict[int, Tuple[int, int]]:

    if allocation_policy == "legacy":
        return legacy_allocation(design_size_x, design_size_y, h_edge, v_edge, macro_snap, projects, openram)

    logging.critical(f"unknown allocation policy {allocation_policy}")
    exit(1)

def legacy_allocation(
    design_size_x: int,
    design_size_y: int,
    x_edge: int,
    y_edge: int,
    macro_snap: float,
    projects,
    openram,
) -> Dict[int, Tuple[int, int]]:
    
    allocation = {}

    macro_x = 360
    macro_y = 360

    x_space = (design_size_x  - 2 * x_edge - (4 * macro_x)) / 3
    y_space = (design_size_y  - 2 * y_edge - (4 * macro_y)) / 3

    for id_, (px, py) in enumerate(itertools.product(range(4), range(4))):
        x = x_edge + (x_space + macro_x)  * px
        y = y_edge + (y_space + macro_y)  * py

        # snap to grid
        x = int(x / macro_snap) * macro_snap
        y = int(y / macro_snap) * macro_snap

        allocation[id_] = (x, y)
   
    # HACK! TODO, hope this will be fixed with new allocator
    if openram:
        # put whatever is in position 0 to the end so there is room for openram
        num_projects = len(projects)
        allocation[0] = allocation[num_projects]
        logging.info("moving project with id 0 to %d" % num_projects)

        # swap whatever is in pos 4 (to the right of openram) with the wb shim
        for project in projects:
            if project.title == 'wb_openram_shim':
                logging.info("swapping projects %s and %s to put shim next to openram" % (projects[4], project))
                old = allocation[4]
                allocation[4] = allocation[project.id]
                old = (int(old[0] + 200), old[1]) # move it 200um to the right
                allocation[project.id] = old
                break

    return allocation

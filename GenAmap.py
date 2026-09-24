
#!/usr/bin/env python3
"""Generates a flat map for car-soccer.com in the csmap format.

Format based on the 'Dribbling Challenge 1 Remastered' JSON:
- meshes: positions (float32 xyz), indices (uint32), uv (float32) in base64
- instances: mesh + material + 4x4 matrix (column-major) + collision
- volumes (ballFinish, etc.): box with min/max and a 6-plane hull [nx,ny,nz,d]
Large units (cm-style), Z is the height.
"""

import base64
import json
import struct


# ---------------- CONFIGURATION (edit here!) ----------------
NAME = "Plan"
AUTHOR = "UNKNOWN"
SIZE = 20000             # arena side length (X and Y), in units
FLOOR_THICKNESS = 200    # floor thickness (top is at Z = 0)
WALLS = True              # low walls around the arena to keep the ball inside
WALL_HEIGHT = 1000
WALL_THICKNESS = 200
FLOOR_COLOR = 0x2E7D32   # green
WALL_COLOR = 0xB0B0B0    # gray
SKY_COLOR = 0x87CEEB     # light blue
NUM_STAGES = 30           # original has 30 stages = 31 checkpoints and 30 ballGoals
OUTPUT = "flat_arena_csmap.json"
# ------------------------------------------------------------


def b64(fmt, values):
    return base64.b64encode(
        struct.pack("<%d%s" % (len(values), fmt), *values)
    ).decode()


def box(sx, sy, sz):
    """Creates a box of size sx*sy*sz centered at the origin.

    24 vertices with outward-facing faces.
    The size is embedded directly into the vertices (like the original),
    so the matrix can use scale 1 — the game rejects huge scales
    ("excessive scale").
    """
    faces = [
        # (normal, 4 corners in counter-clockwise order when viewed from outside)
        ((0, 0, 1), [
            (-.5, -.5, .5),
            (.5, -.5, .5),
            (.5, .5, .5),
            (-.5, .5, .5),
        ]),
        ((0, 0, -1), [
            (-.5, .5, -.5),
            (.5, .5, -.5),
            (.5, -.5, -.5),
            (-.5, -.5, -.5),
        ]),
        ((1, 0, 0), [
            (.5, -.5, -.5),
            (.5, .5, -.5),
            (.5, .5, .5),
            (.5, -.5, .5),
        ]),
        ((-1, 0, 0), [
            (-.5, .5, -.5),
            (-.5, -.5, -.5),
            (-.5, -.5, .5),
            (-.5, .5, .5),
        ]),
        ((0, 1, 0), [
            (.5, .5, -.5),
            (-.5, .5, -.5),
            (-.5, .5, .5),
            (.5, .5, .5),
        ]),
        ((0, -1, 0), [
            (-.5, -.5, -.5),
            (.5, -.5, -.5),
            (.5, -.5, .5),
            (-.5, -.5, .5),
        ]),
    ]

    positions, indices, uv = [], [], []

    for face_index, (_, quad) in enumerate(faces):
        base = face_index * 4

        for vertex in quad:
            positions += [
                vertex[0] * sx,
                vertex[1] * sy,
                vertex[2] * sz,
            ]

        uv += [0, 0, 1, 0, 1, 1, 0, 1]

        indices += [
            base,
            base + 1,
            base + 2,
            base,
            base + 2,
            base + 3,
        ]

    return {
        "positions": b64("f", positions),
        "indices": b64("I", indices),
        "uv": b64("f", uv),
    }


def matrix(sx, sy, sz, tx, ty, tz):
    """Creates a 4x4 column-major matrix.

    Contains scale on the three axes and translation in the last three values.
    """
    return [
        sx, 0, 0, 0,
        0, sy, 0, 0,
        0, 0, sz, 0,
        tx, ty, tz, 1,
    ]


def box_volume(minimum, maximum):
    """Creates a volume in the format used by ballGoals,
    ballFinish, and ballDeathVolumes.
    """
    planes = [
        1, 0, 0, maximum[0],
        0, 1, 0, maximum[1],
        0, 0, 1, maximum[2],
        0, 0, -1, -minimum[2],
        -1, 0, 0, -minimum[0],
        0, -1, 0, -minimum[1],
    ]

    return {
        "min": list(minimum),
        "max": list(maximum),
        "hulls": [{
            "min": list(minimum),
            "max": list(maximum),
            "planes": planes,
        }],
    }


def main():
    half_size = SIZE / 2
    wall_thickness = WALL_THICKNESS
    wall_height = WALL_HEIGHT
    total_side = SIZE + 2 * wall_thickness

    meshes = [
        box(SIZE, SIZE, FLOOR_THICKNESS)
    ]  # 0 = floor

    instances = [{
        "mesh": 0,
        "material": 0,
        "collision": True,
        "matrix": matrix(
            1,
            1,
            1,
            0,
            0,
            -FLOOR_THICKNESS / 2,
        ),
    }]

    if WALLS:
        meshes.append(box(total_side, wall_thickness, wall_height))
        # 1 = north/south walls

        meshes.append(box(wall_thickness, SIZE, wall_height))
        # 2 = east/west walls

        for mesh, tx, ty in [
            (1, 0, half_size + wall_thickness / 2),   # north
            (1, 0, -half_size - wall_thickness / 2),  # south
            (2, half_size + wall_thickness / 2, 0),   # east
            (2, -half_size - wall_thickness / 2, 0),  # west
        ]:
            instances.append({
                "mesh": mesh,
                "material": 1,
                "collision": True,
                "matrix": matrix(
                    1,
                    1,
                    1,
                    tx,
                    ty,
                    wall_height / 2,
                ),
            })

    # Start + N stages.
    # The game validates the count:
    # checkpoints = goals + 1.
    #
    # All checkpoints are in the same location because
    # the arena is a single open area.
    checkpoints = []

    for n in range(NUM_STAGES + 1):
        checkpoints.append({
            "position": [0, 0, 60],
            # Car spawns slightly above the floor

            "yaw": 1.5707963267948966,
            # Facing +Y, like the original

            "radius": 500,

            "ballPosition": [0, 700, 200],
            # Ball in front of the car

            "name": (
                "Start"
                if n == 0
                else "Stage %d / %d" % (n, NUM_STAGES)
            ),
        })

    # One mini-goal per stage, lined up near the north wall
    # without overlapping.
    goals = []

    step = 600
    x0 = -step * (NUM_STAGES - 1) / 2

    for n in range(NUM_STAGES):
        gx = x0 + n * step

        goals.append(
            box_volume(
                (gx - 200, half_size - 900, 0),
                (gx + 200, half_size - 500, 400),
            )
        )

    map_data = {
        "version": 1,
        "name": NAME,
        "author": AUTHOR,
        "description": "Auto-Scripted.",
        "killZ": -30000,
        "skyColor": SKY_COLOR,

        "meshes": meshes,

        "materials": [
            {
                "color": FLOOR_COLOR,
                "roughness": 0.9,
            },
            {
                "color": WALL_COLOR,
                "roughness": 0.8,
            },
        ],

        "instances": instances,
        "checkpoints": checkpoints,
        "deathVolumes": [],

        # Ball that falls outside the map
        # (far below the floor) "dies".
        "ballDeathVolumes": [
            box_volume(
                (-50000, -50000, -30000),
                (50000, 50000, -1000),
            )
        ],

        "ballGoals": goals,

        # Small box in the corner of the arena,
        # just to provide a valid ballFinish.
        "ballFinish": box_volume(
            (half_size - 1200, half_size - 1200, 0),
            (half_size - 200, half_size - 200, 800),
        ),

        "motions": [],
        "movingHazards": [],
    }

    with open(OUTPUT, "w") as file:
        json.dump(
            map_data,
            file,
            separators=(",", ":"),
        )

    print("Map generated:", OUTPUT)


if __name__ == "__main__":
    main()

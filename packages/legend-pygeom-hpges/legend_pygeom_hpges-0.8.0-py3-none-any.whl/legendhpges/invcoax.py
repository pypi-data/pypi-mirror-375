from __future__ import annotations

import math

import awkward as ak
import numpy as np
from numpy.typing import ArrayLike, NDArray
from pyg4ometry import geant4

from . import utils
from .base import HPGe
from .build_utils import make_pplus


class InvertedCoax(HPGe):
    """An inverted-coaxial point contact germanium detector."""

    def __init__(self, *args, **kwargs):
        self.borehole_z = []
        self.borehole_r = []

        super().__init__(*args, **kwargs)

    def _decode_polycone_coord(self) -> tuple[list[float], list[float]]:
        c = self.metadata.geometry

        def _tan(a):
            return math.tan(math.pi * a / 180)

        r = []
        z = []
        surfaces = []

        # save the borehole coords
        borehole_r = []
        borehole_z = []

        r_p, z_p, surface_p = make_pplus(c)
        r += r_p
        z += z_p
        surfaces += surface_p

        if c.taper.bottom.height_in_mm > 0:
            r += [
                c.radius_in_mm
                - c.taper.bottom.height_in_mm * _tan(c.taper.bottom.angle_in_deg),
                c.radius_in_mm,
            ]

            z += [
                0,
                c.taper.bottom.height_in_mm,
            ]
            surfaces += ["nplus", "nplus"]

        else:
            r += [c.radius_in_mm]
            z += [0]
            surfaces += ["nplus"]

        if c.taper.top.height_in_mm > 0:
            r += [
                c.radius_in_mm,
                c.radius_in_mm
                - c.taper.top.height_in_mm * _tan(c.taper.top.angle_in_deg),
            ]

            z += [
                c.height_in_mm - c.taper.top.height_in_mm,
                c.height_in_mm,
            ]
            surfaces += ["nplus", "nplus"]

        else:
            r += [c.radius_in_mm]
            z += [c.height_in_mm]
            surfaces += ["nplus"]

        # first point of the borehole
        borehole_r += [0]
        borehole_z += [c.height_in_mm]

        if c.taper.borehole.height_in_mm > 0:
            r += [
                c.borehole.radius_in_mm
                + c.taper.borehole.height_in_mm * _tan(c.taper.borehole.angle_in_deg),
                c.borehole.radius_in_mm,
            ]

            z += [
                c.height_in_mm,
                c.height_in_mm - c.taper.borehole.height_in_mm,
            ]
            surfaces += ["nplus", "nplus"]

            # add borehole coords
            borehole_r += r[-2:]
            borehole_z += z[-2:]
        else:
            r += [c.borehole.radius_in_mm]
            z += [c.height_in_mm]
            surfaces += ["nplus"]

            borehole_r += [r[-1]]
            borehole_z += [z[-1]]

        # add borehole with or without tapering
        if c.taper.borehole.height_in_mm != c.borehole.depth_in_mm:
            r += [
                c.borehole.radius_in_mm,
                0,
            ]

            z += [
                c.height_in_mm - c.borehole.depth_in_mm,
                c.height_in_mm - c.borehole.depth_in_mm,
            ]
            surfaces += ["nplus", "nplus"]

            borehole_r += r[-2:]
            borehole_z += z[-2:]

        else:
            r += [0]

            z += [c.height_in_mm - c.borehole.depth_in_mm]
            surfaces += ["nplus"]

            borehole_r += [r[-1]]
            borehole_z += [z[-1]]

        self.surfaces = surfaces

        # save the borehole coordinates for future reference

        # reverse to keep clockwise orientation
        self.borehole_r = borehole_r[::-1]
        self.borehole_z = borehole_z[::-1]

        return r, z

    def is_inside_borehole(self, coords: ArrayLike, tol: float = 1e-11) -> NDArray:
        """Check if a point is inside the ICPC borehole

        Parameters
        ----------
        coords
            2D array of shape `(n,3)` of `(x,y,z)` coordinates for each of `n`
            points, second index corresponds to `(x,y,z)`.
        tol
            distance outside the surface which is considered inside. Should be
            on the order of numerical precision of the floating point representation.
        """
        if not isinstance(self.solid, geant4.solid.GenericPolycone):
            msg = f"is_inside_borehole is not implemented for {type(self.solid)} yet"
            raise NotImplementedError(msg)

        if not isinstance(coords, np.ndarray):
            coords = np.array(coords)

        if np.shape(coords)[1] != 3:
            msg = "coords must be provided as a 2D array with x,y,z coordinates for each point."
            raise ValueError(msg)

        r, z = self.borehole_r, self.borehole_z

        coords_rz = utils.convert_coords(coords)
        s1, s2 = utils.get_line_segments(r, z)

        # get the distance for each line segment
        dists = utils.shortest_distance(s1, s2, coords_rz, tol, signed=True)

        # find the minimal distance
        # if we have two of the same sign take the negative value
        # this is correct as long as we dont have angles > 180 deg

        abs_arr = np.abs(dists)
        min_vals = ak.min(abs_arr, axis=1)

        is_min = ak.Array(np.isclose(abs_arr, min_vals[:, np.newaxis]))
        dists = ak.Array(dists)

        min_dist = ak.min(dists[is_min], axis=-1)
        sign = ak.where(min_dist >= 0, True, False)

        return sign.to_numpy()

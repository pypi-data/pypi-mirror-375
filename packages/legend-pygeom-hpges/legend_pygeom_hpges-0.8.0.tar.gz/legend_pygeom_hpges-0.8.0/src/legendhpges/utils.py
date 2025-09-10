from __future__ import annotations

import json
import logging
from pathlib import Path

import numba
import numpy as np
import yaml
from numpy.typing import ArrayLike, NDArray

log = logging.getLogger(__name__)
__file_extensions__ = {"json": [".json"], "yaml": [".yaml", ".yml"]}


def load_dict(fname: str, ftype: str | None = None) -> dict:
    """Load a text file as a Python dict."""
    fname = Path(fname)

    # determine file type from extension
    if ftype is None:
        for _ftype, exts in __file_extensions__.items():
            if fname.suffix in exts:
                ftype = _ftype

    msg = f"loading {ftype} dict from: {fname}"
    log.debug(msg)

    with fname.open() as f:
        if ftype == "json":
            return json.load(f)
        if ftype == "yaml":
            return yaml.safe_load(f)

        msg = f"unsupported file format {ftype}"
        raise NotImplementedError(msg)


@numba.njit(cache=True)
def convert_coords(coords: ArrayLike) -> NDArray:
    """Converts (x,y,z) coordinates into (r,z)

    Parameters
    ----------
    coords
        numpy array of coordinates where the second index corresponds to (x,y,z) respectively

    Returns
    -------
        numpy array of (r,z) coordinates for each point

    """
    r = np.sqrt(coords[:, 0] ** 2 + coords[:, 1] ** 2)
    return np.column_stack((r, coords[:, 2]))


def shortest_distance_to_plane(
    a_vec: NDArray,
    d: float,
    points: NDArray,
    rmax: float | None = None,
    zrange: tuple[float, float] | None = None,
) -> NDArray:
    """Get the shortest distance from a plane (constrained in r and z) to each point.

    The equation of the plane is given by :math:`a_1x+a_2y+a_3z=d`. Where
    :math:`\\vec{a}=(a_1,a_2,a_3)`.
    The closest point on the plane to the point (:math:`y`) is then given by:

    .. math::
        x =y-(y*a-d)*a/||a||^2

    The distance is then given by the length of the vector :math:`x-y`. This
    function also checks if the intersection point is above `rmax` or inside the
    `zrange`, if not, ``numpy.nan`` is returned for that point.

    Parameters
    ----------
    a_vec
        3 coordinate array defining the plane.
    d
        scalar in the plane definition.
    points
        set of points to compute distance.
    rmax
        maximum radius for the plane.
    zrange
        range in z for the plane.
    """

    def _dot(a, b):
        return np.sum(a * b, axis=1)

    def _norm(a):
        ax = 1 if a.ndim == 2 else 0
        return np.sqrt(np.sum(a**2, axis=ax))

    a_norm = np.sum(a_vec * a_vec)

    proj_points = points - ((_dot(points, a_vec) - d)[:, np.newaxis]) * a_vec / a_norm

    dist_vec = _norm((_dot(points, a_vec) - d)[:, np.newaxis] * a_vec / a_norm)

    # check on r and z

    proj_points_rz = convert_coords(proj_points)

    if rmax is not None:
        condition_r = proj_points_rz[:, 0] <= rmax
    else:
        condition_r = np.full(len(points), True)

    if zrange is not None:
        condition_z = (proj_points_rz[:, 1] > zrange[0]) & (
            proj_points_rz[:, 1] < zrange[1]
        )
    else:
        condition_z = np.full(len(points), True)

    condition = condition_r * condition_z
    return np.where(condition, dist_vec, np.full(len(points), np.nan))


def get_line_segments(
    r: ArrayLike, z: ArrayLike, surface_indices: ArrayLike = None
) -> tuple[NDArray, NDArray]:
    """Extracts the line segments from a shape.

    Parameters
    ---------
    r
        array or list of radial positions defining the polycone.
    z
        array or list of vertical positions defining the polycone.
    surface_indices
        list of integer indices of surfaces to consider. If ``None`` (the
        default) all surfaces used.

    Returns
    -------
        tuple of (s1,s2) arrays describing the line segments, both `s1` and
        `s2` have shape `(n_segments,2)` where the first axis represents thhe
        segment and the second `(r,z)`.
    """
    # build lists of pairs of coordinates
    s1 = np.array([np.array([r1, z1]) for r1, z1 in zip(r[:-1], z[:-1], strict=True)])
    s2 = np.array([np.array([r2, z2]) for r2, z2 in zip(r[1:], z[1:], strict=True)])

    if surface_indices is not None:
        s1 = s1[surface_indices]
        s2 = s2[surface_indices]

    return s1, s2


@numba.njit(cache=True)
def shortest_grid_distance(points, s1, s2, axis, signed=True, sign_factor=1):
    other_axis = int(~bool(axis))
    x_level = s1[other_axis]  # x-coordinate of the vertical line
    y_min, y_max = s1[axis], s2[axis]

    # Points that project onto the segment (y between y_min and y_max)
    mask_on_segment = (points[:, axis] >= y_min) & (points[:, axis] <= y_max)

    # Initialize distance vector
    dist_vec = np.zeros_like(points)

    # For points that project onto the segment (y within bounds)
    x_diff = points[:, other_axis] - x_level
    dist_vec[mask_on_segment, other_axis] = x_diff[mask_on_segment]

    # For points below the segment
    mask_below = points[:, axis] < y_min
    dist_vec[mask_below] = points[mask_below] - s1

    # For points above the segment
    mask_above = points[:, axis] > y_max
    dist_vec[mask_above] = points[mask_above] - s2

    # Compute sign for segment (positive to the right for vertical and positive below for horizontal)
    if signed:
        sign_vec_norm = np.ones(len(points))

        mask = x_diff > 0 if sign_factor == 1 else x_diff < 0
        sign_vec_norm[mask] = -1

    else:
        sign_vec_norm = np.ones(len(points))

    return dist_vec, sign_vec_norm


@numba.guvectorize(
    [
        "void(float32[:], float32[:], float32[:, :], float32, boolean, float32[:], float32[:])",
        "void(float64[:], float64[:], float64[:, :], float64, boolean, float64[:], float64[:])",
    ],
    "(d),(d),(n,d),(),()->(n),(n)",
    nopython=True,
    target="parallel",
)
def diagonal_segment_distance(s1, s2, points, tol, signed, dist_result, sign_result):
    """Calculate distances from points to a diagonal line segment.

    Parameters
    ----------
    s1 : ndarray
        First point of the segment (2D)
    s2 : ndarray
        Second point of the segment (2D)
    points : ndarray
        Array of points to calculate distances from
    tol : float
        Tolerance for numerical calculations
    signed : bool
        Whether to return signed distances
    dist_result : ndarray
        Output array for distances
    sign_result : ndarray
        Output array for signs
    """
    n_points = points.shape[0]

    # Calculate segment direction vector (unit vector)
    seg_length = np.sqrt((s2[0] - s1[0]) ** 2 + (s2[1] - s1[1]) ** 2)
    n_x = (s2[0] - s1[0]) / seg_length
    n_y = (s2[1] - s1[1]) / seg_length

    for i in range(n_points):
        # Vector from s1 to point
        diff_x = s1[0] - points[i, 0]
        diff_y = s1[1] - points[i, 1]

        # Dot product of diff_s1 and n
        dot_product = diff_x * n_x + diff_y * n_y

        # Projection distance along the segment
        proj_dist = -dot_product

        # Initialize distance vector
        dist_vec_x = 0.0
        dist_vec_y = 0.0

        if proj_dist < 0:
            # Closest point is s1
            dist_vec_x = diff_x
            dist_vec_y = diff_y

        elif proj_dist > seg_length:
            # Closest point is s2
            dist_vec_x = s2[0] - points[i, 0]
            dist_vec_y = s2[1] - points[i, 1]

        else:
            # Closest point is on the segment
            dist_vec_x = diff_x - n_x * dot_product
            dist_vec_y = diff_y - n_y * dot_product

        # Calculate distance
        normed_dist = np.sqrt(dist_vec_x**2 + dist_vec_y**2)

        # Calculate sign if needed
        if signed:
            # Cross product of n and dist_vec
            sign_vec = n_x * dist_vec_y - n_y * dist_vec_x

            # Push points on surface inside
            if abs(sign_vec) < tol:
                sign_vec = -tol

            # Normalize sign
            sign_vec_norm = -sign_vec / abs(sign_vec)

        else:
            sign_vec_norm = 1.0

        # Store results
        if normed_dist < tol:
            dist_result[i] = tol
        else:
            dist_result[i] = normed_dist

        sign_result[i] = sign_vec_norm


@numba.njit(cache=True)
def shortest_distance(
    s1_list: NDArray,
    s2_list: NDArray,
    points: NDArray,
    tol: float = 1e-11,
    signed: bool = True,
) -> tuple[NDArray, NDArray]:
    """Get the shortest distance between each point and a line segment.

    Based on vector algebra where the distance vector is given by:

    .. math::
        d = s_1 - p - ( (n · (s_1- p)) * n )

    where:

    - :math:`s_1` is a vector from which the distance is measured,
    - `p` is a point vector,
    - `n` is a unit direction vector from :math:`s_1` to :math:`s_2`,
    - `a` is another point vector.

    If the projection point lies inside the segment s1-s2. Else the closest
    point is either :math:`s_1` or :math:`s_2`.  The distance is the modulus of
    this vector and this calculation is performed for each point.  A sign is
    attached based on the cross product of the line vector and the distance
    vector.  To avoid numerical issues any point within the tolerance is
    considered inside.

    Parameters
    ----------
    s1_list
        `(n_segments,2)` np.array of the first points in the line segment, for
        the second axis indices `0,1` correspond to `r,z`.
    s2_list
        second points, same format as `s1_list`.
    points
        `(n_points,2)` array of points to compare, first axis corresponds to
        the point index and the second to `(r,z)`.
    tol
        tolerance when computing sign, points within this distance to the
        surface are pushed inside.
    signed
        boolean flag to attach a sign to the distance (positive if inside).

    Returns
    -------
        ``(n_points,n_segments)`` numpy array of the shortest distances for each segment.
    """

    # helper functions
    def _dot(a, b):
        return np.sum(a * b, axis=1)

    def _norm(a):
        ax = 1 if a.ndim == 2 else 0
        return np.sqrt(np.sum(a**2, axis=ax))

    n_segments = len(s1_list)
    dists = np.full((len(points), len(s1_list)), np.nan)

    for segment in range(n_segments):
        s1 = s1_list[segment]
        s2 = s2_list[segment]
        # check if vertical or horizontal
        # Ensure s2's coordinate is always >= s1's coordinate for simpler logic
        if (s1[0] > s2[0]) or (s1[1] > s2[1]):
            s1, s2 = s2, s1
            sign_factor = -1
        else:
            sign_factor = 1

        if (abs(s1[0] - s2[0]) < tol) or (abs(s1[1] - s2[1]) < tol):
            axis = 1 if abs(s1[0] - s2[0]) < tol else 0
            # Compute distances for segment
            dist_vec, sign_vec_norm = shortest_grid_distance(
                points,
                s1,
                s2,
                axis=axis,
                signed=signed,
                sign_factor=sign_factor if axis == 1 else -sign_factor,
            )
            normed_dist = np.abs(
                np.where(
                    dist_vec[:, axis] == 0,
                    dist_vec[:, int(~bool(axis))],
                    _norm(dist_vec),
                )
            )

        else:
            n = (s2 - s1) / _norm(s2 - s1)

            proj_dist = -_dot(n, (n * _dot(s1 - points, n)[:, np.newaxis]))

            dist_vec = np.empty_like(s1 - points)

            condition1 = proj_dist < 0
            condition2 = proj_dist > _norm(s2 - s1)
            condition3 = (~condition1) & (~condition2)

            diff_s1 = s1 - points
            dist_vec[condition1] = diff_s1[condition1]
            dist_vec[condition2] = s2 - points[condition2]
            dist_vec[condition3] = (
                diff_s1[condition3] - n * _dot(diff_s1, n)[condition3, np.newaxis]
            )

            # make this signed so inside is positive and outside negative
            if signed:
                sign_vec = n[0] * dist_vec[:, 1] - n[1] * dist_vec[:, 0]

                # push points on surface inside
                sign_vec = (
                    np.where(np.abs(sign_vec) < tol, -tol, sign_vec) * sign_factor
                )
                sign_vec_norm = -sign_vec / np.abs(sign_vec)

            else:
                sign_vec_norm = np.ones(len(dist_vec))
            normed_dist = np.abs(_norm(dist_vec))

        dists[:, segment] = np.where(
            normed_dist < tol,
            tol,
            normed_dist * sign_vec_norm,
        )
    return dists


@numba.njit(cache=True)
def iterate_segments(s1, s2, coords_rz, tol, signed):
    # first sort by lengths longest first
    segment_lengths = np.sum((s1 - s2) ** 2, axis=1)
    sort_indices = np.argsort(segment_lengths)[::-1]
    s1 = s1[sort_indices]
    s2 = s2[sort_indices]

    dists = np.full(len(coords_rz), np.inf)
    diffs = s1 - s2
    perps = np.abs(diffs[:, 0] * diffs[:, 1]) < tol
    perp_indices = np.where(perps)[0]
    non_perp_indices = np.where(~perps)[0]

    # get shortest distance to vertical/horizontal surfaces
    if len(perp_indices) > 0:
        for start, end in zip(s1[perp_indices], s2[perp_indices]):  # noqa: B905
            if (dists == np.inf).all():
                candidates = np.arange(0, len(coords_rz))
            else:
                diff_x = np.abs(end[0] - start[0])
                axis = 0 if diff_x < tol else 1
                diff_start = np.abs(coords_rz - start)[:, axis]
                abs_dists = np.abs(dists)
                candidates = np.where(diff_start < abs_dists)[0]
                # only calculate for these if
                # and between s1 and s2 or dist
                # in both dimensions to s1/s2 < current min
                # candidates = np.where(between | close)[0]

            if len(candidates) > 0:
                start_array = np.ascontiguousarray(start).reshape(1, -1)
                end_array = np.ascontiguousarray(end).reshape(1, -1)

                dist_candidates = shortest_distance(
                    start_array,
                    end_array,
                    coords_rz[candidates],
                    tol=tol,
                    signed=signed,
                ).flatten()

                mask = np.abs(dist_candidates) < np.abs(dists[candidates])
                # print(candidates[mask])
                dists[candidates[mask]] = dist_candidates[mask]

    # compute shortest distances to remaining surfaces
    # this condition could probably be tightened
    if len(non_perp_indices) > 0:
        for start, end in zip(s1[non_perp_indices], s2[non_perp_indices]):  # noqa: B905
            # Calculate distance to endpoints
            dist_to_start_sq = np.sum((coords_rz - start) ** 2, axis=1)
            dist_to_end_sq = np.sum((coords_rz - end) ** 2, axis=1)

            # Calculate segment length
            segment_length_sq = np.sum((end - start) ** 2)

            # Triangle inequality test:
            # If a point is closer to the segment than its current min distance,
            # then at least one of these must be true:
            # 1. It's within (current_dist + segment_length) of the start point
            # 2. It's within (current_dist + segment_length) of the end point

            threshold_dist_sq = (
                dists**2 + segment_length_sq + (2 * dists * segment_length_sq)
            )

            candidates = np.where(
                (dist_to_start_sq < threshold_dist_sq)
                | (dist_to_end_sq < threshold_dist_sq)
            )[0]

            if len(candidates) > 0:
                dist_candidates = shortest_distance(
                    np.ascontiguousarray(start).reshape(1, -1),
                    np.ascontiguousarray(end).reshape(1, -1),
                    coords_rz[candidates, :],
                    tol=tol,
                    signed=signed,
                ).flatten()
                mask = np.abs(dist_candidates) < np.abs(dists[candidates])
                dists[candidates[mask]] = dist_candidates[mask]
    return dists

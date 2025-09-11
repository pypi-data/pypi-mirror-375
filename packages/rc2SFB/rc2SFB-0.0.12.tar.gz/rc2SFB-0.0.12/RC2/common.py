from typing import Tuple
import numpy as np

def compute_xi_component(u, v, rot_angle_deg: float):
    """
    Project (u,v) onto rotated axes: returns (xi, n).
    xi-axis = [-sin(theta), cos(theta)], n-axis = [cos(theta), sin(theta)].
    Works for coordinates (x,y) or vector components (U,V).
    """
    theta = np.deg2rad(rot_angle_deg)
    coords = np.c_[np.asarray(u), np.asarray(v)]
    n_vec  = np.array([np.cos(theta),  np.sin(theta)])
    xi_vec = np.array([-np.sin(theta), np.cos(theta)])
    xi = (coords @ xi_vec[:, None]).flatten()
    n  = (coords @ n_vec[:,  None]).flatten()
    return xi, n

def in_range(point, x_lims: Tuple[float, float], y_lims: Tuple[float, float], margin: float = 0) -> bool:
    """Check if (x,y) lies inside the box with an optional relative margin."""
    x, y = float(point[0]), float(point[1])
    return (
        (x >= x_lims[0] - abs(x_lims[0]) * margin)
        and (x <= x_lims[1] + abs(x_lims[1]) * margin)
        and (y >= y_lims[0] * (1 - margin))
        and (y <= y_lims[1] * (1 + margin))
    )

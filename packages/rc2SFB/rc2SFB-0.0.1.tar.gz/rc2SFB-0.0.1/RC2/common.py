from typing import Tuple, Sequence
import numpy as np

def compute_xi_component(u: np.ndarray, v: np.ndarray, rot_angle_deg: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Project (u,v) onto tangential xi-hat and normal n-hat rotated by rot_angle_deg.
    Returns (component along xi, component along n).
    """
    ang = np.deg2rad(rot_angle_deg)
    n_vec  = np.array([np.cos(ang), np.sin(ang)])     # normal
    xi_vec = np.array([-np.sin(ang), np.cos(ang)])    # tangent
    coords = np.c_[u, v]
    return (coords @ xi_vec[:, None]).ravel(), (coords @ n_vec[:, None]).ravel()

def in_range(point: Sequence[float], x_lims: Tuple[float, float], y_lims: Tuple[float, float], margin: float = 0.0) -> bool:
    """Inclusive range check with a relative margin."""
    return (
        (point[0] >= x_lims[0] - abs(x_lims[0]) * margin) and
        (point[0] <= x_lims[1] + abs(x_lims[1]) * margin) and
        (point[1] >= y_lims[0] * (1 - margin)) and
        (point[1] <= y_lims[1] * (1 + margin))
    )


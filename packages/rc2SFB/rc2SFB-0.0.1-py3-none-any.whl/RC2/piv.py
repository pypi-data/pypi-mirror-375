from __future__ import annotations
import enum
import numpy as np
import scipy.interpolate as spi
from .common import compute_xi_component

class DataColumn(enum.IntEnum):
    X = 0; Y = 1; Z = 2
    U = 3; V = 4; W = 5
    magVel = 6
    stdU = 7; stdV = 8; stdW = 9
    TKE = 10
    N_VEC = 11
    VALID = 12
    XI = 13        # added by compute step
    Uxi = 14       # added by compute step
    Un = 15        # added by compute step
    stdUxi = 16    # added by compute step

class PIVData:
    def __init__(self, file_path: str, width_px: int, height_px: int, rot_angle_deg: float):
        self.data_ = np.genfromtxt(file_path, delimiter=" ", skip_header=3)
        self.width_px_ = int(width_px)
        self.height_px_ = int(height_px)
        self._compute_xi(rot_angle_deg)
        self._compute_limits()

    # ---------- internals ----------
    def _minmax(self, col: int):
        c = self.data_[:, col]
        return float(np.min(c)), float(np.max(c))

    def _compute_limits(self) -> None:
        self.xlim  = self._minmax(DataColumn.X)
        self.ylim  = self._minmax(DataColumn.Y)
        self.zlim  = self._minmax(DataColumn.Z)
        self.xilim = self._minmax(DataColumn.XI)

    def _gridded(self, data: np.ndarray) -> np.ndarray:
        return np.flipud(np.reshape(data, (self.height_px_, self.width_px_)))

    def _contour_field(self, column: int) -> np.ndarray:
        return self._gridded(self.data_[:, column])

    def _interpolator(self, col: int):
        xi_grid, z_grid, *_ = self.cntr([DataColumn.XI, DataColumn.Z])
        vals = self._gridded(self.data_[:, col])
        return spi.RegularGridInterpolator(
            (xi_grid[0, :].ravel(), z_grid[:, 0].ravel()),
            vals.T, method="linear"
        )

    def _scale_col(self, col: int, s: float) -> None:
        self.data_[:, col] /= s

    def _compute_xi(self, ang_deg: float) -> None:
        x = self.data_[:, DataColumn.X]; y = self.data_[:, DataColumn.Y]
        u = self.data_[:, DataColumn.U]; v = self.data_[:, DataColumn.V]
        su = self.data_[:, DataColumn.stdU]; sv = self.data_[:, DataColumn.stdV]

        xi,  _  = compute_xi_component(x, y, ang_deg)
        uxi, un = compute_xi_component(u, v, ang_deg)
        std_uxi, _ = compute_xi_component(su, sv, ang_deg)

        self.data_ = np.hstack([self.data_, xi[:,None], uxi[:,None], un[:,None], std_uxi[:,None]])

    # ---------- public API ----------
    def scale(self, length: float = 1000.0, vel: float = 0.151) -> None:
        for c in (DataColumn.X, DataColumn.Y, DataColumn.Z, DataColumn.XI):
            self._scale_col(c, length)
        self._compute_limits()

        for c in (DataColumn.U, DataColumn.V, DataColumn.W, DataColumn.Uxi, DataColumn.magVel, DataColumn.stdU, DataColumn.stdV, DataColumn.stdW, DataColumn.stdUxi):
            self._scale_col(c, vel)
        self._scale_col(DataColumn.TKE, vel**2)

    def cntr(self, columns: list[int]):
        return [self._contour_field(int(c)) for c in columns]

    def strm(self, n_div: int = 50):
        x = np.linspace(*self.xilim, n_div)
        z = np.linspace(*self.zlim, n_div)
        X, Z = np.meshgrid(x, z)
        U = self._interpolator(DataColumn.Uxi)((X.ravel(), Z.ravel()))
        V = self._interpolator(DataColumn.W  )((X.ravel(), Z.ravel()))
        return [X, Z, U.reshape(n_div, n_div), V.reshape(n_div, n_div)]

    def at_z(self, z_coord: float, variable: int, n_pts: int = 50):
        xi = np.linspace(self.xilim[0], self.xilim[1], n_pts)
        z = np.full_like(xi, z_coord, dtype=float)
        return xi, self._interpolator(int(variable))((xi, z))


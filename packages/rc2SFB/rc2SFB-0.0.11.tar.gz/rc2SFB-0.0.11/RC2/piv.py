import enum
import numpy as np
import scipy.interpolate as spi
from .common import compute_xi_component

class DataColumn(enum.IntFlag):
    X = 0; Y = 1; Z = 2
    U = 3; V = 4; W = 5
    magVel = 6
    stdU = 7; stdV = 8; stdW = 9
    TKE = 10
    N_VEC = 11
    VALID = 12
    XI = 13
    Uxi = 14
    Un = 15
    stdUxi = 16

class PIVData:
    def __init__(self, file_path, width_px, height_px, rot_angle_deg):
        self.data_ = np.genfromtxt(file_path, delimiter=" ", skip_header=3)
        self.width_px_ = int(width_px)
        self.height_px_ = int(height_px)
        self.__compute_xi(rot_angle_deg)
        self.__compute_limits()

    # ---- internals
    def __compute_limits(self):
        def mm(col): return (float(np.min(col)), float(np.max(col)))
        self.xlim  = mm(self.data_[:, DataColumn.X])
        self.ylim  = mm(self.data_[:, DataColumn.Y])
        self.zlim  = mm(self.data_[:, DataColumn.Z])
        self.xilim = mm(self.data_[:, DataColumn.XI])

    def __gridded(self, data):
        return np.flipud(np.reshape(data, (self.height_px_, self.width_px_)))

    def __contour_field(self, column):
        return self.__gridded(self.data_[:, column])

    def __interpolator(self, data_column):
        XI, Z = self.cntr([DataColumn.XI, DataColumn.Z])
        values = self.__gridded(self.data_[:, data_column])
        return spi.RegularGridInterpolator(
            (XI[0, :].flatten(), Z[:, 0].flatten()), values.T, method="linear"
        )

    def __scale_column(self, column, scale):
        self.data_[:, column] /= scale

    def __compute_xi(self, rot_angle_deg: float):
        x, y = self.data_[:, DataColumn.X], self.data_[:, DataColumn.Y]
        u, v = self.data_[:, DataColumn.U], self.data_[:, DataColumn.V]
        su, sv = self.data_[:, DataColumn.stdU], self.data_[:, DataColumn.stdV]

        xi, _        = compute_xi_component(x, y, rot_angle_deg)
        uxi, un      = compute_xi_component(u, v, rot_angle_deg)
        std_uxi, _   = compute_xi_component(su, sv, rot_angle_deg)

        self.data_ = np.hstack((
            self.data_,
            xi[:, None], uxi[:, None], un[:, None], std_uxi[:, None]
        ))

    # ---- public API
    def scale(self, length: float = 1000.0, vel: float = 0.151):
        for col in (DataColumn.X, DataColumn.Y, DataColumn.Z, DataColumn.XI):
            self.__scale_column(col, length)
        self.__compute_limits()

        for col in (DataColumn.U, DataColumn.V, DataColumn.W,
                    DataColumn.Uxi, DataColumn.magVel,
                    DataColumn.stdU, DataColumn.stdV, DataColumn.stdW, DataColumn.stdUxi):
            self.__scale_column(col, vel)
        self.__scale_column(DataColumn.TKE, vel ** 2)

    def cntr(self, columns):
        return [self.__contour_field(c) for c in columns]

    def strm(self, n_div=50):
        x = np.linspace(*self.xilim, n_div)
        z = np.linspace(*self.zlim,  n_div)
        X, Z = np.meshgrid(x, z)
        U = self.__interpolator(DataColumn.Uxi)((X.flatten(), Z.flatten()))
        V = self.__interpolator(DataColumn.W  )((X.flatten(), Z.flatten()))
        return [X, Z, U.reshape(n_div, n_div), V.reshape(n_div, n_div)]

    def at_z(self, z_coord, variable, n_pts=50):
        xi = np.linspace(self.xilim[0], self.xilim[1], n_pts)
        z = np.full_like(xi, z_coord)
        return xi, self.__interpolator(variable)((xi, z))

import enum
import re
import numpy as np
import scipy.interpolate as spi
from .common import compute_xi_component

# --------- Tecplot başlıklarını otomatik atlayan yardımcılar ----------
_num_line_re = re.compile(r'^\s*[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?')

def _first_data_line_index(path: str) -> int:
    """Başlıktaki metin satırlarını atlayıp ilk sayısal satırın (0-based) indeksini döndürür."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f):
            if _num_line_re.match(line):
                return i
    raise ValueError(f"No numeric data lines found in {path}")

def _load_piv_table(path: str) -> np.ndarray:
    """Başlık uzunluğu kendiliğinden tespit edilerek tabloyu okur."""
    skip = _first_data_line_index(path)
    arr = np.loadtxt(path, dtype=float, comments=None, skiprows=skip)
    if arr.ndim == 1:
        arr = arr[None, :]
    # kirli satırları temizle
    arr = arr[~np.any(~np.isfinite(arr), axis=1)]
    return arr
# ----------------------------------------------------------------------

class DataColumn(enum.IntFlag):
    # Tecplot verindeki ilk 12 sütun (örneğine göre)
    X = 0; Y = 1; Z = 2
    U = 3; V = 4; W = 5
    magVel = 6        # |V|
    stdU = 7; stdV = 8; stdW = 9
    N_VEC = 10        # Number of vectors
    VALID = 11        # isValid
    # Aşağıdakiler runtime'da eklenir (dinamik indekslenecek)
    XI = 13
    Uxi = 14
    Un = 15
    stdUxi = 16

class PIVData:
    def __init__(self, file_path, width_px, height_px, rot_angle_deg):
        # Tecplot başlıklarını otomatik atla
        self.data_ = _load_piv_table(file_path)
        self.width_px_ = int(width_px)
        self.height_px_ = int(height_px)

        # eklenen kolonların gerçek indekslerini tutacağız
        self._idx_XI = None
        self._idx_Uxi = None
        self._idx_Un = None
        self._idx_stdUxi = None

        self.__compute_xi(rot_angle_deg)
        self.__compute_limits()

    # ---- internals
    def __compute_limits(self):
        def mm(col): return (float(np.min(col)), float(np.max(col)))
        self.xlim  = mm(self.data_[:, DataColumn.X])
        self.ylim  = mm(self.data_[:, DataColumn.Y])
        self.zlim  = mm(self.data_[:, DataColumn.Z])
        xi_col = self._idx_XI if self._idx_XI is not None else int(DataColumn.XI)
        xi_col = min(xi_col, self.data_.shape[1]-1)
        self.xilim = mm(self.data_[:, xi_col])

    def __gridded(self, data):
        return np.flipud(np.reshape(data, (self.height_px_, self.width_px_)))

    def __contour_field(self, column):
        col = int(column)
        if col >= self.data_.shape[1]:
            raise IndexError(f"Requested column {col} not in data (ncols={self.data_.shape[1]}).")
        return self.__gridded(self.data_[:, col])

    def __interpolator(self, data_column):
        XI, Z = self.cntr([DataColumn.XI, DataColumn.Z])
        values = self.__gridded(self.data_[:, int(data_column)])
        return spi.RegularGridInterpolator(
            (XI[0, :].flatten(), Z[:, 0].flatten()), values.T, method="linear"
        )

    def __scale_col_if_present(self, col, s):
        col = int(col) if not isinstance(col, int) else col
        if 0 <= col < self.data_.shape[1]:
            self.data_[:, col] /= s

    def __compute_xi(self, rot_angle_deg: float):
        x, y = self.data_[:, DataColumn.X], self.data_[:, DataColumn.Y]
        u, v = self.data_[:, DataColumn.U], self.data_[:, DataColumn.V]

        # stdU/stdV dosyada var (7-9). Yine de güvenli okuyoruz:
        su = self.data_[:, DataColumn.stdU] if int(DataColumn.stdU) < self.data_.shape[1] else np.zeros_like(u)
        sv = self.data_[:, DataColumn.stdV] if int(DataColumn.stdV) < self.data_.shape[1] else np.zeros_like(v)

        xi, _      = compute_xi_component(x, y, rot_angle_deg)
        uxi, un    = compute_xi_component(u, v, rot_angle_deg)
        std_uxi, _ = compute_xi_component(su, sv, rot_angle_deg)

        n0 = self.data_.shape[1]
        self.data_ = np.hstack((self.data_, xi[:,None], uxi[:,None], un[:,None], std_uxi[:,None]))
        self._idx_XI, self._idx_Uxi, self._idx_Un, self._idx_stdUxi = n0, n0+1, n0+2, n0+3

    # ---- public API
    def scale(self, length: float = 1000.0, vel: float = 0.151):
        for col in (DataColumn.X, DataColumn.Y, DataColumn.Z, self._idx_XI):
            self.__scale_col_if_present(col, length)
        self.__compute_limits()

        for col in (DataColumn.U, DataColumn.V, DataColumn.W,
                    self._idx_Uxi, DataColumn.magVel,
                    DataColumn.stdU, DataColumn.stdV, DataColumn.stdW, self._idx_stdUxi):
            self.__scale_col_if_present(col, vel)
        # TKE yok → dokunmuyoruz

    def cntr(self, columns):
        return [self.__contour_field(c) for c in columns]

    def strm(self, n_div=50):
        x = np.linspace(*self.xilim, n_div)
        z = np.linspace(*self.zlim,  n_div)
        X, Z = np.meshgrid(x, z)
        U = self.__interpolator(self._idx_Uxi)((X.flatten(), Z.flatten()))
        V = self.__interpolator(DataColumn.W)((X.flatten(), Z.flatten()))
        return [X, Z, U.reshape(n_div, n_div), V.reshape(n_div, n_div)]

    def at_z(self, z_coord, variable, n_pts=50):
        xi = np.linspace(self.xilim[0], self.xilim[1], n_pts)
        z = np.full_like(xi, z_coord)
        return xi, self.__interpolator(variable)((xi, z))

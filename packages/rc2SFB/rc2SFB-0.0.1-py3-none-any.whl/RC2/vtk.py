from __future__ import annotations
import numpy as np
from numpy.typing import ArrayLike
from dataclasses import dataclass
from scipy.interpolate import griddata
import vtk
from .common import compute_xi_component, in_range

class VTKData:
    def __init__(self, filename: str, rot_angle_deg: float):
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(filename)
        reader.Update()
        data = reader.GetOutput()

        self._read_mesh(data)
        self._read_U(data, reader)
        self._compute_xi(rot_angle_deg)

    def _read_mesh(self, data):
        pts = data.GetPoints()
        n = pts.GetNumberOfPoints()
        self.x = np.zeros(n); self.y = np.zeros(n); self.z = np.zeros(n)
        for i in range(n):
            self.x[i], self.y[i], self.z[i] = pts.GetPoint(i)

        raw = data.GetPolys().GetData()
        ntri = raw.GetNumberOfTuples() // 4
        self.tri = np.zeros((ntri, 3), dtype=int)
        for i in range(ntri):
            self.tri[i, :] = (
                int(raw.GetTuple(4*i + 1)[0]),
                int(raw.GetTuple(4*i + 2)[0]),
                int(raw.GetTuple(4*i + 3)[0]),
            )

    def _field_index(self, name: str, reader) -> int:
        n = reader.GetOutput().GetPointData().GetNumberOfArrays()
        fields = [reader.GetOutput().GetPointData().GetArrayName(i) for i in range(n)]
        return fields.index(name) if name in fields else -1

    def _read_U(self, data, reader, name: str = "U") -> None:
        arr = data.GetPointData().GetArray(self._field_index(name, reader))
        n = arr.GetNumberOfTuples()
        self.ux = np.zeros(n); self.uy = np.zeros(n); self.uz = np.zeros(n)
        for i in range(n):
            self.ux[i], self.uy[i], self.uz[i] = arr.GetTuple(i)

    def _compute_xi(self, ang: float) -> None:
        self.xi, _ = compute_xi_component(self.x, self.y, ang)
        self.uxi, self.un = compute_xi_component(self.ux, self.uy, ang)

    # -------- transforms --------
    def translate(self, x: float, y: float, z: float) -> None:
        self.x += x; self.y += y; self.z += z

    def scale(self, length: float = 1000.0, vel: float = 0.151) -> None:
        self.x /= length; self.y /= length; self.z /= length; self.xi /= length
        self.ux /= vel; self.uy /= vel; self.uz /= vel; self.uxi /= vel; self.un /= vel

    # -------- utilities --------
    def tris_in_range(self, x_lims, y_lims, margin: float = 0.05, x_name="xi", y_name="z"):
        keep = np.zeros(self.tri.shape[0], dtype=bool)
        x = getattr(self, x_name); y = getattr(self, y_name)
        for i, t in enumerate(self.tri):
            for p in t:
                pi = int(p)
                keep[i] |= in_range([x[pi], y[pi]], x_lims, y_lims, margin)
        return self.tri[keep, :]

    def at_z(self, xi_bounds, z_coord: float, array: np.ndarray, n_pts: int = 50):
        xi = np.linspace(xi_bounds[0], xi_bounds[1], n_pts)
        z  = np.full_like(xi, z_coord, dtype=float)
        return xi, griddata((self.xi, self.z), array, (xi, z))

    def for_streams(self, x_lim, y_lim):
        gx, gy = np.mgrid[x_lim[0]:x_lim[1]:100j, y_lim[0]:y_lim[1]:100j]
        uxi = griddata((self.xi, self.z), self.uxi, (gx.ravel(), gy.ravel()))
        uz  = griddata((self.xi, self.z), self.uz,  (gx.ravel(), gy.ravel()))
        return gx.T, gy.T, uxi.reshape(gx.shape).T, uz.reshape(gx.shape).T


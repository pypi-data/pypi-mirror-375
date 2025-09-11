import numpy as np
from numpy.typing import ArrayLike
from dataclasses import dataclass
from scipy.interpolate import griddata
import vtk
from .common import compute_xi_component, in_range

class VTUSlice:
    @dataclass
    class Vector: x: ArrayLike; y: ArrayLike; z: ArrayLike

    def __field_index(self, name, reader):
        n = reader.GetOutput().GetPointData().GetNumberOfArrays()
        names = [reader.GetOutput().GetPointData().GetArrayName(i) for i in range(n)]
        try: return names.index(name)
        except ValueError: return -1

    def __read_vector(self, name: str, data, reader, attr_name: str | None = None):
        arr = data.GetPointData().GetArray(self.__field_index(name, reader))
        n = arr.GetNumberOfTuples()
        if attr_name is None: attr_name = name
        setattr(self, attr_name, self.Vector(np.zeros(n), np.zeros(n), np.zeros(n)))
        vec = getattr(self, attr_name)
        for i in range(n):
            vec.x[i], vec.y[i], vec.z[i] = arr.GetTuple(i)

class VTKData:
    def __init__(self, filename, rot_angle_deg):
        reader = vtk.vtkXMLPolyDataReader()
        reader.SetFileName(filename)
        reader.Update()
        data = reader.GetOutput()

        # points
        points = data.GetPoints()
        npts = points.GetNumberOfPoints()
        self.x, self.y, self.z = np.zeros(npts), np.zeros(npts), np.zeros(npts)
        for i in range(npts):
            self.x[i], self.y[i], self.z[i] = points.GetPoint(i)

        # triangles (cells)
        tris = data.GetPolys().GetData()
        ntri = int(tris.GetNumberOfTuples() / 4)
        self.tri = np.zeros((ntri, 3))
        for i in range(ntri):
            self.tri[i, :] = (
                tris.GetTuple(4 * i + 1)[0],
                tris.GetTuple(4 * i + 2)[0],
                tris.GetTuple(4 * i + 3)[0],
            )

        # velocity
        name = "U"  # adjust if your field is 'UMean'
        U = data.GetPointData().GetArray(self.__field_index(name, reader))
        if U is None:
            raise RuntimeError(f"Field '{name}' not found in {filename}")
        nv = U.GetNumberOfTuples()
        self.ux, self.uy, self.uz = np.zeros(nv), np.zeros(nv), np.zeros(nv)
        for i in range(nv):
            self.ux[i], self.uy[i], self.uz[i] = U.GetTuple(i)

        # rotated coordinates/components
        self.xi, _ = compute_xi_component(self.x,  self.y,  rot_angle_deg)
        self.uxi, self.un = compute_xi_component(self.ux, self.uy, rot_angle_deg)

    def __field_index(self, name, reader):
        n = reader.GetOutput().GetPointData().GetNumberOfArrays()
        names = [reader.GetOutput().GetPointData().GetArrayName(i) for i in range(n)]
        try: return names.index(name)
        except ValueError: return -1

    # transforms
    def translate(self, x, y, z):
        self.x += x; self.y += y; self.z += z

    def scale(self, length=1000.0, vel=0.151):
        self.x  /= length; self.y  /= length; self.z  /= length; self.xi /= length
        self.ux /= vel;    self.uy /= vel;    self.uz /= vel;    self.uxi/= vel; self.un/=vel

    # queries
    def tris_in_range(self, x_lims, y_lims, margin=0.05, x_name="xi", y_name="z"):
        kept = np.full(self.tri.shape[0], False)
        x = getattr(self, x_name); y = getattr(self, y_name)
        for i, t in enumerate(self.tri):
            for p in t:
                pi = int(p)
                kept[i] = kept[i] or in_range([x[pi], y[pi]], x_lims, y_lims, margin)
        return self.tri[kept, :]

    def at_z(self, xi_bounds, z_coord, array, n_pts=50):
        xi = np.linspace(xi_bounds[0], xi_bounds[1], n_pts)
        z  = np.full_like(xi, z_coord)
        return xi, griddata((self.xi, self.z), array, (xi, z))

    def for_streams(self, x_lim, y_lim):
        grid_x, grid_y = np.mgrid[x_lim[0]:x_lim[1]:100j, y_lim[0]:y_lim[1]:100j]
        uxi = griddata((self.xi, self.z), self.uxi, (grid_x.flatten(), grid_y.flatten()))
        uz  = griddata((self.xi, self.z), self.uz,  (grid_x.flatten(), grid_y.flatten()))
        return (grid_x.T, grid_y.T, uxi.reshape(grid_x.shape).T, uz.reshape(grid_x.shape).T)

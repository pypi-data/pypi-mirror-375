from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Iterable, Mapping
from .piv import PIVData
from .vtk import VTKData

@dataclass(frozen=True)
class Scale:
    length: float
    vel: float
    translate_xyz: tuple[float, float, float] = (0.0, 0.0, 0.0)

@dataclass(frozen=True)
class FilePatterns:
    """Filename patterns with placeholders."""
    piv_dir_by_Re: Mapping[int, str]                   # {100: "/path/Re100", ...}
    piv_pattern: str = "{prefix}_Pos{pos:02d}_Re{Re}_B0001_T.dat"
    vtk_pattern: str = "Re{Re}_{prefix}_Pos{pos:02d}.vtp"

@dataclass
class ReaderConfig:
    Res: Iterable[int]
    positions: Iterable[int]                           # e.g. [1,3]
    prefixes: Iterable[str]                            # e.g. ["S","L17","L16","L15"]
    piv_sizes: Mapping[tuple[int,int,str], tuple[int,int,int]]  # (Re,pos,prefix)->(w,h,rot_deg)
    scales_by_Re: Mapping[int, Scale]
    of_dir: str | None = None                          # base dir for OF VTK files (optional)

def _iter_leaves(tree: dict):
    for k, v in tree.items():
        if isinstance(v, dict):
            yield from _iter_leaves(v)
        else:
            yield k, v

def read_piv_data_tree(fp: FilePatterns, cfg: ReaderConfig) -> Dict[int, Dict[int, Dict[str, PIVData]]]:
    out: Dict[int, Dict[int, Dict[str, PIVData]]] = {}
    for Re in cfg.Res:
        out[Re] = {}
        for pos in cfg.positions:
            out[Re][pos] = {}
            for prefix in cfg.prefixes:
                w, h, rot = cfg.piv_sizes[(Re, pos, prefix)]
                piv_dir = fp.piv_dir_by_Re[Re].rstrip("/")
                path = f"{piv_dir}/{fp.piv_pattern.format(prefix=prefix, pos=pos, Re=Re)}"
                piv = PIVData(path, w, h, rot)
                out[Re][pos][prefix] = piv
        sc = cfg.scales_by_Re[Re]
        for _, obj in _iter_leaves(out[Re]):
            obj.scale(length=sc.length, vel=sc.vel)
    return out

def read_of_tree(fp: FilePatterns, cfg: ReaderConfig) -> Dict[int, Dict[int, Dict[str, VTKData]]]:
    if not cfg.of_dir:
        return {}
    out: Dict[int, Dict[int, Dict[str, VTKData]]] = {}
    rot_map = {"S": 0, "L17": -30, "L16": -60, "L15": -90, "L14": -120, "L13": -150}
    for Re in cfg.Res:
        out[Re] = {}
        sc = cfg.scales_by_Re[Re]
        tx, ty, tz = sc.translate_xyz
        for pos in cfg.positions:
            out[Re][pos] = {}
            for prefix in cfg.prefixes:
                vf = f"{cfg.of_dir.rstrip('/')}/{fp.vtk_pattern.format(Re=Re, prefix=prefix, pos=pos)}"
                vtk = VTKData(vf, rot_angle_deg=rot_map.get(prefix, 0))
                vtk.scale(sc.length, sc.vel)
                if any(abs(v) > 0 for v in (tx, ty, tz)):
                    vtk.translate(tx, ty, tz)
                out[Re][pos][prefix] = vtk
    return out

def read_all_data(fp: FilePatterns, cfg: ReaderConfig):
    """Return (PIV, OF). OF may be an empty dict if cfg.of_dir is None."""
    return read_piv_data_tree(fp, cfg), read_of_tree(fp, cfg)

from __future__ import annotations
import argparse
import numpy as np
import matplotlib.pyplot as plt

from .data_readers import FilePatterns, ReaderConfig, Scale
from .plotting import compute_piv_limits, plot_exp_grid, plot_sim_exp_comparison
from .core import read_all_data

def _build_cfg(args) -> tuple[FilePatterns, ReaderConfig]:
    prefixes = ["S","L17","L16","L15"] if args.prefixes is None else args.prefixes

    def default_size(Re, pos, pref):
        rot = {"S":0,"L17":-30,"L16":-60,"L15":-90,"L14":-120,"L13":-150}.get(pref,0)
        # sensible, override via piv-sizes in code if needed
        return (360, 335, rot) if pref=="S" else (208, 33, rot)

    piv_sizes = {(Re,pos,p): default_size(Re,pos,p) for Re in args.Re for pos in args.pos for p in prefixes}
    scales = {
        Re: Scale(length=args.length_scale, vel=args.vel_scale,
                  translate_xyz=tuple(args.translate) if args.translate else (0.0,0.0,0.0))
        for Re in args.Re
    }

    piv_dirs = {Re: args.piv_dir.format(Re=Re) for Re in args.Re}
    fp = FilePatterns(
        piv_dir_by_Re=piv_dirs,
        piv_pattern=args.piv_pattern,
        vtk_pattern=args.vtk_pattern,
    )

    cfg = ReaderConfig(
        Res=args.Re,
        positions=args.pos,
        prefixes=prefixes,
        piv_sizes=piv_sizes,
        scales_by_Re=scales,
        of_dir=args.of_dir
    )
    return fp, cfg

def app():
    p = argparse.ArgumentParser(prog="rc2flow", description="RC2 plotting (PIV + OF only)")
    p.add_argument("--Re", nargs="+", type=int, default=[100,150,200])
    p.add_argument("--pos", nargs="+", type=int, default=[1,3])
    p.add_argument("--prefixes", nargs="+", default=["S","L17","L16","L15"])
    p.add_argument("--piv-dir", required=True, help="Template like '/data/preliminary-Re{Re}'")
    p.add_argument("--piv-pattern", default="{prefix}_Pos{pos:02d}_Re{Re}_B0001_T.dat")
    p.add_argument("--of-dir", help="Base dir for OF VTK files")
    p.add_argument("--vtk-pattern", default="Re{Re}_{prefix}_Pos{pos:02d}.vtp")
    p.add_argument("--length-scale", type=float, default=10.0)
    p.add_argument("--vel-scale", type=float, default=10.0)
    p.add_argument("--translate", nargs=3, type=float, help="x y z translation applied to VTK per Re")
    p.add_argument("--mode", choices=["exp-grid","compare"], default="exp-grid")
    p.add_argument("--pos-for-compare", type=int, default=1)
    p.add_argument("--xlim", nargs=2, type=float)
    p.add_argument("--zS", nargs=2, type=float); p.add_argument("--zL17", nargs=2, type=float); p.add_argument("--zL16", nargs=2, type=float)
    p.add_argument("--save", help="output path (e.g. results/plot.pdf)")
    args = p.parse_args()

    fp, cfg = _build_cfg(args)
    PIV, OF = read_all_data(fp, cfg)

    cbarticks = np.linspace(-2, 6, 20)
    strml_opts_S = {"density": 1.0, "color": "k", "linewidth": 1.0}
    strml_opts_L = {"density": 0.75, "color": "k", "linewidth": 0.5}

    if args.mode == "exp-grid":
        Re0 = args.Re[0]
        xlim_piv, zlim_piv = compute_piv_limits(PIV[Re0])
        fig, ax = plot_exp_grid(PIV[Re0], cbarticks, strml_opts_L, strml_opts_S, zlim_piv, xlim_piv)
    else:
        Re0 = args.Re[0]
        pos = args.pos_for_compare
        piv_pos = PIV[Re0][pos]
        xlim_piv = tuple(args.xlim) if args.xlim else (
            min(v.xilim[0] for v in piv_pos.values()),
            max(v.xilim[1] for v in piv_pos.values())
        )
        zlim_piv = {
            "S": tuple(args.zS) if args.zS else piv_pos["S"].zlim,
            "L17": tuple(args.zL17) if args.zL17 else piv_pos["L17"].zlim,
            "L16": tuple(args.zL16) if args.zL16 else piv_pos["L16"].zlim,
        }
        if not OF:
            raise SystemExit("compare mode requires --of-dir (OF data).")
        fig, ax = plot_sim_exp_comparison(
            PIV=PIV[Re0][pos], OF=OF[Re0][pos],
            cbarticks=cbarticks, strml_opts_L=strml_opts_L, strml_opts_S=strml_opts_S,
            xlim_piv=xlim_piv, zlim_piv=zlim_piv
        )

    if args.save:
        import pathlib
        pathlib.Path(args.save).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(args.save, bbox_inches="tight")
    else:
        plt.show()


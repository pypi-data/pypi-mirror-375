from __future__ import annotations
from typing import Dict, Tuple
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from .piv import PIVData, DataColumn
from .vtk import VTKData

def span(lim: tuple[float, float]) -> float:
    return lim[1] - lim[0]

def compute_piv_limits(PIV_pos_tree: Dict[int, Dict[str, PIVData]]):
    """PIV_pos_tree: {pos: {prefix: PIVData}} → (xlim_by_pos, zlim_by_prefix)"""
    x_by_pos = {
        pos: (
            min(p.xilim[0] for p in PIV_pos_tree[pos].values()),
            max(p.xilim[1] for p in PIV_pos_tree[pos].values()),
        )
        for pos in PIV_pos_tree
    }
    z_by_prefix: Dict[str, Tuple[float, float]] = {}
    sample_pos = next(iter(PIV_pos_tree))
    for pref in PIV_pos_tree[sample_pos]:
        z_by_prefix[pref] = (
            min(PIV_pos_tree[pos][pref].zlim[0] for pos in PIV_pos_tree if pref in PIV_pos_tree[pos]),
            max(PIV_pos_tree[pos][pref].zlim[1] for pos in PIV_pos_tree if pref in PIV_pos_tree[pos]),
        )
    return x_by_pos, z_by_prefix

def PIV_cmap_strm(ax, PIV: PIVData, columns: list[DataColumn], cbarticks, strml_opts, streams_interp_density=200, do_streams=True, cmap_name="jet"):
    c = ax.contourf(*PIV.cntr(columns), cbarticks, cmap=mpl.colormaps[cmap_name])
    if do_streams:
        ax.streamplot(*PIV.strm(streams_interp_density), **strml_opts)
    return c

def VTK_cmap_strm(ax, VTK: VTKData, fieldname: str, cbarticks, xilim: Tuple[float,float], zlim: Tuple[float,float], strml_opts, do_streams=True, cmap_name="jet"):
    c = ax.tricontourf(
        VTK.xi, VTK.z, VTK.tris_in_range(xilim, zlim),
        getattr(VTK, fieldname), cbarticks, cmap=mpl.colormaps[cmap_name]
    )
    if do_streams:
        ax.streamplot(*VTK.for_streams(xilim, zlim), **strml_opts)
    return c

def plot_exp_grid(PIV_by_pos: Dict[int, Dict[str, PIVData]], cbarticks, strml_opts_L, strml_opts_S, zlim_piv, xlim_piv, plotted_column=DataColumn.W):
    fig, ax = plt.subplots(
        4, 2, layout="tight", sharex="col", sharey="row",
        width_ratios=[span(xlim_piv[1]), span(xlim_piv[3])],
        height_ratios=[span(zlim_piv["S"]), span(zlim_piv["L17"]), span(zlim_piv["L16"]), span(zlim_piv.get("L15",(14,15)))]
    )

    rows = [("S", strml_opts_S), ("L17", strml_opts_L), ("L16", strml_opts_L), ("L15", strml_opts_L)]
    for i, (pref, so) in enumerate(rows):
        if pref not in PIV_by_pos[1] or pref not in PIV_by_pos[3]:
            continue
        PIV_cmap_strm(ax[i,0], PIV_by_pos[1][pref], [DataColumn.XI, DataColumn.Z, plotted_column], cbarticks, so)
        PIV_cmap_strm(ax[i,1], PIV_by_pos[3][pref], [DataColumn.XI, DataColumn.Z, plotted_column], cbarticks, so)

    [a.set_xlim(l) for l,a in zip([xlim_piv[1], xlim_piv[3]], ax[0,:])]
    [a.set_ylim(l) for l,a in zip([zlim_piv["S"], (16,17), (15,16), zlim_piv.get("L15",(14,15))], ax[:,0])]
    [a.set_aspect("equal") for a in ax.flat]
    [a.set_xlabel(r"$\xi/B$") for a in ax[-1,:]]
    [a.set_ylabel(r"$z/B$") for a in ax[:,0]]
    [a.set_title(t) for a,t in zip(ax[0,:], ["Position 01","Position 03"])]
    [ax[i,-1].text(1,0.5, t, transform=ax[i,-1].transAxes, va="center", ha="center", rotation=-90)
        for i,t in enumerate(["S (freeboard)","L17","L16","L15"]) if i < ax.shape[0]]

    cbar_ax = fig.add_axes([1.0, 0.35, 0.025, 0.30])
    c = ax[-1,-1].collections[-1]
    fig.colorbar(c, cax=cbar_ax)
    cbar_ax.set_yticks(cbarticks[::4]); cbar_ax.set_xlabel(r"$w/\langle w \rangle $")
    return fig, ax

def plot_sim_exp_comparison(PIV: Dict[str, PIVData], OF: Dict[str, VTKData], cbarticks, strml_opts_L, strml_opts_S, xlim_piv, zlim_piv):
    """PIV vs OF (BRO yok)."""
    fig, ax = plt.subplots(
        3, 2, sharex="col", sharey="row",
        width_ratios=[span(xlim_piv), span(xlim_piv)],
        height_ratios=[span(zlim_piv["S"]), span(zlim_piv["L17"]), span(zlim_piv["L16"])],
        figsize=(6.5, 4)
    )
    for i,pref in enumerate(["S","L17","L16"]):
        PIV_cmap_strm(ax[i,0], PIV[pref], [DataColumn.XI, DataColumn.Z, DataColumn.W], cbarticks, strml_opts_S if pref=="S" else strml_opts_L)
        c1 = VTK_cmap_strm(ax[i,1], OF[pref], "uz", cbarticks, xlim_piv, zlim_piv[pref], strml_opts_L if pref!="S" else strml_opts_S)

    [a.set_xlim(xlim_piv) for a in ax[0,:]]
    [a.set_ylim(l) for l,a in zip([zlim_piv["S"], (16,17), (15,16)], ax[:,0])]
    [a.set_aspect("equal") for a in ax.flat]
    [a.set_xlabel(r"$\xi/B$") for a in ax[-1,:]]
    [a.set_title(t) for a,t in zip(ax[0,:], ["PIV","boundary-conforming"])]
    [ax[i,-1].text(1,0.5, t, transform=ax[i,-1].transAxes, va="center", ha="center", rotation=-90)
        for i,t in enumerate(["S (freeboard)","L17","L16"])]

    cbar_ax = fig.add_axes([0.92, 0.35, 0.025, 0.30])
    fig.colorbar(c1, cax=cbar_ax)
    cbar_ax.set_yticks(cbarticks[::4]); cbar_ax.set_xlabel(r"$w/\langle w \rangle $")
    ax[1,0].set_yticklabels(["","17"]); ax[0,0].set_ylabel(r"$z/B$", loc="bottom")
    return fig, ax

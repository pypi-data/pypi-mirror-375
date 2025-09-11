from __future__ import annotations
from .data_readers import FilePatterns, ReaderConfig, read_piv_data_tree, read_of_tree

def read_all_data(piv_fp: FilePatterns, cfg: ReaderConfig):
    """Return (PIV, OF) — BRO removed."""
    PIV = read_piv_data_tree(piv_fp, cfg)
    OF  = read_of_tree(piv_fp, cfg)
    return PIV, OF


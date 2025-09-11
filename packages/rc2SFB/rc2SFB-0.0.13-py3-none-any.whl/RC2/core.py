from .data_readers import FilePatterns, ReaderConfig, read_piv_data_tree, read_of_tree

def read_all_data(fp: FilePatterns, cfg: ReaderConfig):
    """Return (PIV, OF). OF may be {} if cfg.of_dir is None."""
    return read_piv_data_tree(fp, cfg), read_of_tree(fp, cfg)

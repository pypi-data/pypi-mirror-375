try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from ._reader import napari_get_reader
from ._sample_data import make_sample_data
from ._widget import (
    individual_tree,
)
from ._writer import write_multiple, write_single_image
from segtree.utils import get_base_dir
__all__ = (
    "napari_get_reader",
    "write_single_image",
    "write_multiple",
    "make_sample_data",
    "individual_tree",
)

import os

checkpoint = os.path.join(get_base_dir(),"segtree","sam2.1_hq_hiera_large.pt")
segtree_pth = os.path.join(get_base_dir(),"segtree")
A = [ix for ix in os.listdir(segtree_pth) if ix.endswith(".pt")]
if 'sam2.1_hq_hiera_large.pt' in A:
    pass
else:
    import requests
    sam2p1_hq_hiera_l_url="https://huggingface.co/lkeab/hq-sam/resolve/main/sam2.1_hq_hiera_large.pt?download=true"
    save_path = os.path.join(get_base_dir(),"segtree","sam2.1_hq_hiera_large.pt")
    response = requests.get(sam2p1_hq_hiera_l_url, stream=True)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download completed successfully.")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
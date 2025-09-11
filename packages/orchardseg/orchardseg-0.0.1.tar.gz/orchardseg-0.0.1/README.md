# 🌳 Segtree

[![License BSD-3](https://img.shields.io/pypi/l/segtree.svg?color=green)](https://github.com/hereariim/segtree/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/segtree.svg?color=green)](https://pypi.org/project/segtree)
[![Python Version](https://img.shields.io/pypi/pyversions/segtree.svg?color=green)](https://python.org)
[![tests](https://github.com/hereariim/segtree/workflows/tests/badge.svg)](https://github.com/hereariim/segtree/actions)
[![codecov](https://codecov.io/gh/hereariim/segtree/branch/main/graph/badge.svg)](https://codecov.io/gh/hereariim/segtree)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/segtree)](https://napari-hub.org/plugins/segtree)
[![npe2](https://img.shields.io/badge/plugin-npe2-blue?link=https://napari.org/stable/plugins/index.html)](https://napari.org/stable/plugins/index.html)
[![Copier](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/copier-org/copier/master/img/badge/badge-grayscale-inverted-border-purple.json)](https://github.com/copier-org/copier)

Segtree is a plugin designed for the segmentation of individual trees from imagery. It isolates tree in ovelapping tree context.

**Input:** RGB images or preprocessed point clouds.

**Output:** Binary masks of segmentated tree.

![alt text](<Screenshot from 2025-09-10 17-01-24.png>)

## How it works

The user provides as input a **color image** and, optionally, a **trunk detector mask**.
With a single click, the plugin automatically places prompt points on the detected trunk labels. These prompts are then used by [SAM2 HQ](https://github.com/SysCV/sam-hq/blob/main/sam-hq2/README.md#citing-hq-sam-2) (Segment Anything Model v2, High Quality mode) to segment the tree foliage associated with each trunk.

![alt text](<Screenshot from 2025-09-10 15-30-09.png>)

<!--
Don't miss the full getting started guide to set up your new package:
https://github.com/napari/napari-plugin-template#getting-started

and review the napari docs for plugin developers:
https://napari.org/stable/plugins/index.html
-->

## Article : Individual Segmentation of Intertwined Apple Trees in a Row via Prompt Engineering

METUAREA, Herearii, LAURENS, François, GUERRA, Walter, et al. [Individual Segmentation of Intertwined Apple Trees in a Row via Prompt Engineering](https://www.mdpi.com/1424-8220/25/15/4721). Sensors, 2025, vol. 25, no 15, p. 4721.

## Citing segtree

If you find segtree useful in your research, please star ⭐ this repository and consider citing 📝:

```
@article{metuarea2025individual,
  title={Individual Segmentation of Intertwined Apple Trees in a Row via Prompt Engineering},
  author={Metuarea, Herearii and Laurens, Fran{\c{c}}ois and Guerra, Walter and Lozano, Lidia and Patocchi, Andrea and Van Hoye, Shauny and Dutagaci, Helin and Labrosse, Jeremy and Rasti, Pejman and Rousseau, David},
  journal={Sensors},
  volume={25},
  number={15},
  pages={4721},
  year={2025},
  publisher={MDPI}
}
```

## Installation

You can install `segtree` via [pip]:

    pip install segtree



To install latest development version :

    pip install git+https://github.com/hereariim/segtree.git


## Contact

Imhorphen team, bioimaging research group

42 rue George Morel, Angers, France

- Pr David Rousseau, david.rousseau@univ-angers.fr
- Herearii Metuarea, herearii.metuarea@univ-angers.fr


## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"segtree" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[copier]: https://copier.readthedocs.io/en/stable/
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[napari-plugin-template]: https://github.com/napari/napari-plugin-template

[file an issue]: https://github.com/hereariim/segtree/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/

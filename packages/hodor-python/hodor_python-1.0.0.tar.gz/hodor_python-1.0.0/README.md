
# 🐟🐍 HODOR Python API

**A Python package for programmatic access, download, and analysis of the [HODOR dataset](https://github.com/TAWilts/HODOR).**

---

## About the HODOR Dataset

HODOR (Hydroacoustic and Optical Dataset for Oceanic Research) is a large, open-access dataset of synchronized underwater stereo video and sonar recordings, with detailed animal activity counts. The main HODOR data repository and documentation are available at: [https://github.com/TAWilts/HODOR](https://github.com/TAWilts/HODOR)

This package provides a convenient Python interface to access, download, and analyze HODOR data. It is installable via PyPI and designed for easy integration with pandas and scientific workflows.

---

## Features

- Download HODOR activity counts, stereo video, and sonar data by sequence ID
- Filter and analyze metadata and animal activity using pandas DataFrames
- Download only the data you need (safe, repeatable, skips files already present)
- Enum-based filtering for species
- Simple API for targeted or bulk downloads

---

## Installation

```bash
pip install hodor-python
```

---

## Quickstart

```python
from hodor_python import HODOR_Dataset, Species

# Set a local folder for data storage
hodor = HODOR_Dataset(dataset_folder="/path/to/hodor_data")

# Access activity counts as a pandas DataFrame
df = dataset.counts

# Filter for sequences with high cod activity
cod_sequences = df[df[Species.FISH_COD] > 0]

# Download video and sonar for a specific sequence
hodor.download_sequence(1)
```

For more in-depth examples using the API, have a look at: 

https://github.com/TAWilts/HODOR/tree/main/meta/hodor_python


---

## API Overview

### `HODOR_Dataset`

- `HODOR_Dataset(dataset_folder: str)` – Main entry point. Manages local cache and access.
- `.counts` – Returns a pandas DataFrame with sequence metadata and activity counts.
- `.download_video(sequence_ids)` – Download stereo video for one or more sequence IDs.
- `.download_sonar(sequence_ids)` – Download sonar data for one or more sequence IDs.
- `.download_sequence(sequence_ids)` – Download both video and sonar for one or more sequence IDs.

### `Species` Enum

Use for filtering DataFrame columns by species (e.g., `Species.FISH_COD`).

---

## More Information

- Main HODOR data repository: [https://github.com/TAWilts/HODOR](https://github.com/TAWilts/HODOR)
- Data is hosted on [PANGAEA](https://doi.pangaea.de/10.1594/PANGAEA.980000), with DOIs for each subset.

---

## License

See [LICENSE](LICENSE).

---

## Citation

If you use HODOR in your research, please cite the main dataset as:

```bibtex
@ARTICLE{11121653,
  author={Wilts, Thomas and Böer, Gordon and Winkler, Julian and Cisewski, Boris and Schramm, Hauke and Badri-Hoeher, Sabah},
  journal={IEEE Data Descriptions}, 
  title={Descriptor: Hydroacoustic and Optical Dataset for Oceanic Research (HODOR)}, 
  year={2025},
  volume={},
  number={},
  pages={1-9},
  keywords={Sonar;Cameras;Optical sensors;Optical imaging;Biomedical optical imaging;Fish;Optical recording;Acoustics;Synchronization;Sonar measurements},
  doi={10.1109/IEEEDATA.2025.3596913}}
```

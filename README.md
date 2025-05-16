# GeoJSON Waypoint Synthesizer

A Python utility to generate a new sequence of waypoints that “resembles” a user-provided trajectory, sampling from a larger database of GeoJSON points. The output is a GeoJSON LineString whose step-lengths and bearings mimic the input path but live entirely within your database.

---

## Features

- **Input & output in GeoJSON**  
  Read from and write to standard GeoJSON FeatureCollections.
- **Step-wise feature matching**  
  Extracts distances and bearings between successive points of the input path.
- **Fast nearest-neighbor lookup**  
  Uses a haversine-metric KD-tree for geospatial indexing of your database.
- **Variability via top-k sampling**  
  Randomly choose among the _k_ closest matches at each step to avoid degenerate outputs.
- **Single-line output**  
  Generates a `LineString` Feature preserving input path length and structure.

---

## Installation

```bash
# Create & activate a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install numpy scikit-learn

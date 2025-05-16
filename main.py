import numpy as np
from sklearn.neighbors import KDTree
import math

def haversine(pt1, pt2):
    """Calculate the Haversine distance (meters) between two (lon, lat) points."""
    lon1, lat1 = np.radians(pt1)
    lon2, lat2 = np.radians(pt2)
    dlon, dlat = lon2 - lon1, lat2 - lat1
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    return 6371000 * 2 * np.arcsin(np.sqrt(a))

def bearing(pt1, pt2):
    """Calculate bearing (radians) from pt1→pt2."""
    lon1, lat1 = np.radians(pt1)
    lon2, lat2 = np.radians(pt2)
    y = math.sin(lon2 - lon1) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)
    return math.atan2(y, x)

def generate_waypoints_geojson(input_geojson, db_geojson, k=5):
    """
    Given:
      - input_geojson: GeoJSON FeatureCollection of Points in order
      - db_geojson:   GeoJSON FeatureCollection of Points (the database)
      - k:            number of nearest neighbors to sample from
    Returns:
      - GeoJSON FeatureCollection containing a single LineString feature
        whose coordinates mimic the input trajectory.
    """
    # Extract ordered input coords [(lon,lat), ...]
    input_coords = [feat["geometry"]["coordinates"] for feat in input_geojson["features"]]
    
    # Build database array and KD-tree (in radians)
    db_coords = np.array([feat["geometry"]["coordinates"] for feat in db_geojson["features"]])
    tree = KDTree(np.radians(db_coords), metric='haversine')
    
    # Compute (distance, bearing) for each step in input
    steps = []
    for i in range(len(input_coords) - 1):
        d = haversine(input_coords[i], input_coords[i + 1])
        b = bearing(input_coords[i], input_coords[i + 1])
        steps.append((d, b))
    
    # Initialize new sequence starting from a random DB point
    idx = np.random.choice(len(db_coords))
    new_seq = [tuple(db_coords[idx])]
    
    # Generate new points
    for d_target, b_target in steps:
        lon0, lat0 = new_seq[-1]
        # Project next point approximation
        R = 6371000.0
        d_frac = d_target / R
        lat_pred = lat0 + np.degrees(d_frac * math.cos(b_target))
        lon_pred = lon0 + np.degrees(d_frac * math.sin(b_target) / math.cos(np.radians(lat0)))
        
        # Query k nearest DB points
        dist, ind = tree.query(np.radians([[lon_pred, lat_pred]]), k=k)
        chosen = db_coords[np.random.choice(ind[0])]
        new_seq.append(tuple(chosen))
    
    # Build output GeoJSON LineString
    output = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "LineString",
                    "coordinates": new_seq
                }
            }
        ]
    }
    return output

# Example usage (assuming 'input.geojson' and 'db.geojson' on disk):
# with open("input.geojson") as f:
#     input_gc = json.load(f)
# with open("db.geojson") as f:
#     db_gc = json.load(f)
# output_gc = generate_waypoints_geojson(input_gc, db_gc)
# print(json.dumps(output_gc, indent=2))

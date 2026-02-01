import csv
import io
from fastapi import APIRouter
from typing import List
from app.models.location import Location
from app.models.geology import GeologicalLayer

router = APIRouter(prefix="/export", tags=["Export"])

@router.post("/civil3d")
def export_civil3d(
    locations: List[Location],
    layers: List[GeologicalLayer]
):
    location_csv = io.StringIO()
    geology_csv = io.StringIO()

    loc_writer = csv.writer(location_csv)
    geo_writer = csv.writer(geology_csv)

    # Cabeçalhos EXATOS
    loc_writer.writerow([
        "Location ID",
        "East",
        "North",
        "Ground Level",
        "Final Depth"
    ])

    for loc in locations:
        loc_writer.writerow([
            loc.location_id,
            loc.east,
            loc.north,
            loc.ground_level,
            loc.final_depth
        ])

    geo_writer.writerow([
        "Location ID",
        "Depth Top",
        "Depth Base",
        "Geology Code",
        "Description"
    ])

    for layer in layers:
        geo_writer.writerow([
            layer.location_id,
            layer.depth_top,
            layer.depth_base,
            layer.geology_code,
            layer.description or ""
        ])

    return {
        "Location Details.csv": location_csv.getvalue(),
        "Field Geological Descriptions.csv": geology_csv.getvalue()
    }

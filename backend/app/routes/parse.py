from fastapi import APIRouter
from typing import List

from app.models.location import Location
from app.models.geology import GeologicalLayer
from app.validators.geology_validator import validate_layers

router = APIRouter(prefix="/data", tags=["Data Input"])

@router.post("/validate")
def validate_manual_data(
    locations: List[Location],
    layers: List[GeologicalLayer]
):
    errors = validate_layers(layers)

    return {
        "locations_count": len(locations),
        "layers_count": len(layers),
        "errors": errors,
        "valid": len(errors) == 0
    }

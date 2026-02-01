from pydantic import BaseModel, Field

class Location(BaseModel):
    location_id: str = Field(..., description="ID da sondagem (ex: BH-01)")
    east: float = Field(..., description="Coordenada Leste (X)")
    north: float = Field(..., description="Coordenada Norte (Y)")
    ground_level: float = Field(..., description="Cota da boca do furo")
    final_depth: float = Field(..., gt=0, description="Profundidade final do furo")

    class Config:
        schema_extra = {
            "example": {
                "location_id": "BH-01",
                "east": 543210.25,
                "north": 9571234.80,
                "ground_level": 102.50,
                "final_depth": 15.00
            }
        }

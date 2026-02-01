from pydantic import BaseModel, Field

class GeologicalLayer(BaseModel):
    location_id: str = Field(..., description="ID da sondagem")
    depth_top: float = Field(..., ge=0, description="Topo da camada")
    depth_base: float = Field(..., gt=0, description="Base da camada")
    geology_code: str = Field(..., description="Código geológico (ARG, ARE, etc)")
    description: str | None = Field(None, description="Descrição textual da camada")

    class Config:
        schema_extra = {
            "example": {
                "location_id": "BH-01",
                "depth_top": 0.00,
                "depth_base": 2.50,
                "geology_code": "ARG",
                "description": "Argila mole, cinza"
            }
        }

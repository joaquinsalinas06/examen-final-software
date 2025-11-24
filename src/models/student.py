from pydantic import BaseModel, Field
from typing import Optional


class Student(BaseModel):
    """
    Modelo que representa a un estudiante en el sistema.

    Attributes:
        codigo: Código único del estudiante (identificador)
        nombre: Nombre completo del estudiante (opcional)
    """
    codigo: str = Field(..., description="Código único del estudiante", min_length=1)
    nombre: Optional[str] = Field(None, description="Nombre completo del estudiante")

    class Config:
        json_schema_extra = {
            "example": {
                "codigo": "202012345",
                "nombre": "Juan Pérez"
            }
        }

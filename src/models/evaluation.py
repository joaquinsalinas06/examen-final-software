from pydantic import BaseModel, Field, field_validator


class Evaluation(BaseModel):
    """
    Modelo que representa una evaluación con su nota y peso.

    Attributes:
        nota: Calificación obtenida (0-20 según sistema peruano)
        peso: Porcentaje de peso sobre la nota final (0-100)
    """
    nota: float = Field(..., description="Calificación obtenida", ge=0, le=20)
    peso: float = Field(..., description="Porcentaje de peso sobre 100", gt=0, le=100)

    @field_validator('nota')
    @classmethod
    def validate_nota(cls, value: float) -> float:
        """Valida que la nota esté en el rango permitido"""
        if value < 0 or value > 20:
            raise ValueError("La nota debe estar entre 0 y 20")
        return value

    @field_validator('peso')
    @classmethod
    def validate_peso(cls, value: float) -> float:
        """Valida que el peso esté en el rango permitido"""
        if value <= 0 or value > 100:
            raise ValueError("El peso debe ser mayor a 0 y no mayor a 100")
        return value

    class Config:
        json_schema_extra = {
            "example": {
                "nota": 15.5,
                "peso": 30.0
            }
        }

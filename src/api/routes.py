from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional
from src.models.student import Student
from src.models.evaluation import Evaluation
from src.calculator.grade_calculator import GradeCalculator, GradeCalculatorException
from src.storage.json_storage import JsonStorage

router = APIRouter()
calculator = GradeCalculator()
storage = JsonStorage()


# Modelos de request/response para la API
class RegisterStudentRequest(BaseModel):
    """Request para registrar un estudiante"""
    codigo: str = Field(..., description="Código del estudiante")
    nombre: Optional[str] = Field(None, description="Nombre del estudiante")


class RegisterEvaluationsRequest(BaseModel):
    """Request para registrar evaluaciones de un estudiante"""
    codigo_estudiante: str = Field(..., description="Código del estudiante")
    evaluaciones: List[Evaluation] = Field(..., description="Lista de evaluaciones")


class CalculateGradeRequest(BaseModel):
    """Request para calcular la nota final"""
    codigo_estudiante: str = Field(..., description="Código del estudiante")
    evaluaciones: List[Evaluation] = Field(..., description="Lista de evaluaciones")
    has_minimum_attendance: bool = Field(
        ...,
        description="Indica si el estudiante cumple con la asistencia mínima"
    )
    all_years_teachers: List[bool] = Field(
        ...,
        description="Lista que indica cumplimiento del criterio por año académico"
    )


class GradeCalculationResponse(BaseModel):
    """Response del cálculo de nota final"""
    promedio_ponderado: float
    penalizacion_inasistencias: float
    puntos_extra: float
    nota_final: float
    detalle: str


@router.post(
    "/students",
    status_code=status.HTTP_201_CREATED,
    response_model=Student,
    tags=["Estudiantes"],
    summary="Registrar estudiante (RF01)"
)
async def register_student(request: RegisterStudentRequest):
    """
    Registra un nuevo estudiante en el sistema.

    Implementa RF01: Registro de estudiante.
    """
    try:
        student = Student(codigo=request.codigo, nombre=request.nombre)
        student_dict = student.model_dump()
        storage.save_student(student_dict)
        return student
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar estudiante: {str(e)}"
        )


@router.get(
    "/students/{codigo}",
    response_model=Student,
    tags=["Estudiantes"],
    summary="Obtener estudiante"
)
async def get_student(codigo: str):
    """Obtiene la información de un estudiante"""
    student_data = storage.get_student(codigo)
    if not student_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Estudiante con código {codigo} no encontrado"
        )
    return Student(**student_data)


@router.get(
    "/students",
    response_model=List[Student],
    tags=["Estudiantes"],
    summary="Listar todos los estudiantes"
)
async def list_students():
    """Obtiene la lista de todos los estudiantes registrados"""
    students_data = storage.load_students()
    return [Student(**s) for s in students_data]


@router.post(
    "/calculate-grade",
    response_model=GradeCalculationResponse,
    tags=["Cálculo de Notas"],
    summary="Calcular nota final (RF04)"
)
async def calculate_grade(request: CalculateGradeRequest):
    """
    Calcula la nota final de un estudiante.

    Implementa RF04: Cálculo de nota final considerando:
    - Promedio ponderado de evaluaciones
    - Asistencia mínima (RF02)
    - Puntos extra (RF03)
    - Detalle del cálculo (RF05)
    """
    try:
        # Verificar que el estudiante existe
        student = storage.get_student(request.codigo_estudiante)
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Estudiante {request.codigo_estudiante} no encontrado"
            )

        # Calcular nota final
        result = calculator.calculate_final_grade(
            evaluations=request.evaluaciones,
            has_minimum_attendance=request.has_minimum_attendance,
            all_years_teachers=request.all_years_teachers
        )

        # Guardar el cálculo
        calculation_record = {
            'codigo_estudiante': request.codigo_estudiante,
            'evaluaciones': [e.model_dump() for e in request.evaluaciones],
            'has_minimum_attendance': request.has_minimum_attendance,
            'all_years_teachers': request.all_years_teachers,
            **result
        }
        storage.save_calculation(request.codigo_estudiante, calculation_record)

        return GradeCalculationResponse(**result)

    except GradeCalculatorException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al calcular nota: {str(e)}"
        )


@router.get(
    "/grade-detail/{codigo}",
    tags=["Cálculo de Notas"],
    summary="Ver detalle del cálculo (RF05)"
)
async def get_grade_detail(codigo: str):
    """
    Obtiene el detalle del último cálculo de nota de un estudiante.

    Implementa RF05: Visualización del detalle del cálculo.
    """
    calculation = storage.get_latest_calculation(codigo)
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay cálculos para el estudiante {codigo}"
        )
    return calculation


@router.get(
    "/calculations/{codigo}",
    tags=["Cálculo de Notas"],
    summary="Ver historial de cálculos"
)
async def get_calculation_history(codigo: str):
    """Obtiene el historial de cálculos de un estudiante"""
    calculations = storage.load_calculations(codigo)
    if not calculations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No hay cálculos para el estudiante {codigo}"
        )
    return calculations


@router.get(
    "/attendance/{codigo}",
    tags=["Políticas"],
    summary="Consultar asistencia mínima (RF02)"
)
async def check_attendance(codigo: str, has_reached_minimum_classes: bool):
    """
    Consulta si un estudiante cumple con la asistencia mínima.

    Implementa RF02: Validación de asistencia mínima.
    """
    from src.policies.attendance_policy import AttendancePolicy

    policy = AttendancePolicy()
    cumple = policy.check_minimum_attendance(has_reached_minimum_classes)

    return {
        "codigo_estudiante": codigo,
        "has_reached_minimum_classes": has_reached_minimum_classes,
        "cumple_asistencia_minima": cumple,
        "detalle": "Cumple con asistencia mínima" if cumple else "NO cumple con asistencia mínima"
    }


@router.get(
    "/extra-points/{codigo}",
    tags=["Políticas"],
    summary="Consultar elegibilidad para puntos extra (RF03)"
)
async def check_extra_points(codigo: str, all_years_teachers: str):
    """
    Consulta si un estudiante es elegible para puntos extra.

    Implementa RF03: Validación de elegibilidad para puntos extra.

    Args:
        all_years_teachers: String separado por comas con valores true/false
                           Ejemplo: "true,true,false"
    """
    from src.policies.extra_points_policy import ExtraPointsPolicy

    # Parsear el string a lista de booleanos
    try:
        years_list = [
            val.strip().lower() == 'true'
            for val in all_years_teachers.split(',')
        ]
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato inválido para all_years_teachers. Use: 'true,false,true'"
        )

    policy = ExtraPointsPolicy()
    es_elegible = policy.check_eligibility(years_list)
    puntos = policy.calculate_extra_points(es_elegible)

    return {
        "codigo_estudiante": codigo,
        "all_years_teachers": years_list,
        "es_elegible": es_elegible,
        "puntos_extra": puntos,
        "detalle": f"Elegible para {puntos} puntos extra" if es_elegible else "No es elegible para puntos extra"
    }

"""
Tests para modelos Student y Evaluation
"""

import pytest
from pydantic import ValidationError
from src.models.student import Student
from src.models.evaluation import Evaluation


class TestStudent:
    """Tests para el modelo Student"""

    def test_create_student_with_name(self):
        """Test: Crear estudiante con código y nombre"""
        student = Student(codigo="202012345", nombre="Juan Pérez")
        assert student.codigo == "202012345"
        assert student.nombre == "Juan Pérez"

    def test_create_student_without_name(self):
        """Test: Crear estudiante sin nombre (opcional)"""
        student = Student(codigo="202012345")
        assert student.codigo == "202012345"
        assert student.nombre is None

    def test_student_codigo_required(self):
        """Test: Código es requerido"""
        with pytest.raises(ValidationError):
            Student()

    def test_student_to_dict(self):
        """Test: Convertir estudiante a diccionario"""
        student = Student(codigo="202012345", nombre="Juan Pérez")
        data = student.model_dump()
        assert data["codigo"] == "202012345"
        assert data["nombre"] == "Juan Pérez"


class TestEvaluation:
    """Tests para el modelo Evaluation"""

    def test_create_evaluation_valid(self):
        """Test: Crear evaluación válida"""
        evaluation = Evaluation(nota=15.5, peso=30.0)
        assert evaluation.nota == 15.5
        assert evaluation.peso == 30.0

    def test_evaluation_nota_min_value(self):
        """Test: Nota mínima válida (0)"""
        evaluation = Evaluation(nota=0.0, peso=50.0)
        assert evaluation.nota == 0.0

    def test_evaluation_nota_max_value(self):
        """Test: Nota máxima válida (20)"""
        evaluation = Evaluation(nota=20.0, peso=50.0)
        assert evaluation.nota == 20.0

    def test_evaluation_nota_below_min(self):
        """Test: Error si nota es menor a 0"""
        with pytest.raises(ValidationError):
            Evaluation(nota=-1.0, peso=50.0)

    def test_evaluation_nota_above_max(self):
        """Test: Error si nota es mayor a 20"""
        with pytest.raises(ValidationError):
            Evaluation(nota=21.0, peso=50.0)

    def test_evaluation_peso_min_value(self):
        """Test: Peso mínimo válido (> 0)"""
        evaluation = Evaluation(nota=15.0, peso=0.1)
        assert evaluation.peso == 0.1

    def test_evaluation_peso_max_value(self):
        """Test: Peso máximo válido (100)"""
        evaluation = Evaluation(nota=15.0, peso=100.0)
        assert evaluation.peso == 100.0

    def test_evaluation_peso_zero(self):
        """Test: Error si peso es 0"""
        with pytest.raises(ValidationError):
            Evaluation(nota=15.0, peso=0.0)

    def test_evaluation_peso_negative(self):
        """Test: Error si peso es negativo"""
        with pytest.raises(ValidationError):
            Evaluation(nota=15.0, peso=-10.0)

    def test_evaluation_peso_above_max(self):
        """Test: Error si peso es mayor a 100"""
        with pytest.raises(ValidationError):
            Evaluation(nota=15.0, peso=101.0)

    def test_evaluation_to_dict(self):
        """Test: Convertir evaluación a diccionario"""
        evaluation = Evaluation(nota=16.5, peso=40.0)
        data = evaluation.model_dump()
        assert data["nota"] == 16.5
        assert data["peso"] == 40.0

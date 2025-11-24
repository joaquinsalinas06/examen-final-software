"""
Tests para GradeCalculator (RF04)
"""

import pytest
from src.models.evaluation import Evaluation
from src.calculator.grade_calculator import GradeCalculator, GradeCalculatorException


class TestGradeCalculator:
    """Tests para el calculador de notas"""

    def setup_method(self):
        """Setup ejecutado antes de cada test"""
        self.calculator = GradeCalculator()

    def test_normal_calculation(self):
        """Test: Cálculo normal con asistencia y sin puntos extra"""
        evaluations = [
            Evaluation(nota=15.0, peso=30.0),
            Evaluation(nota=18.0, peso=40.0),
            Evaluation(nota=16.0, peso=30.0)
        ]

        result = self.calculator.calculate_final_grade(
            evaluations=evaluations,
            has_minimum_attendance=True,
            all_years_teachers=[True, False]  # No todos cumplen
        )

        # Promedio: 15*0.3 + 18*0.4 + 16*0.3 = 4.5 + 7.2 + 4.8 = 16.5
        assert result['promedio_ponderado'] == 16.5
        assert result['penalizacion_inasistencias'] == 0.0
        assert result['puntos_extra'] == 0.0
        assert result['nota_final'] == 16.5
        assert 'detalle' in result

    def test_no_minimum_attendance(self):
        """Test: Sin asistencia mínima, nota final es 0"""
        evaluations = [
            Evaluation(nota=18.0, peso=50.0),
            Evaluation(nota=19.0, peso=50.0)
        ]

        result = self.calculator.calculate_final_grade(
            evaluations=evaluations,
            has_minimum_attendance=False,  # No cumple asistencia
            all_years_teachers=[True, True]
        )

        # Promedio: 18*0.5 + 19*0.5 = 18.5
        # Pero nota final es 0 por no cumplir asistencia
        assert result['promedio_ponderado'] == 18.5
        assert result['penalizacion_inasistencias'] == 18.5  # Pierde todo
        assert result['puntos_extra'] == 0.0
        assert result['nota_final'] == 0.0

    def test_with_extra_points(self):
        """Test: Con puntos extra (cumple criterio en todos los años)"""
        evaluations = [
            Evaluation(nota=16.0, peso=100.0)
        ]

        result = self.calculator.calculate_final_grade(
            evaluations=evaluations,
            has_minimum_attendance=True,
            all_years_teachers=[True, True, True]  # Todos cumplen -> puntos extra
        )

        # Promedio: 16.0
        # Puntos extra: 2.0
        # Nota final: 16.0 + 2.0 = 18.0
        assert result['promedio_ponderado'] == 16.0
        assert result['puntos_extra'] == 2.0
        assert result['nota_final'] == 18.0

    def test_without_extra_points(self):
        """Test: Sin puntos extra (no cumple en todos los años)"""
        evaluations = [
            Evaluation(nota=17.0, peso=100.0)
        ]

        result = self.calculator.calculate_final_grade(
            evaluations=evaluations,
            has_minimum_attendance=True,
            all_years_teachers=[True, False, True]  # No todos -> sin puntos extra
        )

        assert result['promedio_ponderado'] == 17.0
        assert result['puntos_extra'] == 0.0
        assert result['nota_final'] == 17.0

    def test_deterministic(self):
        """Test: Mismo input produce mismo output (RNF03)"""
        evaluations = [
            Evaluation(nota=14.5, peso=25.0),
            Evaluation(nota=16.8, peso=35.0),
            Evaluation(nota=15.2, peso=40.0)
        ]

        # Ejecutar el cálculo 3 veces con los mismos parámetros
        result1 = self.calculator.calculate_final_grade(
            evaluations=evaluations,
            has_minimum_attendance=True,
            all_years_teachers=[True, True]
        )

        result2 = self.calculator.calculate_final_grade(
            evaluations=evaluations,
            has_minimum_attendance=True,
            all_years_teachers=[True, True]
        )

        result3 = self.calculator.calculate_final_grade(
            evaluations=evaluations,
            has_minimum_attendance=True,
            all_years_teachers=[True, True]
        )

        # Los tres resultados deben ser idénticos
        assert result1['nota_final'] == result2['nota_final'] == result3['nota_final']
        assert result1['promedio_ponderado'] == result2['promedio_ponderado']
        assert result1['puntos_extra'] == result2['puntos_extra']

    def test_max_evaluations_limit(self):
        """Test: Límite de 10 evaluaciones (RNF01)"""
        # Crear 11 evaluaciones (excede el límite)
        evaluations = [
            Evaluation(nota=15.0, peso=9.09) for _ in range(11)
        ]

        with pytest.raises(GradeCalculatorException) as exc_info:
            self.calculator.calculate_final_grade(
                evaluations=evaluations,
                has_minimum_attendance=True,
                all_years_teachers=[True]
            )

        assert "máximo de evaluaciones es 10" in str(exc_info.value)

    def test_exactly_10_evaluations(self):
        """Test: Permite exactamente 10 evaluaciones"""
        evaluations = [
            Evaluation(nota=15.0, peso=10.0) for _ in range(10)
        ]

        result = self.calculator.calculate_final_grade(
            evaluations=evaluations,
            has_minimum_attendance=True,
            all_years_teachers=[False]
        )

        assert result['promedio_ponderado'] == 15.0
        assert result['nota_final'] == 15.0

    def test_empty_evaluations(self):
        """Test: Error con lista vacía de evaluaciones"""
        with pytest.raises(GradeCalculatorException) as exc_info:
            self.calculator.calculate_final_grade(
                evaluations=[],
                has_minimum_attendance=True,
                all_years_teachers=[True]
            )

        assert "al menos una evaluación" in str(exc_info.value)

    def test_invalid_weights_sum(self):
        """Test: Error cuando pesos no suman 100%"""
        evaluations = [
            Evaluation(nota=15.0, peso=30.0),
            Evaluation(nota=18.0, peso=30.0)  # Total: 60% != 100%
        ]

        with pytest.raises(GradeCalculatorException) as exc_info:
            self.calculator.calculate_final_grade(
                evaluations=evaluations,
                has_minimum_attendance=True,
                all_years_teachers=[True]
            )

        assert "suma de los pesos debe ser 100%" in str(exc_info.value)

    def test_nota_final_max_20(self):
        """Test: Nota final no puede exceder 20 (incluso con puntos extra)"""
        evaluations = [
            Evaluation(nota=19.0, peso=100.0)
        ]

        result = self.calculator.calculate_final_grade(
            evaluations=evaluations,
            has_minimum_attendance=True,
            all_years_teachers=[True, True]  # Puntos extra
        )

        # 19 + 2 = 21, pero se limita a 20
        assert result['nota_final'] == 20.0

    def test_weighted_average_calculation(self):
        """Test: Verifica cálculo correcto del promedio ponderado"""
        evaluations = [
            Evaluation(nota=10.0, peso=20.0),
            Evaluation(nota=15.0, peso=30.0),
            Evaluation(nota=20.0, peso=50.0)
        ]

        result = self.calculator.calculate_final_grade(
            evaluations=evaluations,
            has_minimum_attendance=True,
            all_years_teachers=[False]
        )

        # Promedio: 10*0.2 + 15*0.3 + 20*0.5 = 2 + 4.5 + 10 = 16.5
        assert result['promedio_ponderado'] == 16.5

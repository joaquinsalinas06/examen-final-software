from typing import List, Dict
from src.models.evaluation import Evaluation
from src.policies.attendance_policy import AttendancePolicy
from src.policies.extra_points_policy import ExtraPointsPolicy


class GradeCalculatorException(Exception):
    """Excepción personalizada para errores en el cálculo de notas"""
    pass


class GradeCalculator:
    """
    Calculadora central para el cálculo de notas finales.

    Implementa los requisitos funcionales RF01-RF05 y no funcionales RNF01-RNF04.
    Garantiza determinismo: mismos inputs siempre producen mismo output.

    Attributes:
        attendance_policy: Política de asistencia mínima
        extra_points_policy: Política de puntos extra
        max_evaluations: Número máximo de evaluaciones permitidas (RNF01)
    """

    MAX_EVALUATIONS = 10  # RNF01

    def __init__(self):
        """Inicializa el calculador con las políticas necesarias"""
        self.attendance_policy = AttendancePolicy()
        self.extra_points_policy = ExtraPointsPolicy()

    def calculate_final_grade(
        self,
        evaluations: List[Evaluation],
        has_minimum_attendance: bool,
        all_years_teachers: List[bool]
    ) -> Dict:
        """
        Calcula la nota final de un estudiante (RF04).

        Proceso determinista (RNF03):
        1. Validar número de evaluaciones (RNF01)
        2. Calcular promedio ponderado
        3. Aplicar política de asistencia (RF02)
        4. Aplicar política de puntos extra (RF03)
        5. Calcular nota final

        Args:
            evaluations: Lista de evaluaciones con nota y peso
            has_minimum_attendance: Indica si cumple asistencia mínima
            all_years_teachers: Lista de booleanos para política de puntos extra

        Returns:
            Dict con:
                - promedio_ponderado: float
                - penalizacion_inasistencias: float
                - puntos_extra: float
                - nota_final: float
                - detalle: str (RF05)

        Raises:
            GradeCalculatorException: Si hay errores de validación
        """
        # 1. Validar número de evaluaciones (RNF01)
        self._validate_evaluations(evaluations)

        # 2. Calcular promedio ponderado
        promedio_ponderado = self._calculate_weighted_average(evaluations)

        # 3. Aplicar política de asistencia (RF02)
        cumple_asistencia = self.attendance_policy.check_minimum_attendance(
            has_minimum_attendance
        )

        # Si no cumple asistencia mínima, nota final es 0
        if not cumple_asistencia:
            return {
                'promedio_ponderado': promedio_ponderado,
                'penalizacion_inasistencias': promedio_ponderado,  # Pierde todo
                'puntos_extra': 0.0,
                'nota_final': 0.0,
                'detalle': self._generate_detail(
                    promedio_ponderado,
                    promedio_ponderado,
                    0.0,
                    0.0,
                    cumple_asistencia,
                    False
                )
            }

        # 4. Aplicar política de puntos extra (RF03)
        es_elegible_extra = self.extra_points_policy.check_eligibility(
            all_years_teachers
        )
        puntos_extra = self.extra_points_policy.calculate_extra_points(
            es_elegible_extra
        )

        # 5. Calcular nota final
        nota_final = min(promedio_ponderado + puntos_extra, 20.0)  # Max 20

        # 6. Generar detalle (RF05)
        detalle = self._generate_detail(
            promedio_ponderado,
            0.0,
            puntos_extra,
            nota_final,
            cumple_asistencia,
            es_elegible_extra
        )

        return {
            'promedio_ponderado': round(promedio_ponderado, 2),
            'penalizacion_inasistencias': 0.0,
            'puntos_extra': round(puntos_extra, 2),
            'nota_final': round(nota_final, 2),
            'detalle': detalle
        }

    def _validate_evaluations(self, evaluations: List[Evaluation]) -> None:
        """
        Valida que las evaluaciones cumplan con los requisitos.

        Args:
            evaluations: Lista de evaluaciones a validar

        Raises:
            GradeCalculatorException: Si hay errores de validación
        """
        if not evaluations:
            raise GradeCalculatorException(
                "Debe haber al menos una evaluación"
            )

        if len(evaluations) > self.MAX_EVALUATIONS:
            raise GradeCalculatorException(
                f"El número máximo de evaluaciones es {self.MAX_EVALUATIONS} (RNF01)"
            )

        # Validar que los pesos sumen 100%
        total_peso = sum(eval.peso for eval in evaluations)
        if abs(total_peso - 100.0) > 0.01:  # Tolerancia para errores de punto flotante
            raise GradeCalculatorException(
                f"La suma de los pesos debe ser 100%, actual: {total_peso}%"
            )

    def _calculate_weighted_average(self, evaluations: List[Evaluation]) -> float:
        """
        Calcula el promedio ponderado de las evaluaciones.

        Método determinista: mismo orden de operaciones siempre.

        Args:
            evaluations: Lista de evaluaciones

        Returns:
            float: Promedio ponderado calculado
        """
        promedio = sum(
            eval.nota * (eval.peso / 100.0)
            for eval in evaluations
        )
        return promedio

    def _generate_detail(
        self,
        promedio: float,
        penalizacion: float,
        puntos_extra: float,
        nota_final: float,
        cumple_asistencia: bool,
        es_elegible_extra: bool
    ) -> str:
        """
        Genera el detalle del cálculo (RF05).

        Args:
            promedio: Promedio ponderado
            penalizacion: Penalización por inasistencias
            puntos_extra: Puntos extra otorgados
            nota_final: Nota final calculada
            cumple_asistencia: Si cumple con asistencia mínima
            es_elegible_extra: Si es elegible para puntos extra

        Returns:
            str: Detalle del cálculo en formato legible
        """
        detalle_parts = [
            f"Promedio ponderado: {promedio:.2f}",
        ]

        if not cumple_asistencia:
            detalle_parts.append(
                f"Asistencia mínima: NO CUMPLE - Penalización: {penalizacion:.2f}"
            )
            detalle_parts.append(f"Nota final: {nota_final:.2f}")
        else:
            detalle_parts.append("Asistencia mínima: CUMPLE")

            if es_elegible_extra and puntos_extra > 0:
                detalle_parts.append(
                    f"Puntos extra: +{puntos_extra:.2f} (Cumple criterio en todos los años)"
                )
            else:
                detalle_parts.append("Puntos extra: 0.00 (No cumple criterio)")

            detalle_parts.append(f"Nota final: {nota_final:.2f}")

        return " | ".join(detalle_parts)

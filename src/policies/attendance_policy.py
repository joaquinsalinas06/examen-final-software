from typing import List


class AttendancePolicy:
    """
    Política de asistencia mínima requerida según el reglamento académico de UTEC.

    Implementa RF02: Verificación de asistencia mínima requerida.
    """

    def check_minimum_attendance(
        self,
        has_reached_minimum_classes: bool
    ) -> bool:
        """
        Verifica si el estudiante cumple con la asistencia mínima requerida.

        Args:
            has_reached_minimum_classes: Indica si el estudiante alcanzó
                                         la asistencia mínima según el reglamento

        Returns:
            bool: True si cumple con la asistencia mínima, False en caso contrario
        """
        return has_reached_minimum_classes

    def calculate_penalty(self, has_minimum_attendance: bool) -> float:
        """
        Calcula la penalización por no cumplir con la asistencia mínima.

        Args:
            has_minimum_attendance: Indica si cumple con asistencia mínima

        Returns:
            float: 0 si cumple con asistencia, penalización si no cumple
        """
        if not has_minimum_attendance:
            # Si no cumple con asistencia mínima, la nota final es 0
            # La penalización será aplicada en el calculador
            return 0.0
        return 0.0

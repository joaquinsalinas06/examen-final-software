from typing import List


class ExtraPointsPolicy:
    """
    Política de puntos extra según criterios académicos.

    Implementa RF03: Determina si el estudiante califica para puntos extra
    según la política de allYearsTeachers.
    """

    def check_eligibility(
        self,
        all_years_teachers: List[bool]
    ) -> bool:
        """
        Verifica si el estudiante es elegible para recibir puntos extra.

        Según RF03, el estudiante debe cumplir el criterio en TODOS los años.

        Args:
            all_years_teachers: Lista de booleanos que indica si cumplió
                               el criterio en cada año académico

        Returns:
            bool: True si cumple en TODOS los años (elegible para puntos extra),
                  False en caso contrario
        """
        if not all_years_teachers:
            return False

        return all(all_years_teachers)

    def calculate_extra_points(
        self,
        is_eligible: bool,
        extra_points_amount: float = 2.0
    ) -> float:
        """
        Calcula los puntos extra a otorgar.

        Args:
            is_eligible: Indica si el estudiante es elegible para puntos extra
            extra_points_amount: Cantidad de puntos extra a otorgar (default: 2.0)

        Returns:
            float: Puntos extra otorgados (0 si no es elegible)
        """
        if is_eligible:
            return extra_points_amount
        return 0.0

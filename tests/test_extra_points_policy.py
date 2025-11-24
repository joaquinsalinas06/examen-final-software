"""
Tests para ExtraPointsPolicy (RF03)
"""

import pytest
from src.policies.extra_points_policy import ExtraPointsPolicy


class TestExtraPointsPolicy:
    """Tests para la política de puntos extra"""

    def setup_method(self):
        """Setup ejecutado antes de cada test"""
        self.policy = ExtraPointsPolicy()

    def test_check_eligibility_all_true(self):
        """Test: Elegible cuando cumple criterio en TODOS los años"""
        all_years = [True, True, True]
        result = self.policy.check_eligibility(all_years)
        assert result is True

    def test_check_eligibility_some_false(self):
        """Test: NO elegible cuando no cumple en algún año"""
        all_years = [True, False, True]
        result = self.policy.check_eligibility(all_years)
        assert result is False

    def test_check_eligibility_all_false(self):
        """Test: NO elegible cuando no cumple en ningún año"""
        all_years = [False, False, False]
        result = self.policy.check_eligibility(all_years)
        assert result is False

    def test_check_eligibility_empty_list(self):
        """Test: NO elegible con lista vacía"""
        result = self.policy.check_eligibility([])
        assert result is False

    def test_calculate_extra_points_eligible(self):
        """Test: Calcula puntos extra si es elegible"""
        points = self.policy.calculate_extra_points(is_eligible=True)
        assert points == 2.0

    def test_calculate_extra_points_not_eligible(self):
        """Test: No otorga puntos si no es elegible"""
        points = self.policy.calculate_extra_points(is_eligible=False)
        assert points == 0.0

    def test_calculate_extra_points_custom_amount(self):
        """Test: Permite personalizar cantidad de puntos extra"""
        points = self.policy.calculate_extra_points(is_eligible=True, extra_points_amount=3.0)
        assert points == 3.0

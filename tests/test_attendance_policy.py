"""
Tests para AttendancePolicy (RF02)
"""

import pytest
from src.policies.attendance_policy import AttendancePolicy


class TestAttendancePolicy:
    """Tests para la política de asistencia mínima"""

    def setup_method(self):
        """Setup ejecutado antes de cada test"""
        self.policy = AttendancePolicy()

    def test_check_minimum_attendance_cumple(self):
        """Test: Estudiante cumple con asistencia mínima"""
        result = self.policy.check_minimum_attendance(has_reached_minimum_classes=True)
        assert result is True

    def test_check_minimum_attendance_no_cumple(self):
        """Test: Estudiante NO cumple con asistencia mínima"""
        result = self.policy.check_minimum_attendance(has_reached_minimum_classes=False)
        assert result is False

    def test_calculate_penalty_with_attendance(self):
        """Test: No hay penalización si cumple asistencia"""
        penalty = self.policy.calculate_penalty(has_minimum_attendance=True)
        assert penalty == 0.0

    def test_calculate_penalty_without_attendance(self):
        """Test: Penalización si no cumple asistencia"""
        penalty = self.policy.calculate_penalty(has_minimum_attendance=False)
        assert penalty == 0.0  # La penalización se aplica en el calculador

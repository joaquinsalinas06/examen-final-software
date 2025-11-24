"""
Tests para JsonStorage
"""

import pytest
import os
import json
from pathlib import Path
from src.storage.json_storage import JsonStorage


class TestJsonStorage:
    """Tests para el sistema de almacenamiento JSON"""

    def setup_method(self):
        """Setup: Crear storage con directorio temporal"""
        self.test_data_dir = "test_data"
        self.storage = JsonStorage(data_dir=self.test_data_dir)
        self.storage.clear_all_data()

    def teardown_method(self):
        """Cleanup: Limpiar archivos de prueba"""
        self.storage.clear_all_data()
        import shutil
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)

    def test_initialize_creates_directory(self):
        """Test: Inicialización crea directorio de datos"""
        storage = JsonStorage(data_dir="test_init")
        assert os.path.exists("test_init")
        # Cleanup
        import shutil
        shutil.rmtree("test_init")

    def test_save_student(self):
        """Test: Guardar un estudiante"""
        student_data = {"codigo": "202012345", "nombre": "Juan Pérez"}
        result = self.storage.save_student(student_data)
        assert result is True

    def test_load_students(self):
        """Test: Cargar estudiantes guardados"""
        student1 = {"codigo": "202012345", "nombre": "Juan Pérez"}
        student2 = {"codigo": "202012346", "nombre": "María García"}

        self.storage.save_student(student1)
        self.storage.save_student(student2)

        students = self.storage.load_students()
        assert len(students) == 2
        assert students[0]["codigo"] == "202012345"
        assert students[1]["codigo"] == "202012346"

    def test_get_student_exists(self):
        """Test: Obtener estudiante existente"""
        student_data = {"codigo": "202012345", "nombre": "Juan Pérez"}
        self.storage.save_student(student_data)

        student = self.storage.get_student("202012345")
        assert student is not None
        assert student["codigo"] == "202012345"
        assert student["nombre"] == "Juan Pérez"

    def test_get_student_not_exists(self):
        """Test: Obtener estudiante que no existe"""
        student = self.storage.get_student("999999999")
        assert student is None

    def test_update_existing_student(self):
        """Test: Actualizar estudiante existente"""
        student1 = {"codigo": "202012345", "nombre": "Juan Pérez"}
        self.storage.save_student(student1)

        student2 = {"codigo": "202012345", "nombre": "Juan Pérez Updated"}
        self.storage.save_student(student2)

        students = self.storage.load_students()
        assert len(students) == 1  # Solo debe haber 1, no 2
        assert students[0]["nombre"] == "Juan Pérez Updated"

    def test_save_calculation(self):
        """Test: Guardar cálculo de nota"""
        calculation = {
            "promedio_ponderado": 16.5,
            "puntos_extra": 2.0,
            "nota_final": 18.5,
            "detalle": "Test calculation"
        }

        result = self.storage.save_calculation("202012345", calculation)
        assert result is True

    def test_load_calculations(self):
        """Test: Cargar cálculos de un estudiante"""
        calc1 = {"nota_final": 15.0}
        calc2 = {"nota_final": 16.0}

        self.storage.save_calculation("202012345", calc1)
        self.storage.save_calculation("202012345", calc2)

        calculations = self.storage.load_calculations("202012345")
        assert len(calculations) == 2
        assert "timestamp" in calculations[0]  # Debe agregar timestamp
        assert "timestamp" in calculations[1]

    def test_load_calculations_empty(self):
        """Test: Cargar cálculos de estudiante sin cálculos"""
        calculations = self.storage.load_calculations("999999999")
        assert calculations == []

    def test_get_latest_calculation(self):
        """Test: Obtener último cálculo"""
        calc1 = {"nota_final": 15.0}
        calc2 = {"nota_final": 16.0}
        calc3 = {"nota_final": 17.0}

        self.storage.save_calculation("202012345", calc1)
        self.storage.save_calculation("202012345", calc2)
        self.storage.save_calculation("202012345", calc3)

        latest = self.storage.get_latest_calculation("202012345")
        assert latest is not None
        assert latest["nota_final"] == 17.0  # El último guardado

    def test_get_latest_calculation_none(self):
        """Test: Obtener último cálculo cuando no hay ninguno"""
        latest = self.storage.get_latest_calculation("999999999")
        assert latest is None

    def test_clear_all_data(self):
        """Test: Limpiar todos los datos"""
        student = {"codigo": "202012345", "nombre": "Juan Pérez"}
        calculation = {"nota_final": 16.0}

        self.storage.save_student(student)
        self.storage.save_calculation("202012345", calculation)

        self.storage.clear_all_data()

        students = self.storage.load_students()
        calculations = self.storage.load_calculations("202012345")

        assert students == []
        assert calculations == []

    def test_calculations_different_students(self):
        """Test: Cálculos separados por estudiante"""
        calc1 = {"nota_final": 15.0}
        calc2 = {"nota_final": 18.0}

        self.storage.save_calculation("202012345", calc1)
        self.storage.save_calculation("202012346", calc2)

        calcs_student1 = self.storage.load_calculations("202012345")
        calcs_student2 = self.storage.load_calculations("202012346")

        assert len(calcs_student1) == 1
        assert len(calcs_student2) == 1
        assert calcs_student1[0]["nota_final"] == 15.0
        assert calcs_student2[0]["nota_final"] == 18.0

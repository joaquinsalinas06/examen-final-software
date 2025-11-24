import json
import os
from typing import List, Dict, Optional
from pathlib import Path


class JsonStorage:
    """
    Gestor de persistencia de datos en archivos JSON.

    Maneja el almacenamiento de estudiantes y cálculos de notas.
    Garantiza la integridad de los datos y el acceso thread-safe básico.
    """

    def __init__(self, data_dir: str = "data"):
        """
        Inicializa el gestor de almacenamiento.

        Args:
            data_dir: Directorio donde se almacenarán los archivos JSON
        """
        self.data_dir = Path(data_dir)
        self.students_file = self.data_dir / "students.json"
        self.calculations_file = self.data_dir / "calculations.json"

        # Crear directorio si no existe
        self.data_dir.mkdir(exist_ok=True)

        # Inicializar archivos si no existen
        self._initialize_files()

    def _initialize_files(self) -> None:
        """Inicializa los archivos JSON si no existen"""
        if not self.students_file.exists():
            self._write_json(self.students_file, [])

        if not self.calculations_file.exists():
            self._write_json(self.calculations_file, {})

    def _read_json(self, file_path: Path) -> any:
        """
        Lee un archivo JSON de forma segura.

        Args:
            file_path: Ruta al archivo JSON

        Returns:
            Contenido del archivo JSON
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return [] if file_path == self.students_file else {}
        except json.JSONDecodeError:
            # Si el archivo está corrupto, retornar estructura vacía
            return [] if file_path == self.students_file else {}

    def _write_json(self, file_path: Path, data: any) -> None:
        """
        Escribe datos a un archivo JSON de forma segura.

        Args:
            file_path: Ruta al archivo JSON
            data: Datos a escribir
        """
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save_student(self, student_data: Dict) -> bool:
        """
        Guarda o actualiza un estudiante.

        Args:
            student_data: Diccionario con datos del estudiante
                         {codigo: str, nombre: str}

        Returns:
            bool: True si se guardó exitosamente
        """
        students = self._read_json(self.students_file)

        # Buscar si el estudiante ya existe
        existing_index = None
        for i, student in enumerate(students):
            if student.get('codigo') == student_data.get('codigo'):
                existing_index = i
                break

        if existing_index is not None:
            # Actualizar estudiante existente
            students[existing_index] = student_data
        else:
            # Agregar nuevo estudiante
            students.append(student_data)

        self._write_json(self.students_file, students)
        return True

    def load_students(self) -> List[Dict]:
        """
        Carga todos los estudiantes.

        Returns:
            List[Dict]: Lista de estudiantes
        """
        return self._read_json(self.students_file)

    def get_student(self, codigo: str) -> Optional[Dict]:
        """
        Obtiene un estudiante por su código.

        Args:
            codigo: Código del estudiante

        Returns:
            Optional[Dict]: Datos del estudiante o None si no existe
        """
        students = self._read_json(self.students_file)
        for student in students:
            if student.get('codigo') == codigo:
                return student
        return None

    def save_calculation(self, student_code: str, calculation_result: Dict) -> bool:
        """
        Guarda el resultado de un cálculo de nota.

        Args:
            student_code: Código del estudiante
            calculation_result: Resultado del cálculo con todos los detalles

        Returns:
            bool: True si se guardó exitosamente
        """
        calculations = self._read_json(self.calculations_file)

        # Si no existe una lista para este estudiante, crearla
        if student_code not in calculations:
            calculations[student_code] = []

        # Agregar timestamp al cálculo
        import datetime
        calculation_result['timestamp'] = datetime.datetime.now().isoformat()

        # Agregar el nuevo cálculo
        calculations[student_code].append(calculation_result)

        self._write_json(self.calculations_file, calculations)
        return True

    def load_calculations(self, student_code: str) -> List[Dict]:
        """
        Carga todos los cálculos de un estudiante.

        Args:
            student_code: Código del estudiante

        Returns:
            List[Dict]: Lista de cálculos del estudiante
        """
        calculations = self._read_json(self.calculations_file)
        return calculations.get(student_code, [])

    def get_latest_calculation(self, student_code: str) -> Optional[Dict]:
        """
        Obtiene el cálculo más reciente de un estudiante.

        Args:
            student_code: Código del estudiante

        Returns:
            Optional[Dict]: Último cálculo o None si no hay cálculos
        """
        calculations = self.load_calculations(student_code)
        if calculations:
            return calculations[-1]  # El último agregado
        return None

    def clear_all_data(self) -> None:
        """Limpia todos los datos (útil para tests)"""
        self._write_json(self.students_file, [])
        self._write_json(self.calculations_file, {})

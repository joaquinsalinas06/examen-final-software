#!/usr/bin/env python
"""
CLI simple para demostración del CS Grade Calculator.

Permite probar las funcionalidades principales desde la terminal.
"""

import sys
import os
from pathlib import Path
from typing import List

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.models.student import Student
from src.models.evaluation import Evaluation
from src.calculator.grade_calculator import GradeCalculator, GradeCalculatorException
from src.storage.json_storage import JsonStorage


def print_header(text: str):
    """Imprime un encabezado formateado"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_section(text: str):
    """Imprime una sección formateada"""
    print(f"\n--- {text} ---")


def get_boolean_input(prompt: str) -> bool:
    """Obtiene un input booleano del usuario"""
    while True:
        response = input(f"{prompt} (s/n): ").strip().lower()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Por favor ingrese 's' para sí o 'n' para no")


def register_student_cli(storage: JsonStorage):
    """Registra un estudiante desde la CLI"""
    print_section("Registrar Estudiante")

    codigo = input("Código del estudiante: ").strip()
    if not codigo:
        print("Error: El código no puede estar vacío")
        return

    nombre = input("Nombre del estudiante (opcional): ").strip()

    student = Student(codigo=codigo, nombre=nombre if nombre else None)
    storage.save_student(student.model_dump())

    print(f"\n✓ Estudiante {codigo} registrado exitosamente")


def calculate_grade_cli(storage: JsonStorage, calculator: GradeCalculator):
    """Calcula la nota final desde la CLI"""
    print_section("Calcular Nota Final")

    codigo = input("Código del estudiante: ").strip()
    if not codigo:
        print("Error: El código no puede estar vacío")
        return

    # Verificar si el estudiante existe
    student = storage.get_student(codigo)
    if not student:
        print(f"Advertencia: Estudiante {codigo} no está registrado")
        if not get_boolean_input("¿Desea continuar de todos modos?"):
            return

    # Ingresar evaluaciones
    print("\nIngrese las evaluaciones (nota y peso)")
    print("Recuerde que los pesos deben sumar 100%")

    evaluations: List[Evaluation] = []
    total_peso = 0.0

    while True:
        try:
            print(f"\nEvaluación #{len(evaluations) + 1}")

            nota_input = input("  Nota (0-20, o 'fin' para terminar): ").strip()
            if nota_input.lower() in ['fin', 'terminar', 'exit']:
                break

            nota = float(nota_input)
            peso = float(input(f"  Peso (restante: {100 - total_peso:.2f}%): ").strip())

            evaluation = Evaluation(nota=nota, peso=peso)
            evaluations.append(evaluation)
            total_peso += peso

            print(f"  ✓ Evaluación agregada (Total peso: {total_peso:.2f}%)")

            if abs(total_peso - 100.0) < 0.01:
                print("\n✓ Peso total alcanzado (100%)")
                break

            if total_peso > 100:
                print("Error: El peso total excede 100%")
                evaluations.pop()
                total_peso -= peso

        except ValueError as e:
            print(f"Error: Entrada inválida - {e}")
            continue

    if not evaluations:
        print("Error: Debe ingresar al menos una evaluación")
        return

    # Asistencia mínima
    print_section("Asistencia")
    has_minimum_attendance = get_boolean_input(
        "¿El estudiante cumple con la asistencia mínima?"
    )

    # Puntos extra
    print_section("Puntos Extra")
    print("Ingrese si cumplió el criterio en cada año académico")

    all_years_teachers: List[bool] = []
    num_years = int(input("¿Cuántos años académicos? "))

    for i in range(num_years):
        cumple = get_boolean_input(f"  Año {i + 1} - ¿Cumple criterio?")
        all_years_teachers.append(cumple)

    # Calcular nota final
    print_section("Calculando...")

    try:
        result = calculator.calculate_final_grade(
            evaluations=evaluations,
            has_minimum_attendance=has_minimum_attendance,
            all_years_teachers=all_years_teachers
        )

        # Guardar el cálculo
        calculation_record = {
            'codigo_estudiante': codigo,
            'evaluaciones': [e.model_dump() for e in evaluations],
            'has_minimum_attendance': has_minimum_attendance,
            'all_years_teachers': all_years_teachers,
            **result
        }
        storage.save_calculation(codigo, calculation_record)

        # Mostrar resultado
        print_header("RESULTADO DEL CÁLCULO")
        print(f"Promedio ponderado:           {result['promedio_ponderado']:.2f}")
        print(f"Penalización (inasistencias): {result['penalizacion_inasistencias']:.2f}")
        print(f"Puntos extra:                 {result['puntos_extra']:.2f}")
        print(f"\nNOTA FINAL:                   {result['nota_final']:.2f}")
        print(f"\nDetalle: {result['detalle']}")

    except GradeCalculatorException as e:
        print(f"\nError en el cálculo: {e}")


def view_grade_detail_cli(storage: JsonStorage):
    """Visualiza el detalle del cálculo de un estudiante"""
    print_section("Ver Detalle de Cálculo")

    codigo = input("Código del estudiante: ").strip()
    if not codigo:
        print("Error: El código no puede estar vacío")
        return

    calculation = storage.get_latest_calculation(codigo)
    if not calculation:
        print(f"No hay cálculos registrados para el estudiante {codigo}")
        return

    print_header(f"DETALLE DE CÁLCULO - {codigo}")
    print(f"Timestamp: {calculation.get('timestamp', 'N/A')}")
    print(f"\nPromedio ponderado:           {calculation['promedio_ponderado']:.2f}")
    print(f"Penalización (inasistencias): {calculation['penalizacion_inasistencias']:.2f}")
    print(f"Puntos extra:                 {calculation['puntos_extra']:.2f}")
    print(f"\nNOTA FINAL:                   {calculation['nota_final']:.2f}")
    print(f"\nDetalle: {calculation['detalle']}")


def main():
    """Función principal del CLI"""
    storage = JsonStorage()
    calculator = GradeCalculator()

    print_header("CS GRADE CALCULATOR - CLI")
    print("Sistema de Cálculo de Notas Finales UTEC")

    while True:
        print_section("MENÚ PRINCIPAL")
        print("1. Registrar estudiante")
        print("2. Calcular nota final")
        print("3. Ver detalle de cálculo")
        print("4. Listar estudiantes")
        print("5. Salir")

        choice = input("\nSeleccione una opción: ").strip()

        if choice == '1':
            register_student_cli(storage)
        elif choice == '2':
            calculate_grade_cli(storage, calculator)
        elif choice == '3':
            view_grade_detail_cli(storage)
        elif choice == '4':
            students = storage.load_students()
            print_section("ESTUDIANTES REGISTRADOS")
            if students:
                for student in students:
                    print(f"  - {student['codigo']}: {student.get('nombre', 'Sin nombre')}")
            else:
                print("  No hay estudiantes registrados")
        elif choice == '5':
            print("\n¡Hasta luego!")
            sys.exit(0)
        else:
            print("Opción inválida. Por favor seleccione 1-5")


if __name__ == "__main__":
    main()

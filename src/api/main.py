from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router

app = FastAPI(
    title="CS Grade Calculator API",
    description="""
    Sistema de cálculo de notas finales para UTEC.

    ## Características

    * **Registro de estudiantes** (RF01)
    * **Validación de asistencia mínima** (RF02)
    * **Política de puntos extra** (RF03)
    * **Cálculo de nota final** (RF04)
    * **Visualización de detalle** (RF05)

    ## Requisitos No Funcionales

    * Máximo 10 evaluaciones por estudiante (RNF01)
    * Soporte para 50 usuarios concurrentes (RNF02)
    * Cálculo determinista (RNF03)
    * Tiempo de cálculo < 300ms (RNF04)
    """,
    version="1.0.0",
    contact={
        "name": "UTEC",
        "email": "info@utec.edu.pe"
    }
)

# Configurar CORS para permitir acceso desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir rutas con prefijo
app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """Endpoint raíz para verificar que la API está funcionando"""
    return {
        "message": "CS Grade Calculator API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

from pydantic import BaseModel, Field
from enum import Enum

from google.adk.agents.llm_agent import LlmAgent


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IssueType(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    DOCUMENTATION = "documentation"


class IssueAnalysis(BaseModel):
    priority: Priority = Field(description="Priority level based on impact and urgency")
    issue_type: IssueType = Field(
        description="Type of issue: bug, feature, improvement, or documentation"
    )
    affected_areas: list[str] = Field(
        description="List of affected system areas (e.g., ['auth', 'database', 'ui'])"
    )
    estimated_complexity: int = Field(
        ge=1,
        le=5,
        description="Estimated complexity on 1-5 scale, where 1=very simple and 5=very complex",
    )
    reasoning: str = Field(
        description="Brief explanation (2-3 sentences) of why this priority and complexity was assigned"
    )


root_agent = LlmAgent(
    name="issue_analyzer",
    model="gemini-2.5-flash",
    instruction="""
        Eres un Asistente de Análisis de Issues para equipos de desarrollo de software.
        Tu tarea es analizar issues/tickets y extraer información estructurada.

        GUÍAS:
        - Determina la PRIORIDAD basándote en:
            * Impacto en usuarios (crítico si afecta funcionalidad principal)
            * Urgencia (alta si bloquea trabajo o afecta producción)
            * Alcance (crítico si afecta a muchos usuarios)
        
        - Identifica el TIPO DE ISSUE:
            * bug: algo que no funciona como se espera
            * feature: nueva funcionalidad solicitada
            * improvement: optimización de funcionalidad existente
            * documentation: actualización de documentación
        
        - Lista las ÁREAS AFECTADAS del sistema:
            * Usa nombres técnicos: 'auth', 'api', 'database', 'ui', 'backend', etc.
            * Pueden ser múltiples áreas
        
        - Estima la COMPLEJIDAD (1-5):
            * 1: Cambio trivial (error tipográfico, configuración simple)
            * 2: Cambio simple (una función, un endpoint)
            * 3: Cambio moderado (múltiples archivos, lógica mediana)
            * 4: Cambio complejo (refactorización, múltiples componentes)
            * 5: Cambio muy complejo (arquitectura, migraciones, múltiples sistemas)
        
        - Proporciona un RAZONAMIENTO claro y conciso
    """,
    description="Analyzes technical issues and extracts structured information for prioritization",
    output_schema=IssueAnalysis,
    output_key="issue_analysis",
)

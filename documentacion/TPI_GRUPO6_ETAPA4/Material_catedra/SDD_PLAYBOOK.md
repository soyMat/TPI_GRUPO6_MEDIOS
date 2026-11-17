# Playbook SDD con LLMs
## Spec-Driven Development: Plan → Build → Validate

| Campo | Detalle |
| :--- | :--- |
| **Tipo de documento** | Playbook de proceso (guía operativa) |
| **Audiencia** | Grupos que desarrollan prototipos asistidos por LLMs |
| **Materia** | Ingeniería de Software I — UNTDF |
| **Versión** | 0.1 |
| **Artefacto de la fase Plan** | [RFC_TEMPLATE.md](./RFC_TEMPLATE.md) |

> **Idea central:** la especificación es la fuente de verdad. El LLM genera código a partir de ella,
> pero la persona decide, revisa y valida. Si el código y la spec no coinciden, se corrige uno de los
> dos de forma explícita; nunca se deja la diferencia sin registrar.

---

## 1. Visión general

```
 SPEC (TPI)        PLAN (RFC)          BUILD               VALIDATE
┌──────────┐    ┌────────────┐    ┌────────────┐    ┌──────────────┐
│ CU, RF,  │──▶ │ Stack,     │──▶ │ Tareas     │──▶ │ Pruebas,     │
│ RNF      │    │ diseño,    │    │ pequeñas   │    │ trazabilidad,│
│          │    │ pruebas    │    │ con LLM    │    │ revisión     │
└──────────┘    └─────┬──────┘    └─────┬──────┘    └──────┬───────┘
                      │   Gate 1        │   Gate 2         │  Gate 3
                      ▼                 ▼                  ▼
                 RFC aprobado      Código que corre    Evidencia + demo
                      ▲                                    │
                      └──────── feedback: se ajusta la spec o el RFC ┘
```

| Fase | Pregunta que responde | Entregable | Puerta de salida |
| :--- | :--- | :--- | :--- |
| **0. Specify** | ¿Qué hay que construir? | Spec del TPI (CU, RF, RNF) | Ya existe |
| **1. Plan** | ¿Cómo lo vamos a construir? | RFC completo | Gate 1 |
| **2. Build** | ¿Lo construimos de a pasos? | Código + registro de prompts | Gate 2 |
| **3. Validate** | ¿Cumple la spec? | Informe de verificación | Gate 3 |

El proceso es iterativo: si en Build o Validate aparece un problema de diseño, se vuelve a Plan y se
actualiza el RFC antes de seguir.

---

## 2. Roles y responsabilidades

| Rol | Responsabilidad | Qué NO se delega al LLM |
| :--- | :--- | :--- |
| **Persona responsable (humana)** | Aprobar gates, decidir ambigüedades, revisar cada cambio | Decisiones de alcance, aprobación de gates |
| **LLM (asistente)** | Proponer diseño, generar código, tests y documentación, ejecutar comandos | Interpretar requisitos ambiguos sin consultar |
| **Revisor (otro integrante)** | Revisar el RFC y el diff antes de cada gate | — |

Regla: **toda persona del grupo debe poder explicar el código que entrega**, aunque lo haya generado el LLM.

---

## 3. Fase 1 — PLAN

**Objetivo:** convertir la spec en un diseño técnico verificable *antes* de escribir código.

### 3.1 Pasos
1. **Leer la spec completa** (CU, RF, RNF, observaciones docentes). Listar ambigüedades y contradicciones.
2. **Resolver ambigüedades con una persona**, no con el LLM. Se anotan en el RFC como decisiones.
3. **Completar el [RFC_TEMPLATE.md](./RFC_TEMPLATE.md)** con ayuda del LLM:
   alcance (real / simulado / fuera), stack, arquitectura, diseño detallado, plan de verificación.
4. **Hacer medibles los RNF** (ej. "rápido" → "< 1 s").
5. **Definir los casos de prueba (TC-xx)** ahora, no después: cada criterio de aceptación debe tener uno.
6. **Dividir el trabajo en tareas chicas** (ver 4.1) y anotarlas en el plan de trabajo del RFC.

### 3.2 Prompt sugerido (plan)
```
Contexto: te paso la spec (CU_<N>, RF-<N>, RNF-<N>) y el template de RFC.
Tarea: completá el RFC. NO escribas código todavía.
Reglas:
- Listá primero las ambigüedades y contradicciones que encuentres y preguntame antes de decidir.
- Cada RF/RNF debe tener al menos un caso de prueba (TC-xx) con resultado medible.
- Distinguí claramente qué es real, qué se simula y qué queda fuera de alcance.
- Proponé 2 alternativas de stack y justificá la recomendada.
```

### 3.3 Gate 1 — RFC aprobado
- [ ] Todas las secciones aplicables del RFC están completas; las que no aplican, marcadas.
- [ ] Ninguna ambigüedad queda sin decisión registrada.
- [ ] Cada RF/RNF tiene al menos un TC con resultado medible.
- [ ] Stack y versiones definidos; el entorno se puede reproducir.
- [ ] Otra persona del grupo revisó el RFC.

---

## 4. Fase 2 — BUILD

**Objetivo:** implementar el RFC en incrementos pequeños, verificables y trazables.

### 4.1 Principios
- **Tareas chicas:** una tarea = un comportamiento verificable (ej. "parsear la trama del sensor"),
  no "hacer el backend".
- **Un ciclo por tarea:** pedir → generar → ejecutar → revisar el diff → commit.
- **Contexto mínimo y explícito:** pasar al LLM solo el RFC, los archivos relevantes y la tarea.
- **Fuente de verdad:** si el LLM propone algo que contradice el RFC, gana el RFC. Si el cambio es
  mejor, se actualiza el RFC primero.
- **Todo corre:** nada se da por hecho hasta que se ejecutó (build, tests o prueba manual).
- **Commits chicos y trazables:** el mensaje del commit referencia el requisito (ej. `RF-11: ...`).

### 4.2 Ciclo por tarea
```
1. Elegir tarea del plan  ─▶  2. Prompt con RFC + tarea + criterio de aceptación
         ▲                                         │
         │                                         ▼
6. Commit + registrar   ◀─  5. Revisar diff  ◀─ 4. Ejecutar/probar  ◀─ 3. LLM genera
```

### 4.3 Prompt sugerido (build)
```
Contexto: este es el RFC aprobado (adjunto) y los archivos relevantes.
Tarea: implementá <tarea concreta> (requisito <RF-xx / CU_xx>).
Criterio de aceptación: <TC-xx, resultado medible>.
Restricciones:
- Respetá el stack y la estructura de carpetas del RFC.
- No agregues funcionalidad fuera del alcance ni dependencias nuevas sin avisar.
- Si algo del RFC es ambiguo o contradictorio, preguntame antes de decidir.
- Al terminar, indicá cómo probarlo y qué archivos modificaste.
```

### 4.4 Qué se registra
Mantené un registro simple (puede ser una tabla en el repo o en el informe):

| Tarea | Requisito | Prompt (resumen) | Qué se corrigió manualmente | Commit |
| :--- | :--- | :--- | :--- | :--- |
| <...> | RF-<N> | <...> | <...> | <hash> |

### 4.5 Gate 2 — Build completo
- [ ] El código corre desde cero con los comandos del RFC (sección "Ejecución").
- [ ] Todas las tareas del plan están hechas o descartadas con justificación.
- [ ] No hay funcionalidad fuera del RFC; si la hay, el RFC fue actualizado.
- [ ] No hay secretos, claves ni datos personales en el repositorio.
- [ ] Cada integrante puede explicar los módulos que entrega.

---

## 5. Fase 3 — VALIDATE

**Objetivo:** demostrar con evidencia que el prototipo cumple la spec.

### 5.1 Niveles de validación

| Nivel | Qué verifica | Cómo |
| :--- | :--- | :--- |
| **Lógica** | Funciones puras, cálculos, parsers | Tests unitarios |
| **Integración** | Frontend ↔ backend ↔ datos | Pruebas de API (curl, Postman, tests) |
| **Aceptación** | Cada criterio de la spec | Ejecutar los TC-xx del RFC y completar "Resultado obtenido" |
| **No funcional** | RNF con métrica | Medir (tiempos, tamaños) y registrar el valor |
| **Revisión humana** | Código y diseño | Revisar el diff completo; no confiar solo en que "funciona" |

### 5.2 Pasos
1. Ejecutar todos los casos de prueba del RFC y completar la columna **Resultado obtenido**.
2. Verificar la **trazabilidad**: cada RF/RNF → TC → código. Marcar lo que quedó sin cubrir.
3. Pedirle al LLM una **revisión crítica** del diff contra el RFC (ver prompt 5.3), y decidir qué se acepta.
4. Probar **escenarios alternativos y errores** (extensiones del CU), no solo el camino feliz.
5. Registrar **desvíos**: qué cambió respecto del RFC y por qué.
6. Preparar la **demo** de 3-5 minutos que recorra el escenario principal y una extensión.

### 5.3 Prompt sugerido (validate)
```
Actuá como revisor. Compará el código adjunto con el RFC y la spec.
Listá:
1. Requisitos (RF/RNF/CU) sin implementar o implementados parcialmente.
2. Comportamientos del código que no están en la spec (alcance extra).
3. Casos límite y errores sin manejar (extensiones del CU).
4. Riesgos de seguridad evidentes (validación de entradas, secretos, inyección).
Para cada punto indicá archivo y línea. No modifiques código.
```

### 5.4 Gate 3 — Validación aprobada
- [ ] Todos los TC-xx ejecutados, con resultado obtenido y evidencia (captura, log o salida de comando).
- [ ] Trazabilidad completa; los requisitos sin cubrir están justificados.
- [ ] Revisión humana del diff completa.
- [ ] Desvíos respecto del RFC documentados en su historial de cambios.
- [ ] La demo fue ensayada desde un entorno limpio.

---

## 6. Reglas de uso responsable de LLMs

| Regla | Motivo |
| :--- | :--- |
| El LLM no decide ambigüedades de la spec | Puede inventar requisitos plausibles pero incorrectos |
| Nunca pegar secretos, claves o datos reales de personas | Privacidad y seguridad |
| Verificar versiones y APIs en la documentación oficial | Los LLMs pueden alucinar funciones o versiones |
| Ejecutar siempre lo generado antes de aceptarlo | "Parece correcto" no es evidencia |
| Declarar el uso de LLM en el informe (herramienta, para qué) | Transparencia académica |
| Si no podés explicar el código, no lo entregues | Responsabilidad individual |

### Anti-patrones frecuentes
- Pedir "hacé todo el prototipo" en un solo prompt.
- Empezar a programar sin RFC aprobado.
- Aceptar cambios del LLM sin leer el diff.
- Escribir las pruebas al final y solo para lo que ya funciona.
- Dejar que el código se desvíe de la spec sin actualizar el RFC.
- Simular una parte (ej. hardware) sin declararlo en el alcance.

---

## 7. Artefactos del proceso

| Artefacto | Fase | Plantilla / ubicación |
| :--- | :--- | :--- |
| Spec (CU, RF, RNF) | 0 | TPI del grupo |
| RFC técnico | 1 | [RFC_TEMPLATE.md](./RFC_TEMPLATE.md) |
| Registro de prompts y tareas | 2 | Tabla de la sección 4.4 |
| Código y README de ejecución | 2 | Repositorio del grupo |
| Informe de verificación (TC-xx completados) | 3 | Plan de verificación del RFC |
| Demo | 3 | Guion de 3-5 minutos |

---

## 8. Resumen en una página

1. **Plan:** spec → ambigüedades resueltas → RFC con pruebas definidas → **Gate 1**.
2. **Build:** tareas chicas → prompt con RFC → ejecutar → revisar diff → commit → **Gate 2**.
3. **Validate:** correr TC-xx → trazabilidad → revisión crítica → desvíos documentados → **Gate 3**.
4. **Siempre:** la persona decide, el RFC manda y todo se ejecuta antes de aceptarse.

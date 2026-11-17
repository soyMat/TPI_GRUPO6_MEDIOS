# AGENTS.md

Instrucciones para asistentes de IA (LLMs) que trabajan en este repositorio.

## Regla principal

**Toda feature nueva debe seguir el proceso definido en [SDD_PLAYBOOK.md](./SDD_PLAYBOOK.md)**
(Plan → Build → Validate). No se escribe código de una feature sin pasar antes por la fase Plan.

| Fase | Qué debés hacer | Referencia |
| :--- | :--- | :--- |
| **Plan** | Completar o actualizar el RFC de la feature a partir de [RFC_TEMPLATE.md](./RFC_TEMPLATE.md). Listar ambigüedades y preguntar antes de decidir. Definir los casos de prueba (TC-xx). | Playbook, sección 3 |
| **Build** | Implementar por tareas chicas, ejecutar lo generado y referenciar el requisito. | Playbook, sección 4 |
| **Validate** | Correr los TC-xx, verificar la trazabilidad y documentar los desvíos. | Playbook, sección 5 |

## Reglas de trabajo

- La fuente de verdad es el RFC de la feature (`RFC_<SPEC>.md`). No implementes nada que no esté en el RFC.
- Si el RFC de la feature no existe o no está aprobado, detenete y proponé completarlo antes de programar.
- Ante ambigüedades o contradicciones en la spec o el RFC, preguntá antes de decidir.
- Trabajá por tareas chicas: una tarea es un comportamiento verificable.
- Ejecutá lo que generes (build, tests o prueba manual) antes de darlo por terminado.
- Referenciá el requisito (RF, RNF o CU) en los commits y en los tests.
- No agregues dependencias ni archivos fuera de la estructura del RFC sin avisar.
- Si un cambio mejora el diseño pero contradice el RFC, actualizá el RFC primero y registrá el desvío en su historial.
- No incluyas secretos, claves ni datos personales reales en el código ni en los prompts.
- Verificá versiones y APIs en la documentación oficial; no asumas que existen.

## Al finalizar una tarea

Informá:
1. Qué archivos modificaste.
2. Cómo probarlo (comandos exactos).
3. Qué requisito y qué TC-xx cubre.
4. Desvíos respecto del RFC, si los hubo.

## Prohibido

- Implementar una feature sin RFC aprobado.
- Pedir o generar "todo el prototipo" en un solo paso.
- Dejar que el código se desvíe de la spec sin actualizar el RFC.
- Simular una parte del sistema (hardware, servicios externos) sin declararlo en el alcance del RFC.

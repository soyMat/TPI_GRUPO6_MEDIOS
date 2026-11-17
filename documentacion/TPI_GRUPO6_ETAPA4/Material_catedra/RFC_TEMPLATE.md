# RFC Técnico: <Nombre del Spec / Prototipo>
## <Subtítulo: qué se va a construir>

> **Cómo usar este template:** copiá el archivo, reemplazá todo lo que está entre `<...>` y borrá las
> notas en cita (`>`) y las secciones que no apliquen (indicando "No aplica" y por qué, si es relevante).
> Un RFC corto y concreto es mejor que uno largo y genérico.

| Campo | Detalle |
| :--- | :--- |
| **Título** | RFC-<SPEC N>: <título corto> |
| **Proyecto** | <nombre del proyecto / cliente> |
| **Materia / Grupo** | <materia> — Grupo <N> |
| **Integrantes** | <nombres> |
| **Fecha** | <mes año> |
| **Estado** | Borrador / En revisión / Aprobado / Implementado |
| **Revisores** | <docente / compañeros que deben opinar> |

---

## 1. Alcance del Prototipo y Enfoque

> Definí qué partes del sistema se construyen de verdad, cuáles se simulan y cuáles se omiten.

| Componente | Real / Simulado / Fuera de alcance | Nota |
| :--- | :--- | :--- |
| <ej. Interfaz de usuario> | Real | <...> |
| <ej. Hardware/sensor> | Simulado | <cómo se simula> |
| <ej. Plataforma web> | Fuera de alcance | <por qué> |

### 1.1 Alternativas evaluadas

| Criterio | Opción A: <...> | Opción B: <...> |
| :--- | :--- | :--- |
| Complejidad | | |
| Cobertura del Spec | | |
| Riesgo / tiempo | | |

**Decisión:** <opción elegida y por qué>.

---

## 2. Stack Tecnológico

| Capa | Tecnología | Versión | Motivo de la elección |
| :--- | :--- | :--- | :--- |
| Frontend | <lenguaje / framework> | | |
| Backend | <lenguaje / framework> | | |
| Persistencia | <BD / archivos> | | |
| Integraciones externas | <APIs, protocolos, librerías> | | |
| Herramientas | <editor, control de versiones, testing> | | |

### 2.1 Requisitos del entorno
* <SO / navegador / runtime necesarios>
* <Dependencias a instalar>

---

## 3. Arquitectura

> Un diagrama simple (ASCII, Mermaid o imagen) con los componentes y cómo se comunican.

```
<diagrama de componentes>
```

### 3.1 Componentes y responsabilidades

| Componente | Responsabilidad | Depende de |
| :--- | :--- | :--- |
| <...> | <...> | <...> |

### 3.2 Alineación con el modelo de clases del proyecto

> Indicá qué clases del diagrama de clases del TPI se implementan y cómo se llaman en el código.
> Señalá operaciones o atributos que hubo que agregar al modelo.

| Clase del modelo | Implementación en código | Cambios respecto del modelo |
| :--- | :--- | :--- |
| <...> | <...> | <...> |

---

## 4. Diseño Detallado

### 4.1 Flujo principal
> Secuencia resumida del escenario principal del CU, mapeada a llamadas entre componentes.
> Este apartado puede incluir **diagramas de secuencia, de comunicación o de actividad** (ASCII,
> Mermaid o imagen) además de, o en lugar de, la lista de pasos.

1. <Paso>
2. <Paso>

### 4.2 Estados y transiciones (si hay comportamiento con estados)

> Este apartado puede incluir un **diagrama de máquina de estados** (ASCII, Mermaid o imagen)
> además de, o en lugar de, la tabla.

| Estado | Evento | Siguiente estado | Efecto visible / sonoro |
| :--- | :--- | :--- | :--- |
| <...> | <...> | <...> | <...> |

### 4.3 Escenarios alternativos y manejo de errores

| Extensión del CU | Condición | Comportamiento del sistema |
| :--- | :--- | :--- |
| <ej. 3a> | <...> | <...> |

### 4.4 Interfaz de usuario
> Pantallas o wireframes, ubicación de cada elemento y estados visuales.

---

## 5. Modelo de Datos (opcional)

> Sección opcional: omitila si el prototipo no persiste datos.

```sql
-- Esquema de tablas / estructuras de datos
```

> Aclarar qué datos persisten localmente y cuáles se envían a otro sistema, si aplica.

---

## 6. Interfaces (API / Protocolos) (opcional)

> Sección opcional: omitila si el prototipo no expone APIs ni usa protocolos externos.

### 6.1 Endpoints o contratos internos

| Método | Ruta / operación | Entrada | Salida | Errores |
| :--- | :--- | :--- | :--- | :--- |
| <POST> | </api/...> | `{...}` | `{...}` | <códigos> |

### 6.2 Protocolos o servicios externos
> Documentación de referencia, identificadores, formatos de mensaje, límites (rate limits, claves de API).

---

## 7. Estructura del Código

```
<carpeta>/
├── <archivo o módulo>     # <descripción>
└── ...
```

### 7.1 Ejecución del prototipo

```
<comandos exactos para instalar y correr>
```

---

## 8. Plan de Verificación

| ID | Criterio de aceptación | Procedimiento | Resultado esperado | Resultado obtenido |
| :--- | :--- | :--- | :--- | :--- |
| TC-01 | <criterio del Spec> | <pasos> | <resultado medible> | <completar al probar> |

> Cada criterio de aceptación del Spec debe tener al menos una prueba. Completá la última columna
> cuando termines el prototipo.

---

## 9. Riesgos y Preguntas Abiertas

| # | Riesgo / pregunta | Impacto | Mitigación / quién responde |
| :--- | :--- | :--- | :--- |
| 1 | <...> | Alto / Medio / Bajo | <...> |

---

## 10. Plan de Trabajo

| Tarea | Responsable | Estimación | Estado |
| :--- | :--- | :--- | :--- |
| <...> | <...> | <...> | Pendiente |

---

## 11. Historial de Cambios

| Versión | Fecha | Autor | Cambio |
| :--- | :--- | :--- | :--- |
| 0.1 | <fecha> | <autor> | Borrador inicial |

---

## Checklist antes de pasar a "Aprobado"

- [ ] Cada RF/RNF del Spec está cubierto por al menos una prueba del plan de verificación (sección 8).
- [ ] Los RNF tienen una métrica concreta (tiempo, tamaño, porcentaje).
- [ ] Está claro qué es real y qué es simulado.
- [ ] Los lenguajes, versiones y dependencias están especificados.
- [ ] Los comandos de ejecución fueron probados desde cero.
- [ ] Cada criterio de aceptación del Spec tiene al menos un caso de prueba.

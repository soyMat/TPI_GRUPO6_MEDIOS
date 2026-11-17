(() => {
  "use strict";

  const CAMPOS_FORMULARIO = ["tipo_id", "cantidad", "desde", "hasta", "materia_id"];

  const estado = {
    datosPrevalidados: null,
    resultadoPrevalidacion: null,
    enviandoPrevalidacion: false,
    enviandoConfirmacion: false,
    vistaActual: "formulario",
  };

  // Referencias DOM
  const selectUsuario = document.getElementById("usuario-demo");
  const tabSolicitar = document.getElementById("tab-solicitar");
  const tabMisSolicitudes = document.getElementById("tab-mis-solicitudes");

  const alertaGlobal = document.getElementById("alerta-global");
  const alertaTitulo = document.getElementById("alerta-titulo");
  const alertaMensaje = document.getElementById("alerta-mensaje");
  const alertaDetalles = document.getElementById("alerta-detalles");
  const btnCerrarAlerta = document.getElementById("btn-cerrar-alerta");

  const vistaFormulario = document.getElementById("vista-formulario");
  const vistaResumen = document.getElementById("vista-resumen");
  const vistaConfirmacion = document.getElementById("vista-confirmacion");
  const vistaMisSolicitudes = document.getElementById("vista-mis-solicitudes");

  const formSolicitud = document.getElementById("form-solicitud");
  const inputTipo = document.getElementById("tipo_id");
  const inputCantidad = document.getElementById("cantidad");
  const inputDesde = document.getElementById("desde");
  const inputHasta = document.getElementById("hasta");
  const inputMateria = document.getElementById("materia_id");
  const btnSugerir48h = document.getElementById("btn-sugerir-48h");
  const btnCancelarForm = document.getElementById("btn-cancelar-form");
  const btnContinuar = document.getElementById("btn-continuar");

  const resumenUsuario = document.getElementById("resumen-usuario");
  const resumenTipo = document.getElementById("resumen-tipo");
  const resumenCantidad = document.getElementById("resumen-cantidad");
  const resumenDesde = document.getElementById("resumen-desde");
  const resumenHasta = document.getElementById("resumen-hasta");
  const resumenMateria = document.getElementById("resumen-materia");
  const resumenCondicionAval = document.getElementById("resumen-condicion-aval");
  const avisoAvalResumen = document.getElementById("aviso-aval-resumen");
  const btnCancelarResumen = document.getElementById("btn-cancelar-resumen");
  const btnVolver = document.getElementById("btn-volver");
  const btnConfirmar = document.getElementById("btn-confirmar");

  const confirmacionNumero = document.getElementById("confirmacion-numero");
  const confirmacionEstado = document.getElementById("confirmacion-estado");
  const confirmacionDetalleAval = document.getElementById("confirmacion-detalle-aval");
  const cajaAdvertencias = document.getElementById("caja-advertencias");
  const listaAdvertencias = document.getElementById("lista-advertencias");
  const btnNuevaSolicitud = document.getElementById("btn-nueva-solicitud");
  const btnIrMisSolicitudes = document.getElementById("btn-ir-mis-solicitudes");

  const etiquetaUsuarioListado = document.getElementById("etiqueta-usuario-listado");
  const btnRefrescarSolicitudes = document.getElementById("btn-refrescar-solicitudes");
  const estadoListado = document.getElementById("estado-listado");
  const tablaSolicitudes = document.getElementById("tabla-solicitudes");
  const cuerpoTablaSolicitudes = document.getElementById("cuerpo-tabla-solicitudes");

  function obtenerAliasDemo() {
    return selectUsuario.value;
  }

  function mostrarAlerta(titulo, mensaje, errores = []) {
    alertaTitulo.textContent = titulo;
    alertaMensaje.textContent = mensaje;
    alertaDetalles.innerHTML = "";

    if (Array.isArray(errores) && errores.length > 0) {
      errores.forEach((err) => {
        const li = document.createElement("li");
        const prefijo = err.campo ? `[${err.campo}] ` : "";
        li.textContent = `${prefijo}${err.mensaje || err.codigo || "Error de validación"}`;
        alertaDetalles.appendChild(li);
      });
      alertaDetalles.classList.remove("oculto");
    } else {
      alertaDetalles.classList.add("oculto");
    }

    alertaGlobal.classList.remove("oculto");
  }

  function ocultarAlerta() {
    alertaGlobal.classList.add("oculto");
    alertaDetalles.innerHTML = "";
  }

  function limpiarErroresCampos() {
    CAMPOS_FORMULARIO.forEach((campo) => {
      const control = document.getElementById(campo);
      const mensajeCampo = document.getElementById(`error-${campo}`);
      if (control) {
        control.classList.remove("campo-invalido");
      }
      if (mensajeCampo) {
        mensajeCampo.textContent = "";
        mensajeCampo.classList.add("oculto");
      }
    });
  }

  function mostrarErroresEnCampos(errores) {
    limpiarErroresCampos();
    if (!Array.isArray(errores)) return;

    errores.forEach((err) => {
      if (!err.campo) return;
      const control = document.getElementById(err.campo);
      const mensajeCampo = document.getElementById(`error-${err.campo}`);
      if (control) {
        control.classList.add("campo-invalido");
      }
      if (mensajeCampo) {
        mensajeCampo.textContent = err.mensaje || "Dato inválido.";
        mensajeCampo.classList.remove("oculto");
      }
    });
  }

  function activarVista(nombreVista) {
    estado.vistaActual = nombreVista;

    vistaFormulario.classList.toggle("oculto", nombreVista !== "formulario");
    vistaResumen.classList.toggle("oculto", nombreVista !== "resumen");
    vistaConfirmacion.classList.toggle("oculto", nombreVista !== "confirmacion");
    vistaMisSolicitudes.classList.toggle("oculto", nombreVista !== "mis-solicitudes");

    const enFlujoSolicitud = nombreVista !== "mis-solicitudes";
    tabSolicitar.classList.toggle("activo", enFlujoSolicitud);
    tabSolicitar.setAttribute("aria-pressed", String(enFlujoSolicitud));

    tabMisSolicitudes.classList.toggle("activo", !enFlujoSolicitud);
    tabMisSolicitudes.setAttribute("aria-pressed", String(!enFlujoSolicitud));
  }

  function formatearFechaHoraLegible(valorIso) {
    if (!valorIso) return "—";
    const fecha = new Date(valorIso);
    if (Number.isNaN(fecha.getTime())) {
      return String(valorIso).replace("T", " ");
    }
    return fecha.toLocaleString("es-AR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function formatearParaDatetimeLocal(fecha) {
    const pad = (n) => String(n).padStart(2, "0");
    return (
      `${fecha.getFullYear()}-${pad(fecha.getMonth() + 1)}-${pad(fecha.getDate())}` +
      `T${pad(fecha.getHours())}:${pad(fecha.getMinutes())}`
    );
  }

  function sugerirVencimiento48h(forzar = false) {
    if (!inputDesde.value) return;
    if (!forzar && inputHasta.value) return;

    const inicio = new Date(inputDesde.value);
    if (Number.isNaN(inicio.getTime())) return;

    const finSugerido = new Date(inicio.getTime() + 48 * 60 * 60 * 1000);
    inputHasta.value = formatearParaDatetimeLocal(finSugerido);
  }

  function normalizarFechaIso(valorDatetimeLocal) {
    if (!valorDatetimeLocal) return "";
    return valorDatetimeLocal.length === 16 ? `${valorDatetimeLocal}:00` : valorDatetimeLocal;
  }

  function construirPayloadSolicitud() {
    const cantidadNumero = Number.parseInt(inputCantidad.value, 10);
    return {
      tipo_id: inputTipo.value,
      cantidad: Number.isNaN(cantidadNumero) ? 0 : cantidadNumero,
      desde: normalizarFechaIso(inputDesde.value),
      hasta: normalizarFechaIso(inputHasta.value),
      materia_id: inputMateria.value,
    };
  }

  async function interpretarErrorRespuesta(respuesta) {
    let cuerpo = null;
    try {
      cuerpo = await respuesta.json();
    } catch (_err) {
      cuerpo = null;
    }

    const detail = cuerpo && typeof cuerpo.detail === "object" ? cuerpo.detail : null;
    const codigo = detail?.codigo || `HTTP_${respuesta.status}`;
    const mensaje =
      detail?.mensaje ||
      (typeof cuerpo?.detail === "string" ? cuerpo.detail : null) ||
      `Error inesperado del servidor (HTTP ${respuesta.status}).`;
    const errores = Array.isArray(detail?.errores) ? detail.errores : [];

    return { status: respuesta.status, codigo, mensaje, errores };
  }

  function tituloParaStatus(status) {
    if (status === 403) return "Acceso o elegibilidad denegada (HTTP 403)";
    if (status === 409) return "Conflicto de disponibilidad (HTTP 409)";
    if (status === 422) return "Datos de solicitud inválidos (HTTP 422)";
    if (status === 503) return "Servicio no configurado (HTTP 503)";
    return `No se pudo completar la operación (HTTP ${status})`;
  }

  async function cargarCatalogos() {
    try {
      const [respTipos, respMaterias] = await Promise.all([
        fetch("/api/equipos/tipos"),
        fetch("/api/materias"),
      ]);

      if (!respTipos.ok) {
        const err = await interpretarErrorRespuesta(respTipos);
        mostrarAlerta(tituloParaStatus(err.status), err.mensaje);
        return;
      }
      if (!respMaterias.ok) {
        const err = await interpretarErrorRespuesta(respMaterias);
        mostrarAlerta(tituloParaStatus(err.status), err.mensaje);
        return;
      }

      const tipos = await respTipos.json();
      const materias = await respMaterias.json();

      inputTipo.innerHTML = '<option value="">Seleccioná un tipo de equipamiento...</option>';
      tipos.forEach((tipo) => {
        const opt = document.createElement("option");
        opt.value = tipo.id;
        opt.textContent = tipo.alta_gama ? `${tipo.nombre} [Alta gama]` : tipo.nombre;
        inputTipo.appendChild(opt);
      });

      inputMateria.innerHTML = '<option value="">Seleccioná una materia o proyecto...</option>';
      materias.forEach((materia) => {
        const opt = document.createElement("option");
        opt.value = materia.id;
        opt.textContent = materia.nombre;
        inputMateria.appendChild(opt);
      });
    } catch (_error) {
      mostrarAlerta(
        "Error de conexión",
        "No se pudieron cargar los catálogos iniciales desde el servidor."
      );
    }
  }

  function inicializarFechasPorDefecto() {
    const manana = new Date(Date.now() + 24 * 60 * 60 * 1000);
    manana.setMinutes(0, 0, 0);
    inputDesde.value = formatearParaDatetimeLocal(manana);
    sugerirVencimiento48h(true);
  }

  function reiniciarFlujoSolicitud(limpiarMensajeGlobal = true) {
    if (limpiarMensajeGlobal) {
      ocultarAlerta();
    }
    limpiarErroresCampos();
    estado.datosPrevalidados = null;
    estado.resultadoPrevalidacion = null;
    formSolicitud.reset();
    inputCantidad.value = "1";
    inicializarFechasPorDefecto();
    activarVista("formulario");
  }

  function renderizarResumen(resultado) {
    const resumen = resultado.resumen || {};
    resumenUsuario.textContent = selectUsuario.options[selectUsuario.selectedIndex]?.text || obtenerAliasDemo();
    resumenTipo.textContent = resumen.tipo || inputTipo.value;
    resumenCantidad.textContent = String(resumen.cantidad ?? inputCantidad.value);
    resumenDesde.textContent = formatearFechaHoraLegible(resumen.desde);
    resumenHasta.textContent = formatearFechaHoraLegible(resumen.hasta);
    resumenMateria.textContent = resumen.materia || inputMateria.value;

    const requiereAval = Boolean(resultado.requiere_aval);
    resumenCondicionAval.textContent = requiereAval
      ? "Pendiente/Solicitada · Requiere aval docente posterior"
      : "Pendiente/Solicitada · Sin aval docente requerido";

    avisoAvalResumen.classList.toggle("oculto", !requiereAval);
  }

  async function manejarPrevalidacion(evento) {
    evento.preventDefault();
    if (estado.enviandoPrevalidacion) return;

    ocultarAlerta();
    limpiarErroresCampos();

    const payload = construirPayloadSolicitud();
    estado.enviandoPrevalidacion = true;
    btnContinuar.disabled = true;
    btnContinuar.textContent = "Validando...";

    try {
      const respuesta = await fetch("/api/solicitudes/prevalidar", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Usuario-Demo": obtenerAliasDemo(),
        },
        body: JSON.stringify(payload),
      });

      if (!respuesta.ok) {
        const err = await interpretarErrorRespuesta(respuesta);
        mostrarErroresEnCampos(err.errores);
        mostrarAlerta(tituloParaStatus(err.status), err.mensaje, err.errores);
        return;
      }

      const resultado = await respuesta.json();
      if (!resultado.valido) {
        mostrarErroresEnCampos(resultado.errores || []);
        mostrarAlerta(
          "La solicitud no puede continuar",
          "Corregí los inconvenientes detectados antes de avanzar.",
          resultado.errores || []
        );
        return;
      }

      estado.datosPrevalidados = payload;
      estado.resultadoPrevalidacion = resultado;
      renderizarResumen(resultado);
      activarVista("resumen");
    } catch (_error) {
      mostrarAlerta(
        "Error de conexión",
        "No se pudo comunicar con el servidor para prevalidar la solicitud."
      );
    } finally {
      estado.enviandoPrevalidacion = false;
      btnContinuar.disabled = false;
      btnContinuar.textContent = "Continuar";
    }
  }

  async function manejarConfirmacion() {
    if (estado.enviandoConfirmacion || !estado.datosPrevalidados) return;

    ocultarAlerta();
    estado.enviandoConfirmacion = true;
    btnConfirmar.disabled = true;
    btnVolver.disabled = true;
    btnCancelarResumen.disabled = true;
    btnConfirmar.textContent = "Confirmando...";

    try {
      const respuesta = await fetch("/api/solicitudes", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Usuario-Demo": obtenerAliasDemo(),
        },
        body: JSON.stringify(estado.datosPrevalidados),
      });

      if (!respuesta.ok) {
        const err = await interpretarErrorRespuesta(respuesta);
        mostrarErroresEnCampos(err.errores);
        mostrarAlerta(tituloParaStatus(err.status), err.mensaje, err.errores);
        // Ante conflicto de revalidación (409) o error de datos (422), volver al formulario conservando valores
        if (err.status === 409 || err.status === 422) {
          activarVista("formulario");
        }
        return;
      }

      const creada = await respuesta.json();
      confirmacionNumero.textContent = creada.numero || "—";
      confirmacionEstado.textContent = creada.estado || "PENDIENTE_SOLICITADA";

      if (creada.requiere_aval) {
        confirmacionDetalleAval.innerHTML =
          '<strong>Estado de aval:</strong> Pendiente de aval docente posterior (CU_03). Se generó una notificación interna.';
      } else {
        confirmacionDetalleAval.innerHTML =
          '<strong>Estado de aval:</strong> No requiere aval docente adicional; queda pendiente de evaluación operativa.';
      }

      listaAdvertencias.innerHTML = "";
      if (Array.isArray(creada.advertencias) && creada.advertencias.length > 0) {
        creada.advertencias.forEach((adv) => {
          const li = document.createElement("li");
          li.textContent = adv;
          listaAdvertencias.appendChild(li);
        });
        cajaAdvertencias.classList.remove("oculto");
      } else {
        cajaAdvertencias.classList.add("oculto");
      }

      estado.datosPrevalidados = null;
      estado.resultadoPrevalidacion = null;
      activarVista("confirmacion");
    } catch (_error) {
      mostrarAlerta(
        "Error de conexión",
        "No se pudo registrar la solicitud. Verificá que el servidor local esté activo."
      );
    } finally {
      estado.enviandoConfirmacion = false;
      btnConfirmar.disabled = false;
      btnVolver.disabled = false;
      btnCancelarResumen.disabled = false;
      btnConfirmar.textContent = "Confirmar";
    }
  }

  async function cargarMisSolicitudes() {
    const alias = obtenerAliasDemo();
    etiquetaUsuarioListado.textContent = alias;
    estadoListado.textContent = "Cargando solicitudes...";
    tablaSolicitudes.classList.add("oculto");
    cuerpoTablaSolicitudes.innerHTML = "";

    try {
      const respuesta = await fetch("/api/solicitudes/mias", {
        headers: {
          "X-Usuario-Demo": alias,
        },
      });

      if (!respuesta.ok) {
        const err = await interpretarErrorRespuesta(respuesta);
        estadoListado.textContent = "No fue posible obtener el listado para el usuario seleccionado.";
        mostrarAlerta(tituloParaStatus(err.status), err.mensaje, err.errores);
        return;
      }

      const solicitudes = await respuesta.json();
      if (!Array.isArray(solicitudes) || solicitudes.length === 0) {
        estadoListado.textContent = "Todavía no hay solicitudes registradas para este usuario de demostración.";
        return;
      }

      estadoListado.textContent = `Se encontraron ${solicitudes.length} solicitud(es).`;
      solicitudes.forEach((sol) => {
        const tr = document.createElement("tr");

        const tdNumero = document.createElement("td");
        tdNumero.textContent = sol.numero;

        const tdTipo = document.createElement("td");
        tdTipo.textContent = sol.tipo;

        const tdCantidad = document.createElement("td");
        tdCantidad.textContent = String(sol.cantidad);

        const tdPeriodo = document.createElement("td");
        tdPeriodo.textContent = `${formatearFechaHoraLegible(sol.desde)} → ${formatearFechaHoraLegible(sol.hasta)}`;

        const tdMateria = document.createElement("td");
        tdMateria.textContent = sol.materia;

        const tdEstado = document.createElement("td");
        const spanEstado = document.createElement("span");
        spanEstado.className = "badge badge-pendiente";
        spanEstado.textContent = sol.estado;
        tdEstado.appendChild(spanEstado);

        const tdAval = document.createElement("td");
        const spanAval = document.createElement("span");
        if (sol.requiere_aval) {
          spanAval.className = "badge badge-aval";
          spanAval.textContent = "Pendiente · Requiere aval docente";
        } else {
          spanAval.className = "badge badge-sin-aval";
          spanAval.textContent = "Pendiente · Sin aval requerido";
        }
        tdAval.appendChild(spanAval);

        tr.append(tdNumero, tdTipo, tdCantidad, tdPeriodo, tdMateria, tdEstado, tdAval);
        cuerpoTablaSolicitudes.appendChild(tr);
      });

      tablaSolicitudes.classList.remove("oculto");
    } catch (_error) {
      estadoListado.textContent = "Error de conexión al consultar las solicitudes.";
      mostrarAlerta(
        "Error de conexión",
        "No se pudo consultar el historial de solicitudes del usuario."
      );
    }
  }

  // Eventos de navegación y controles
  btnCerrarAlerta.addEventListener("click", ocultarAlerta);

  inputDesde.addEventListener("change", () => {
    sugerirVencimiento48h(false);
  });

  btnSugerir48h.addEventListener("click", () => {
    sugerirVencimiento48h(true);
  });

  formSolicitud.addEventListener("submit", manejarPrevalidacion);

  btnCancelarForm.addEventListener("click", () => {
    reiniciarFlujoSolicitud(true);
  });

  btnVolver.addEventListener("click", () => {
    // CU_01 5a: conservar los valores cargados en el formulario al volver desde el resumen
    ocultarAlerta();
    activarVista("formulario");
  });

  btnCancelarResumen.addEventListener("click", () => {
    // CU_01 5b: cancelar sin registrar solicitud
    reiniciarFlujoSolicitud(true);
  });

  btnConfirmar.addEventListener("click", manejarConfirmacion);

  btnNuevaSolicitud.addEventListener("click", () => {
    reiniciarFlujoSolicitud(true);
  });

  btnIrMisSolicitudes.addEventListener("click", () => {
    ocultarAlerta();
    activarVista("mis-solicitudes");
    cargarMisSolicitudes();
  });

  tabSolicitar.addEventListener("click", () => {
    ocultarAlerta();
    if (estado.vistaActual === "mis-solicitudes") {
      activarVista(estado.datosPrevalidados ? "resumen" : "formulario");
    }
  });

  tabMisSolicitudes.addEventListener("click", () => {
    ocultarAlerta();
    activarVista("mis-solicitudes");
    cargarMisSolicitudes();
  });

  btnRefrescarSolicitudes.addEventListener("click", () => {
    ocultarAlerta();
    cargarMisSolicitudes();
  });

  selectUsuario.addEventListener("change", () => {
    ocultarAlerta();
    if (estado.vistaActual === "mis-solicitudes") {
      cargarMisSolicitudes();
    } else if (estado.vistaActual === "resumen") {
      // Si cambia el usuario demo en medio del resumen, invalidar prevalidación previa y volver al formulario
      estado.datosPrevalidados = null;
      estado.resultadoPrevalidacion = null;
      activarVista("formulario");
    }
  });

  // Inicialización
  inicializarFechasPorDefecto();
  cargarCatalogos();
})();
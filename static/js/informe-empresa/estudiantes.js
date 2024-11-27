let timeoutId;
const busquedaInput = document.getElementById("busqueda_estudiante");
const tablaEstudiantes = document
    .getElementById("tabla_estudiantes")
    .getElementsByTagName("tbody")[0];
const estudianteSeleccionadoInput = document.getElementById(
    "estudiante_seleccionado"
);
const estudianteSeleccionadoNombre = document.getElementById(
    "estudiante_seleccionado_nombre"
);
const fechaInicioInput = document.getElementById("fecha_inicio");
const fechaFinInput = document.getElementById("fecha_fin");
const btnLimpiar = document.getElementById("limpiar_estudiante");

busquedaInput.addEventListener("input", function () {
    clearTimeout(timeoutId);
    const termino = this.value.trim();

    // Limpiar tabla si el input está vacío
    if (termino.length === 0) {
        tablaEstudiantes.innerHTML = "";
        return;
    }

    if (termino.length < 2) return;

    timeoutId = setTimeout(() => {
        fetch(`${URLS.buscarEstudiantes}?termino=${encodeURIComponent(termino)}`)
            .then((response) => response.json())
            .then((estudiantes) => {
                actualizarTablaEstudiantes(estudiantes);
            })
            .catch((error) => console.error("Error:", error));
    }, 300);
});

function actualizarTablaEstudiantes(estudiantes) {
    tablaEstudiantes.innerHTML = "";

    estudiantes.forEach((estudiante) => {
        const fila = tablaEstudiantes.insertRow();
        fila.innerHTML = `
                <td>${estudiante.apellidos}, ${estudiante.nombre}</td>
                <td>${estudiante.fechaInicio}</td>
                <td>${estudiante.fechaFin}</td>
                <td>
                    <button type="button" 
                            class="btn btn-primary btn-sm"
                            onclick="seleccionarEstudiante('${estudiante.idPersona}', 
                                                        '${estudiante.apellidos}, ${estudiante.nombre}',
                                                        '${estudiante.fechaInicio}',
                                                        '${estudiante.fechaFin}')">
                        Seleccionar
                    </button>
                </td>
            `;
    });
}

function seleccionarEstudiante(id, nombreCompleto, fechaInicio, fechaFin) {
    estudianteSeleccionadoInput.value = id;
    estudianteSeleccionadoNombre.value = nombreCompleto;
    fechaInicioInput.value = fechaInicio;
    fechaFinInput.value = fechaFin;
}

btnLimpiar.addEventListener("click", function () {
    estudianteSeleccionadoInput.value = "";
    estudianteSeleccionadoNombre.value = "";
    fechaInicioInput.value = "";
    fechaFinInput.value = "";
    busquedaInput.value = "";
    tablaEstudiantes.innerHTML = "";
});


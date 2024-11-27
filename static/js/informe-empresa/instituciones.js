let timeoutIdInstitucion;
const busquedaInstitucionInput = document.getElementById("busqueda_institucion");
const tablaInstituciones = document.getElementById("tabla_instituciones").getElementsByTagName('tbody')[0];
const institucionSeleccionadaInput = document.getElementById("institucion_seleccionada");
const institucionSeleccionadaNombre = document.getElementById("institucion_seleccionada_nombre");
const responsableInput = document.getElementById("responsable");
const cargoResponsableInput = document.getElementById("cargo_responsable");
const btnLimpiarInstitucion = document.getElementById("limpiar_institucion");

busquedaInstitucionInput.addEventListener("input", function () {
    clearTimeout(timeoutIdInstitucion);
    const termino = this.value.trim();

    // Limpiar tabla si el input está vacío
    if (termino.length === 0) {
        tablaInstituciones.innerHTML = '';
        return;
    }

    if (termino.length < 2) return;

    timeoutIdInstitucion = setTimeout(() => {
        fetch(`${URLS.buscarInstituciones}?termino=${encodeURIComponent(termino)}`)
            .then(response => response.json())
            .then(instituciones => {
                actualizarTablaInstituciones(instituciones);
            })
            .catch(error => console.error("Error:", error));
    }, 300);
});

function actualizarTablaInstituciones(instituciones) {
    tablaInstituciones.innerHTML = '';

    instituciones.forEach(institucion => {
        const fila = tablaInstituciones.insertRow();
        fila.innerHTML = `
                <td>${institucion.numDoc}</td>
                <td>${institucion.razonSocial}</td>
                <td>${institucion.responsable}</td>
                <td>${institucion.cargo}</td>
                <td>
                    <button type="button" 
                            class="btn btn-primary btn-sm"
                            onclick="seleccionarInstitucion('${institucion.numDoc}', 
                                                        '${institucion.razonSocial}',
                                                        '${institucion.responsable}',
                                                        '${institucion.cargo}')">
                        Seleccionar
                    </button>
                </td>
            `;
    });
}

function seleccionarInstitucion(numDoc, razonSocial, responsable, cargo) {
    institucionSeleccionadaInput.value = numDoc;
    institucionSeleccionadaNombre.value = razonSocial;
    responsableInput.value = responsable;
    cargoResponsableInput.value = cargo;
}

btnLimpiarInstitucion.addEventListener("click", function () {
    institucionSeleccionadaInput.value = '';
    institucionSeleccionadaNombre.value = '';
    responsableInput.value = '';
    cargoResponsableInput.value = '';
    busquedaInstitucionInput.value = '';
    tablaInstituciones.innerHTML = '';
});

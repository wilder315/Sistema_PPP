window.laboresPrincipales = new Map();
document.addEventListener('DOMContentLoaded', function () {
    // Variables globales
    let caracteresUsadosTotales = 0;
    const LIMITE_CARACTERES = 250;

    // Inicialización de elementos
    const modalLaborPrincipal = new bootstrap.Modal(document.getElementById('modalLaborPrincipal'));
    const modalLaboresEspecificas = new bootstrap.Modal(document.getElementById('modalLaboresEspecificas'));


    const inputLabor = document.getElementById('nuevaLabor');
    const contadorCaracteres = document.getElementById('contadorCaracteres');
    const btnRegistrarLabor = document.getElementById('btnRegistrarLabor');
    const btnGuardarLaboresEspecificas = document.getElementById('btnGuardarLaboresEspecificas');
    const tablaLabores = document.getElementById('tablaLabores').getElementsByTagName('tbody')[0];
    const inputLaborEspecifica = document.getElementById('nuevaLaborEspecifica');
    const btnAgregarLaborEspecifica = document.getElementById('btnAgregarLaborEspecifica');
    const listaLaboresEspecificas = document.getElementById('listaLaboresEspecificas');
    let laborSeleccionadaId = null;
    let laboresEspecificasTemp = [];

    // Inicializar estado del botón de guardar labores específicas
    btnGuardarLaboresEspecificas.disabled = true;

    // Estilos para el contador
    contadorCaracteres.style.transition = 'color 0.3s';

    // Función para calcular caracteres totales
    function actualizarCaracteresTotales() {
        caracteresUsadosTotales = 0;
        laboresPrincipales.forEach((labor) => {
            caracteresUsadosTotales += labor.texto.length;
        });
        const disponibles = LIMITE_CARACTERES - caracteresUsadosTotales;

        // Actualizar estilo del contador según disponibilidad
        if (disponibles <= 50) {
            contadorCaracteres.style.color = '#dc3545'; // rojo para pocos caracteres
        } else if (disponibles <= 100) {
            contadorCaracteres.style.color = '#ffc107'; // amarillo para advertencia
        } else {
            contadorCaracteres.style.color = '#198754'; // verde para normal
        }

        return disponibles;
    }

    // Evento para abrir modal principal
    document.querySelector('[data-bs-target="#modalLaborPrincipal"]').addEventListener('click', function (e) {
        const caracteresDisponibles = actualizarCaracteresTotales();
        if (caracteresDisponibles <= 0) {
            e.preventDefault();
            mostrarNotificacionSuave('Has alcanzado el límite de caracteres disponibles');
            return;
        }
        inputLabor.value = '';
        contadorCaracteres.textContent = caracteresDisponibles;
        btnRegistrarLabor.disabled = true;
    });

    // Contador de caracteres en tiempo real
    inputLabor.addEventListener('input', function () {
        const caracteresDisponibles = actualizarCaracteresTotales();
        const longitudActual = this.value.length;
        const caracteresRestantes = Math.max(0, caracteresDisponibles - longitudActual);

        // Actualizar contador
        contadorCaracteres.textContent = caracteresRestantes;

        // Si está excediendo el límite
        if (longitudActual > caracteresDisponibles) {
            // Truncar el texto
            this.value = this.value.substring(0, caracteresDisponibles);
            // Mostrar notificación suave
            mostrarNotificacionSuave('Has alcanzado el límite de caracteres');
        }

        // Actualizar estado del botón
        btnRegistrarLabor.disabled = this.value.trim().length === 0 || caracteresRestantes === 0;
    });

    // Registrar Labor Principal
    btnRegistrarLabor.addEventListener('click', function () {
        const laborPrincipal = inputLabor.value.trim();
        if (!laborPrincipal) return;

        const caracteresDisponibles = actualizarCaracteresTotales();
        if (laborPrincipal.length > caracteresDisponibles) {
            mostrarNotificacionSuave('La labor excede el límite de caracteres disponibles');
            return;
        }

        const id = Date.now().toString();
        laboresPrincipales.set(id, {
            texto: laborPrincipal,
            laboresEspecificas: []
        });

        const fila = tablaLabores.insertRow();
        fila.dataset.laborId = id;
        fila.innerHTML = `
                <td>
                    <button class="btn btn-link btn-sm" onclick="toggleLabores(this)">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </td>
                <td>
                    <div class="labor-principal">${laborPrincipal}</div>
                    <div class="labores-especificas" style="display: none;">
                        <ul class="list-group list-group-flush mt-2"></ul>
                    </div>
                </td>
                <td>
                    <button type="button" class="btn btn-primary btn-sm" onclick="abrirModalLaboresEspecificas('${id}', '${laborPrincipal}')">
                        <i class="fas fa-plus"></i>
                    </button>
                    <button type="button" class="btn btn-danger btn-sm" onclick="eliminarLabor('${id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </td>
            `;

        modalLaborPrincipal.hide();
        mostrarNotificacion('Labor agregada correctamente');
    });

    // Manejo de labores específicas
    btnAgregarLaborEspecifica.addEventListener('click', function () {
        const laborEspecifica = inputLaborEspecifica.value.trim();
        if (laborEspecifica) {
            laboresEspecificasTemp.push(laborEspecifica);
            actualizarListaLaboresEspecificas();
            inputLaborEspecifica.value = '';
        }
    });

    function actualizarListaLaboresEspecificas() {
        listaLaboresEspecificas.innerHTML = '';
        // Habilitar/deshabilitar botón según si hay labores
        btnGuardarLaboresEspecificas.disabled = laboresEspecificasTemp.length === 0;

        laboresEspecificasTemp.forEach((labor, index) => {
            const li = document.createElement('li');
            li.className = 'list-group-item d-flex justify-content-between align-items-center';
            li.innerHTML = `
                    ${labor}
                    <button type="button" class="btn btn-danger btn-sm" onclick="eliminarLaborEspecificaTemp(${index})">
                        <i class="fas fa-times"></i>
                    </button>
                `;
            listaLaboresEspecificas.appendChild(li);
        });
    }

    // Guardar labores específicas
    document.getElementById('btnGuardarLaboresEspecificas').addEventListener('click', function () {
        if (laborSeleccionadaId) {
            const fila = document.querySelector(`tr[data-labor-id="${laborSeleccionadaId}"]`);
            const ulLaboresEspecificas = fila.querySelector('.labores-especificas ul');
            ulLaboresEspecificas.innerHTML = '';

            laboresEspecificasTemp.forEach(labor => {
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.textContent = labor;
                ulLaboresEspecificas.appendChild(li);
            });

            // Actualizar el Map de labores principales
            const laborPrincipal = laboresPrincipales.get(laborSeleccionadaId);
            if (laborPrincipal) {
                laborPrincipal.laboresEspecificas = [...laboresEspecificasTemp];
            }
        }
        modalLaboresEspecificas.hide();
        laboresEspecificasTemp = [];
        mostrarNotificacion('Labores específicas guardadas correctamente');
    });

    // Eventos del modal de labores específicas
    modalLaboresEspecificas._element.addEventListener('show.bs.modal', function () {
        laboresEspecificasTemp = [];
        listaLaboresEspecificas.innerHTML = '';
        inputLaborEspecifica.value = '';
        btnGuardarLaboresEspecificas.disabled = true;

        if (laborSeleccionadaId) {
            const laborPrincipal = laboresPrincipales.get(laborSeleccionadaId);
            if (laborPrincipal && laborPrincipal.laboresEspecificas) {
                laboresEspecificasTemp = [...laborPrincipal.laboresEspecificas];
                actualizarListaLaboresEspecificas();
            }
        }
    });

    modalLaboresEspecificas._element.addEventListener('hidden.bs.modal', function () {
        laborSeleccionadaId = null;
        laboresEspecificasTemp = [];
    });

    // Funciones globales
    window.toggleLabores = function (btn) {
        const fila = btn.closest('tr');
        const laboresEspecificas = fila.querySelector('.labores-especificas');
        const icono = btn.querySelector('i');

        if (laboresEspecificas.style.display === 'none') {
            laboresEspecificas.style.display = 'block';
            icono.classList.replace('fa-chevron-right', 'fa-chevron-down');
        } else {
            laboresEspecificas.style.display = 'none';
            icono.classList.replace('fa-chevron-down', 'fa-chevron-right');
        }
    };

    window.abrirModalLaboresEspecificas = function (laborId, laborPrincipal) {
        document.getElementById('laborPrincipalTitle').textContent = laborPrincipal;
        laborSeleccionadaId = laborId;
        modalLaboresEspecificas.show();
    };

    window.eliminarLabor = function (laborId) {
        Swal.fire({
            title: '¿Eliminar esta labor?',
            text: "Esta acción no se puede deshacer",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonText: 'Sí, eliminar',
            cancelButtonText: 'Cancelar'
        }).then((result) => {
            if (result.isConfirmed) {
                const fila = document.querySelector(`tr[data-labor-id="${laborId}"]`);
                if (fila) {
                    laboresPrincipales.delete(laborId);
                    fila.remove();
                    const caracteresDisponibles = actualizarCaracteresTotales();
                    contadorCaracteres.textContent = caracteresDisponibles;
                    mostrarNotificacion('Labor eliminada correctamente');
                }
            }
        });
    };

    window.eliminarLaborEspecificaTemp = function (index) {
        laboresEspecificasTemp.splice(index, 1);
        actualizarListaLaboresEspecificas();
    };

    function mostrarNotificacion(mensaje) {
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        });

        Toast.fire({
            icon: 'success',
            title: mensaje
        });
    }

    function mostrarNotificacionSuave(mensaje) {
        const Toast = Swal.mixin({
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 2000,
            timerProgressBar: true,
            didOpen: (toast) => {
                toast.addEventListener('mouseenter', Swal.stopTimer)
                toast.addEventListener('mouseleave', Swal.resumeTimer)
            }
        });

        Toast.fire({
            icon: 'info',
            title: mensaje
        });
    }
});

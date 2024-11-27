document.addEventListener('DOMContentLoaded', function () {
    const tablaInformes = document.getElementById('tabla-informes').getElementsByTagName('tbody')[0];
    const modalInforme = new bootstrap.Modal(document.getElementById('modalInforme'));
    const formVerModificar = document.getElementById('form-ver-modificar');
    const btnGuardarCambios = document.getElementById('btnGuardarCambios');

    // Cargar informes cuando se muestre la pestaña
    document.getElementById('tab-listado').addEventListener('shown.bs.tab', cargarInformes);

    function cargarInformes() {
        fetch(URLS.listarInformes)
            .then(response => response.json())
            .then(informes => {
                tablaInformes.innerHTML = '';
                informes.forEach(informe => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${informe.idInforme}</td>
                        <td>${informe.estudiante}</td>
                        <td>${informe.fecha || ''}</td>
                        <td>${informe.estado === 'A' ? 'Activo' : 'Inactivo'}</td>
                        <td>
                            <button class="btn btn-info btn-sm" style="border-radius: 5px; margin-right: 5px;" onclick="verInforme(${informe.idInforme})">
                                <i class="fas fa-eye"></i>
                            </button>
                            <button class="btn btn-warning btn-sm" style="border-radius: 5px;" onclick="modificarInforme(${informe.idInforme})">
                                <i class="fas fa-edit"></i>
                            </button>
                        </td>
                    `;
                    tablaInformes.appendChild(tr);
                });
            })
            .catch(error => {
                console.error('Error:', error);
                Swal.fire({
                    icon: 'error',
                    title: 'Error',
                    text: 'Error al cargar los informes'
                });
            });
    }

    window.verInforme = function (idInforme) {
        cargarDatosInforme(idInforme, false);
    };

    window.modificarInforme = function (idInforme) {
        cargarDatosInforme(idInforme, true);
    };

    async function cargarDatosInforme(idInforme, editable) {
        try {
            const response = await fetch(`${URLS.obtenerInforme}/${idInforme}`);
            if (!response.ok) {
                throw new Error('Error al obtener los datos del informe');
            }
            const informe = await response.json();

            // Cargar datos básicos en el modal
            document.getElementById('modal_id_informe').value = informe.idInforme;
            document.getElementById('modal_estudiante').value = informe.estudiante;
            document.getElementById('modal_fecha').value = informe.fecha;
            document.getElementById('modal_aceptacion').value = informe.aceptacion;

            // Cargar firmas si existen
            const firma1Preview = document.getElementById('modal_firma1_preview');
            const firma2Preview = document.getElementById('modal_firma2_preview');

            if (informe.firma1) {
                firma1Preview.src = `/${informe.firma1}`;
                firma1Preview.style.display = 'block';
            } else {
                firma1Preview.style.display = 'none';
            }

            if (informe.firma2) {
                firma2Preview.src = `/${informe.firma2}`;
                firma2Preview.style.display = 'block';
            } else {
                firma2Preview.style.display = 'none';
            }

            // Cargar labores con mejor manejo de errores
            const laboresContainer = document.getElementById('modal_labores_principales');
            laboresContainer.innerHTML = '';

            let laboresPrincipales = [];
            let laboresEspecificas = [];

            try {
                // Verificar si labor es un string y convertirlo a array si es necesario
                if (informe.labor) {
                    if (typeof informe.labor === 'string') {
                        try {
                            laboresPrincipales = JSON.parse(informe.labor);
                        } catch {
                            laboresPrincipales = [informe.labor];
                        }
                    } else {
                        laboresPrincipales = informe.labor;
                    }
                }

                // Verificar si labores es un string y convertirlo a array si es necesario
                if (informe.labores) {
                    if (typeof informe.labores === 'string') {
                        try {
                            laboresEspecificas = JSON.parse(informe.labores);
                        } catch {
                            laboresEspecificas = [[informe.labores]];
                        }
                    } else {
                        laboresEspecificas = informe.labores;
                    }
                }

                // Asegurar que laboresPrincipales sea un array
                if (!Array.isArray(laboresPrincipales)) {
                    laboresPrincipales = [laboresPrincipales];
                }

                // Asegurar que laboresEspecificas sea un array de arrays
                if (!Array.isArray(laboresEspecificas)) {
                    laboresEspecificas = [[laboresEspecificas]];
                }

                // Mostrar las labores
                /* laboresPrincipales.forEach((labor, index) => {
                    const laborDiv = document.createElement('div');
                    laborDiv.className = 'mb-3 border p-3 rounded';
                    laborDiv.innerHTML = `
                        <div class="labor-principal">
                            <h6 class="mb-3">Labor Principal ${index + 1}:</h6>
                            <input type="text" 
                                   class="form-control mb-2" 
                                   name="labor_principal_${index}"
                                   value="${labor}" 
                                   ${!editable ? 'readonly' : ''}>
                        </div>
                        <div class="labores-especificas mt-3">
                            <h6 class="mb-2">Labores Específicas:</h6>
                            <div class="list-group">
                                ${(laboresEspecificas[index] || []).map((laborEsp, laborIndex) => `
                                    <div class="list-group-item">
                                        <input type="text" 
                                               class="form-control"
                                               name="labor_especifica_${index}_${laborIndex}"
                                               value="${laborEsp}"
                                               ${!editable ? 'readonly' : ''}>
                                    </div>
                                `).join('')}
                            </div>
                            ${editable ? `
                                <button type="button" class="btn btn-sm btn-success mt-2" 
                                        onclick="agregarLaborEspecifica(${index})">
                                    <i class="fas fa-plus"></i> Agregar Labor Específica
                                </button>
                            ` : ''}
                        </div>
                    `;
                    laboresContainer.appendChild(laborDiv);
                }); */

                laboresPrincipales.forEach((labor, index) => {
                    const laborDiv = document.createElement('div');
                    laborDiv.className = 'mb-3 border p-3 rounded';
                    laborDiv.innerHTML = `
                        <div class="labor-principal">
                            <h6 class="mb-3">Labor Principal ${index + 1}:</h6>
                            <div class="form-group">
                                <input type="text" 
                                       class="form-control mb-2" 
                                       name="labor_principal_${index}"
                                       value="${labor}" 
                                       maxlength="255"
                                       onkeyup="actualizarContadorLabor(this)"
                                       ${!editable ? 'readonly' : ''}>
                                <small class="text-muted caracteres-contador">
                                    Caracteres restantes: <span>${255 - labor.length}</span>
                                </small>
                            </div>
                        </div>
                        <div class="labores-especificas mt-3">
                            <h6 class="mb-2">Labores Específicas:</h6>
                            <div class="list-group">
                                ${(laboresEspecificas[index] || []).map((laborEsp, laborIndex) => `
                                    <div class="list-group-item">
                                        <input type="text" 
                                               class="form-control"
                                               name="labor_especifica_${index}_${laborIndex}"
                                               value="${laborEsp}"
                                               ${!editable ? 'readonly' : ''}>
                                    </div>
                                `).join('')}
                            </div>
                            ${editable ? `
                                <button type="button" class="btn btn-sm btn-success mt-2" 
                                        onclick="agregarLaborEspecifica(${index})">
                                    <i class="fas fa-plus"></i> Agregar Labor Específica
                                </button>
                            ` : ''}
                        </div>
                    `;
                    laboresContainer.appendChild(laborDiv);
                });

                // Si no hay labores, mostrar mensaje informativo
                if (laboresPrincipales.length === 0) {
                    laboresContainer.innerHTML = `
                        <div class="alert alert-info">
                            No hay labores registradas
                        </div>
                    `;
                }

            } catch (e) {
                console.error('Error al procesar labores:', e);
                console.log('Labor original:', informe.labor);
                console.log('Labores original:', informe.labores);

                laboresContainer.innerHTML = `
                    <div class="alert alert-info">
                        <h6 class="mb-2">Labor Principal:</h6>
                        <p>${informe.labor || 'No especificada'}</p>
                        <h6 class="mt-3 mb-2">Labores Específicas:</h6>
                        <p>${informe.labores || 'No especificadas'}</p>
                    </div>
                `;
            }

            // Configurar modo (ver/editar)
            const inputs = formVerModificar.querySelectorAll('input:not([readonly])');
            inputs.forEach(input => input.disabled = !editable);

            // Mostrar/ocultar botón de guardar
            btnGuardarCambios.style.display = editable ? 'block' : 'none';

            // Actualizar título del modal
            document.getElementById('modalInformeLabel').textContent =
                editable ? 'Modificar Informe' : 'Ver Informe';

            // Mostrar el modal
            modalInforme.show();

        } catch (error) {
            console.error('Error general:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error al cargar los datos del informe'
            });
        }

        document.querySelectorAll('[name^="labor_principal_"]').forEach(input => {
            actualizarContadorLabor(input);
        });
        
        // Mostrar el modal
        modalInforme.show();
    }


    // Agregar esta función global para el contador de caracteres
window.actualizarContadorLabor = function(input) {
    const maxLength = input.maxLength;
    const currentLength = input.value.length;
    const contadorSpan = input.parentElement.querySelector('.caracteres-contador span');
    const caracteresRestantes = maxLength - currentLength;
    
    contadorSpan.textContent = caracteresRestantes;
    
    // Cambiar color según cantidad de caracteres restantes
    if (caracteresRestantes < 50) {
        contadorSpan.style.color = 'orange';
    } else if (caracteresRestantes < 20) {
        contadorSpan.style.color = 'red';
    } else {
        contadorSpan.style.color = '';
    }
};

// Actualizar la función de agregar labor específica
window.agregarLaborEspecifica = function(laborPrincipalIndex) {
    const laborPrincipalDiv = document.querySelector(`[name="labor_principal_${laborPrincipalIndex}"]`).closest('.mb-3');
    const laboresEspecificasDiv = laborPrincipalDiv.querySelector('.list-group');
    const nuevaLaborIndex = laboresEspecificasDiv.children.length;

    const nuevaLaborDiv = document.createElement('div');
    nuevaLaborDiv.className = 'list-group-item';
    nuevaLaborDiv.innerHTML = `
        <div class="d-flex">
            <input type="text" 
                   class="form-control"
                   name="labor_especifica_${laborPrincipalIndex}_${nuevaLaborIndex}"
                   placeholder="Nueva labor específica">
            <button type="button" class="btn btn-danger ms-2" 
                    onclick="this.closest('.list-group-item').remove()">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    laboresEspecificasDiv.appendChild(nuevaLaborDiv);
};

    window.agregarLaborEspecifica = function (laborPrincipalIndex) {
        const laborPrincipalDiv = document.querySelector(`[name="labor_principal_${laborPrincipalIndex}"]`).closest('.mb-3');
        const laboresEspecificasDiv = laborPrincipalDiv.querySelector('.list-group');
        const nuevaLaborIndex = laboresEspecificasDiv.children.length;

        const nuevaLaborDiv = document.createElement('div');
        nuevaLaborDiv.className = 'list-group-item';
        nuevaLaborDiv.innerHTML = `
            <div class="d-flex">
                <input type="text" 
                       class="form-control"
                       name="labor_especifica_${laborPrincipalIndex}_${nuevaLaborIndex}"
                       placeholder="Nueva labor específica">
                <button type="button" class="btn btn-danger ms-2" 
                        onclick="this.closest('.list-group-item').remove()">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        laboresEspecificasDiv.appendChild(nuevaLaborDiv);
    };

    btnGuardarCambios.addEventListener('click', async function () {
        try {
            const formData = new FormData();
            formData.append('idInforme', document.getElementById('modal_id_informe').value);
            formData.append('fecha', document.getElementById('modal_fecha').value);
            formData.append('aceptacion', document.getElementById('modal_aceptacion').value);

            // Recolectar labores principales y específicas
            const laboresPrincipales = [];
            const laboresEspecificas = [];

            // Obtener todas las labores principales
            document.querySelectorAll('[name^="labor_principal_"]').forEach((input, index) => {
                laboresPrincipales.push(input.value);

                // Obtener las labores específicas correspondientes
                const especificas = [];
                document.querySelectorAll(`[name^="labor_especifica_${index}_"]`).forEach(inputEsp => {
                    if (inputEsp.value.trim()) {
                        especificas.push(inputEsp.value.trim());
                    }
                });
                laboresEspecificas.push(especificas);
            });

            formData.append('labor', JSON.stringify(laboresPrincipales));
            formData.append('labores', JSON.stringify(laboresEspecificas));

            const firma1 = document.getElementById('modal_firma1').files[0];
            const firma2 = document.getElementById('modal_firma2').files[0];

            if (firma1) formData.append('firma1', firma1);
            if (firma2) formData.append('firma2', firma2);

            const response = await fetch(URLS.actualizarInforme, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }

            const result = await response.json();

            if (result.error) {
                throw new Error(result.error);
            }

            Swal.fire({
                icon: 'success',
                title: 'Éxito',
                text: 'Informe actualizado correctamente'
            }).then(() => {
                modalInforme.hide();
                cargarInformes();
            });

        } catch (error) {
            console.error('Error:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: error.message || 'Error al actualizar el informe'
            });
        }
    });

    // Limpiar el formulario cuando se cierre el modal
    document.getElementById('modalInforme').addEventListener('hidden.bs.modal', function () {
        formVerModificar.reset();
        document.getElementById('modal_firma1_preview').style.display = 'none';
        document.getElementById('modal_firma2_preview').style.display = 'none';
        document.getElementById('modal_labores_principales').innerHTML = '';
    });
});
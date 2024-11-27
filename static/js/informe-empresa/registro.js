document.addEventListener('DOMContentLoaded', function () {
    const formInforme = document.getElementById('form-informe-empresa');

    formInforme.addEventListener('submit', async function (e) {
        e.preventDefault();

        try {
            // Validaciones...
            if (!document.getElementById('estudiante_seleccionado').value) {
                mostrarError('Debe seleccionar un estudiante');
                return;
            }

            if (!document.getElementById('institucion_seleccionada').value) {
                mostrarError('Debe seleccionar una institución');
                return;
            }

            // Crear FormData
            const formData = new FormData();

            // Agregar campos del formulario
            formData.append('aceptacion', 'ACEPTADO'); // O el valor que corresponda
            
            // Obtener y formatear las labores principales
            const laboresPrincipalesArray = [];
            window.laboresPrincipales.forEach(labor => {
                laboresPrincipalesArray.push(labor.texto);
            });
            formData.append('labor', JSON.stringify(laboresPrincipalesArray));

            // Obtener y formatear las labores específicas
            const laboresEspecificasArray = [];
            window.laboresPrincipales.forEach(labor => {
                laboresEspecificasArray.push(...labor.laboresEspecificas);
            });
            formData.append('labores', JSON.stringify(laboresEspecificasArray));

            // Agregar archivos de firma
            const firma1 = document.getElementById('firma_responsable').files[0];
            const firma2 = document.getElementById('firma_estudiante').files[0];
            
            if (!firma1 || !firma2) {
                mostrarError('Debe subir ambas firmas');
                return;
            }

            formData.append('firma1', firma1);
            formData.append('firma2', firma2);

            // Enviar formulario usando la URL correcta
            const response = await fetch(URLS.guardarInforme, {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error);
            }

            // Mostrar mensaje de éxito
            Swal.fire({
                icon: 'success',
                title: 'Éxito',
                text: data.message || 'Informe guardado correctamente',
                showConfirmButton: true
            }).then((result) => {
                if (result.isConfirmed) {
                    window.location.reload();
                }
            });

        } catch (error) {
            mostrarError(error.message || 'Error al guardar el informe');
        }
    });

    function mostrarError(mensaje) {
        Swal.fire({
            icon: 'error',
            title: 'Error',
            text: mensaje,
            confirmButtonText: 'Aceptar'
        });
    }
});
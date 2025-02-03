function togglePassword(inputId) {
    let input = document.getElementById(inputId);
    if (!input) {
        input = document.querySelector(`input[name="${inputId}"]`);
    }
    if (!input) return;
    const icon = event.currentTarget.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

const sweetAlertOptions = {
    confirmButtonColor: '#4CAF50',
    cancelButtonColor: '#F44336',
    confirmButtonText: 'Aceptar',
    cancelButtonText: 'Cancelar',
    customClass: {
        popup: 'swal-custom-popup',
        header: 'swal-custom-header',
        title: 'swal-custom-title',
        closeButton: 'swal-custom-close',
        icon: 'swal-custom-icon',
        content: 'swal-custom-content',
        input: 'swal-custom-input',
        actions: 'swal-custom-actions',
        confirmButton: 'swal-custom-confirm',
        cancelButton: 'swal-custom-cancel',
        footer: 'swal-custom-footer'
    },
    buttonsStyling: true,
    showClass: {
        popup: 'animate__animated animate__fadeIn'
    },
    hideClass: {
        popup: 'animate__animated animate__fadeOut'
    }
};

$(document).ready(function () {
    $('[name="titular"], input[name*="titular"]').on('input', function () {
        let value = $(this).val();
        value = value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
        $(this).val(value);
    });
    $('[name="numero_tarjeta"], input[name*="numero_tarjeta"]').on('input', function () {
        let value = $(this).val().replace(/\D/g, '');
        if (value.length > 0) {
            value = value.match(/.{1,4}/g).join('-');
        }
        $(this).val(value.substring(0, 19));
    });
    $('[name="fecha_vencimiento"], input[name*="fecha_vencimiento"]').on('input', function (e) {
        let value = $(this).val().replace(/\D/g, '');
        let previousValue = $(this).data('previous') || '';
        if (value.length < previousValue.replace(/\D/g, '').length) {
            $(this).data('previous', value);
            $(this).val(value);
            return;
        }
        if (value.length > 0) {
            if (value.length > 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            let month = parseInt(value.substring(0, 2));
            let year = parseInt(value.substring(3, 5) || '0');
            if (month > 12) value = '12' + value.substring(2);
            if (month === 0) value = '01' + value.substring(2);
            const currentYear = new Date().getFullYear() % 100;
            const minYear = (currentYear - 4) % 100;
            const maxYear = (currentYear + 5) % 100;
            if (value.length >= 5) {
                if (year < minYear) value = value.substring(0, 3) + minYear;
                if (year > maxYear) value = value.substring(0, 3) + maxYear;
            }
        }
        $(this).data('previous', value);
        $(this).val(value);
    });
    $('[name="codigo_seguridad"], input[name*="codigo_seguridad"]').on('input', function () {
        $(this).val($(this).val().replace(/\D/g, ''));
    });
    $('form').on('submit', function (e) {
        const isEditPage = window.location.href.includes('editar');
        const isPagoPage = window.location.href.includes('pago');
        if (!isPagoPage) return true;
        e.preventDefault();
        const campos = {
            'opcion_pago': 'Seleccione un método de pago',
            'titular': 'Ingrese el nombre del titular',
            'numero_tarjeta': 'Ingrese el número de tarjeta',
            'fecha_vencimiento': 'Ingrese la fecha de vencimiento',
            'codigo_seguridad': 'Ingrese el código de seguridad',
            'saldo': 'Ingrese el saldo inicial'
        };
        for (let [id, mensaje] of Object.entries(campos)) {
            const valor = $(`#${id}`).val()?.trim();
            if (!valor) {
                Swal.fire({
                    ...sweetAlertOptions,
                    title: 'Campo Requerido',
                    text: mensaje,
                    icon: 'warning'
                });
                $(`#${id}`).focus();
                return false;
            }
        }
        const titular = $('#titular').val().trim();
        if (titular.length < 3) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Titular',
                text: 'El nombre del titular debe tener al menos 3 caracteres',
                icon: 'error'
            });
            $('#titular').focus();
            return false;
        }
        const numeroTarjeta = $('#numero_tarjeta').val().replace(/-/g, '');
        if (!/^\d{16}$/.test(numeroTarjeta)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Número de Tarjeta',
                text: 'El número de tarjeta debe tener 16 dígitos',
                icon: 'error'
            });
            $('#numero_tarjeta').focus();
            return false;
        }
        const fechaVencimiento = $('#fecha_vencimiento').val();
        if (!/^\d{2}\/\d{2}$/.test(fechaVencimiento)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Fecha',
                text: 'La fecha debe tener formato MM/YY',
                icon: 'error'
            });
            $('#fecha_vencimiento').focus();
            return false;
        }
        const [mes, anio] = fechaVencimiento.split('/').map(Number);
        const fechaActual = new Date();
        const anioActual = fechaActual.getFullYear() % 100;
        const mesActual = fechaActual.getMonth() + 1;
        if (anio < anioActual || (anio === anioActual && mes < mesActual)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Fecha',
                text: 'La tarjeta está vencida',
                icon: 'error'
            });
            $('#fecha_vencimiento').focus();
            return false;
        }
        const cvv = $('#codigo_seguridad').val();
        if (!/^\d{3,4}$/.test(cvv)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en CVV',
                text: 'El código de seguridad debe tener 3 o 4 dígitos',
                icon: 'error'
            });
            $('#codigo_seguridad').focus();
            return false;
        }
        const saldo = parseFloat($('#saldo').val());
        if (isNaN(saldo) || saldo < 0 || saldo > 10000) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Saldo',
                text: 'El saldo debe ser un número entre 0.00 y 10000.00',
                icon: 'error'
            });
            $('#saldo').focus();
            return false;
        }
        if (isEditPage) {
            Swal.fire({
                ...sweetAlertOptions,
                title: '¿Confirmar cambios?',
                text: '¿Está seguro que desea guardar los cambios realizados?',
                icon: 'question',
                showCancelButton: true
            }).then((result) => {
                if (result.isConfirmed) {
                    this.submit();
                }
            });
        } else {
            this.submit();
        }
    });
});

function formatearTelefono(valor) {
    valor = valor.replace(/\D/g, '');
    if (/^0[2-7]/.test(valor)) {
        if (valor.length > 2) {
            valor = `(${valor.substring(0, 2)}) ${valor.substring(2)}`;
        }
        if (valor.length > 7) {
            valor = valor.substring(0, 7) + ' ' + valor.substring(7);
        }
        return valor.substring(0, 13);
    }
    else if (/^09/.test(valor)) {
        if (valor.length > 3) {
            valor = valor.substring(0, 3) + ' ' + valor.substring(3);
        }
        if (valor.length > 7) {
            valor = valor.substring(0, 7) + ' ' + valor.substring(7);
        }
        return valor.substring(0, 12);
    }
    return valor.substring(0, 10);
}

$(document).ready(function () {
    $('#ruc').on('input', function () {
        let valor = $(this).val().replace(/\D/g, '');
        $(this).val(valor.substring(0, 13));
    });
    $('#telefono').on('input', function () {
        let valor = $(this).val();
        $(this).val(formatearTelefono(valor));
    });
    $('form').on('submit', function (e) {
        const isEditPage = window.location.href.includes('editar');
        const isCooperativaPage = window.location.href.includes('cooperativa');
        if (!isCooperativaPage) {
            return true;
        }
        e.preventDefault();
        const campos = {
            'nombre_cooperativa': 'Ingrese el nombre de la cooperativa',
            'ruc': 'Ingrese el RUC',
            'direccion': 'Ingrese la dirección',
            'telefono': 'Ingrese el teléfono',
            'correo_empresarial': 'Ingrese el correo empresarial'
        };
        for (let [id, mensaje] of Object.entries(campos)) {
            const valor = $(`#${id}`).val()?.trim();
            if (!valor) {
                Swal.fire({
                    ...sweetAlertOptions,
                    title: 'Campo Requerido',
                    text: mensaje,
                    icon: 'warning'
                });
                $(`#${id}`).focus();
                return false;
            }
        }
        const ruc = $('#ruc').val();
        const telefono = $('#telefono').val().replace(/[\s()-]/g, '');
        if (!/^[0-9]{13}$/.test(ruc)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en RUC',
                text: 'El RUC debe tener 13 dígitos numéricos',
                icon: 'error'
            });
            $('#ruc').focus();
            return false;
        }
        if (!/^0[2-7][0-9]{7}$/.test(telefono) && !/^09[0-9]{8}$/.test(telefono)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Teléfono',
                text: 'Ingrese un número de teléfono fijo o celular válido',
                icon: 'error'
            });
            $('#telefono').focus();
            return false;
        }
        if (isEditPage) {
            Swal.fire({
                ...sweetAlertOptions,
                title: '¿Confirmar cambios?',
                text: '¿Está seguro que desea guardar los cambios realizados?',
                icon: 'question',
                showCancelButton: true
            }).then((result) => {
                if (result.isConfirmed) {
                    this.submit();
                }
            });
        } else {
            this.submit();
        }
    });
});

$(document).ready(function () {
    $('#numero_bus').on('input', function () {
        let valor = $(this).val();
        if (valor === '0') {
            $(this).val('1');
        }
    });
    $('#marca').on('input', function () {
        let valor = $(this).val();
        valor = valor.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
        $(this).val(valor);
    });
    $('#modelo').on('input', function () {
        let valor = $(this).val().replace(/\D/g, '');
        valor = valor.substring(0, 4);
        const añoActual = new Date().getFullYear();
        if (valor.length === 4) {
            const año = parseInt(valor);
            if (año < 1980) valor = '1980';
            if (año > añoActual) valor = añoActual.toString();
        }
        $(this).val(valor);
    });
    $('#placa').on('input', function () {
        let valor = $(this).val().toUpperCase();
        valor = valor.replace(/[^A-Z0-9-]/g, '');
        if (valor.length > 0) {
            valor = valor.replace(/-/g, '');
            let letras = valor.match(/[A-Z]+/) ? valor.match(/[A-Z]+/)[0] : '';
            let numeros = valor.match(/[0-9]+/) ? valor.match(/[0-9]+/)[0] : '';
            letras = letras.substring(0, 3);
            numeros = numeros.substring(0, 4);
            if (letras && numeros) {
                valor = `${letras}-${numeros}`;
            } else {
                valor = letras + numeros;
            }
        }
        $(this).val(valor);
    });
    $('#velocidad, #capacidad_pasajeros').on('input', function () {
        let valor = $(this).val();
        const id = $(this).attr('id');
        const maxValue = id === 'velocidad' ? 120 : 80;
        if (valor === '0') {
            $(this).val('');
            return;
        }
        if (parseInt(valor) > maxValue) {
            $(this).val(maxValue);
        }
    });
    $('form').on('submit', function (e) {
        const isEditPage = window.location.href.includes('editar');
        const isBusPage = window.location.href.includes('bus');
        if (!isBusPage) return true;
        e.preventDefault();
        const campos = {
            'numero_bus': 'Ingrese el número de bus',
            'placa': 'Ingrese la placa del bus',
            'marca': 'Ingrese la marca del bus',
            'modelo': 'Ingrese el modelo del bus',
            'capacidad_pasajeros': 'Ingrese la capacidad de pasajeros',
            'velocidad': 'Ingrese la velocidad del bus'
        };
        for (let [id, mensaje] of Object.entries(campos)) {
            const valor = $(`#${id}`).val()?.trim();
            if (!valor) {
                Swal.fire({
                    ...sweetAlertOptions,
                    title: 'Campo Requerido',
                    text: mensaje,
                    icon: 'warning'
                });
                $(`#${id}`).focus();
                return false;
            }
        }
        const placa = $('#placa').val();
        if (!/^[A-Z]{2,3}-\d{4}$/.test(placa)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Placa',
                text: 'El formato de placa debe ser XX-1234 o XXX-1234',
                icon: 'error'
            });
            $('#placa').focus();
            return false;
        }
        const marca = $('#marca').val();
        if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/.test(marca)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Marca',
                text: 'La marca solo debe contener letras',
                icon: 'error'
            });
            $('#marca').focus();
            return false;
        }
        const modelo = $('#modelo').val();
        const añoActual = new Date().getFullYear();
        if (!/^\d{4}$/.test(modelo) || parseInt(modelo) < 1980 || parseInt(modelo) > añoActual) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Modelo',
                text: `El modelo debe ser un año entre 1980 y ${añoActual}`,
                icon: 'error'
            });
            $('#modelo').focus();
            return false;
        }
        const velocidad = parseInt($('#velocidad').val());
        const capacidad = parseInt($('#capacidad_pasajeros').val());
        if (velocidad > 120) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Velocidad',
                text: 'La velocidad máxima permitida es 120 km/h',
                icon: 'error'
            });
            $('#velocidad').focus();
            return false;
        }
        if (capacidad > 80) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Capacidad',
                text: 'La capacidad máxima es de 80 pasajeros',
                icon: 'error'
            });
            $('#capacidad_pasajeros').focus();
            return false;
        }
        if (isEditPage) {
            Swal.fire({
                ...sweetAlertOptions,
                title: '¿Confirmar cambios?',
                text: '¿Está seguro que desea guardar los cambios realizados?',
                icon: 'question',
                showCancelButton: true
            }).then((result) => {
                if (result.isConfirmed) {
                    this.submit();
                }
            });
        } else {
            this.submit();
        }
    });
});

$(document).ready(function () {
    $('form').on('submit', function (e) {
        const isEditPage = window.location.href.includes('editar');
        const isCuentaPage = window.location.href.includes('cuenta');
        if (!isCuentaPage) return true;
        e.preventDefault();
        const campos = {
            'correo': 'Ingrese el correo electrónico',
            'contrasenia': 'Ingrese la contraseña',
            'tipo_cuenta': 'Seleccione el tipo de cuenta',
            'estado_cuenta': 'Seleccione el estado de la cuenta'
        };
        for (let [id, mensaje] of Object.entries(campos)) {
            const valor = $(`#${id}`).val()?.trim();
            if (!valor) {
                Swal.fire({
                    ...sweetAlertOptions,
                    title: 'Campo Requerido',
                    text: mensaje,
                    icon: 'warning'
                });
                $(`#${id}`).focus();
                return false;
            }
        }
        const correo = $('#correo').val();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(correo)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Correo',
                text: 'Ingrese un correo electrónico válido',
                icon: 'error'
            });
            $('#correo').focus();
            return false;
        }
        const contrasenia = $('#contrasenia').val();
        if (contrasenia.length < 8) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Contraseña',
                text: 'La contraseña debe tener al menos 8 caracteres, mayúsculas, minúsculas, números y caracteres especiales',
                icon: 'error'
            });
            $('#contrasenia').focus();
            return false;
        }
        const tieneMinuscula = /[a-z]/.test(contrasenia);
        const tieneMayuscula = /[A-Z]/.test(contrasenia);
        const tieneNumero = /[0-9]/.test(contrasenia);
        const tieneEspecial = /[!@#$%^&*(),.?":{}|<>]/.test(contrasenia);
        if (!(tieneMinuscula && tieneMayuscula && tieneNumero && tieneEspecial)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Contraseña',
                text: 'La contraseña debe contener mayúsculas, minúsculas, números y caracteres especiales',
                icon: 'error'
            });
            $('#contrasenia').focus();
            return false;
        }
        const tipoCuenta = $('#tipo_cuenta').val();
        const estadoCuenta = $('#estado_cuenta').val();
        if (!tipoCuenta || tipoCuenta === "") {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Tipo de Cuenta',
                text: 'Debe seleccionar un tipo de cuenta válido',
                icon: 'error'
            });
            $('#tipo_cuenta').focus();
            return false;
        }
        if (!estadoCuenta || estadoCuenta === "") {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Estado',
                text: 'Debe seleccionar un estado válido',
                icon: 'error'
            });
            $('#estado_cuenta').focus();
            return false;
        }
        if (isEditPage) {
            Swal.fire({
                ...sweetAlertOptions,
                title: '¿Confirmar cambios?',
                text: '¿Está seguro que desea guardar los cambios realizados?',
                icon: 'question',
                showCancelButton: true
            }).then((result) => {
                if (result.isConfirmed) {
                    this.submit();
                }
            });
        } else {
            this.submit();
        }
    });
});


$(document).ready(function () {
    $('#porcentaje').on('input', function () {
        let valor = $(this).val();
        if (valor === '') {
            return;
        }
        valor = parseInt(valor);
        if (!isNaN(valor)) {
            if (valor > 100) {
                $(this).val(100);
            } else if (valor < 0) {
                $(this).val(0);
            }
        } else {
            $(this).val('');
        }
    });
    $('#fecha_inicio, #fecha_fin').on('change', function () {
        const fechaInicio = $('#fecha_inicio').val();
        const fechaFin = $('#fecha_fin').val();
        const today = new Date().toISOString().split('T')[0];
        if (fechaInicio && fechaInicio < today) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Fecha',
                text: 'La fecha de inicio no puede ser anterior a hoy',
                icon: 'error'
            });
            $('#fecha_inicio').val('');
            return;
        }
        if (fechaFin && fechaFin < today) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Fecha',
                text: 'La fecha fin no puede ser anterior a hoy',
                icon: 'error'
            });
            $('#fecha_fin').val('');
            return;
        }
        if (fechaInicio && fechaFin && fechaInicio >= fechaFin) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Fechas',
                text: 'La fecha de inicio debe ser anterior a la fecha fin',
                icon: 'error'
            });
            $(this).val('');
            return;
        }
    });
    $('form').on('submit', function (e) {
        const isEditPage = window.location.href.includes('editar');
        const isDescuentoPage = window.location.href.includes('descuento');
        if (!isDescuentoPage) return true;
        e.preventDefault();
        const campos = {
            'nombre_descuento': 'Ingrese el nombre del descuento',
            'descripcion': 'Ingrese la descripción del descuento',
            'porcentaje': 'Ingrese el porcentaje del descuento',
            'estado_descuento': 'Seleccione el estado del descuento'
        };
        const esPromocion = window.location.href.includes('crear') ||
            (window.location.href.includes('editar') &&
                parseInt($('#id_descuento').val()) > 5);
        if ($('#fecha_inicio').length && !$('#fecha_inicio').prop('disabled')) {
            campos['fecha_inicio'] = 'Ingrese la fecha de inicio';
        }
        if ($('#fecha_fin').length && !$('#fecha_fin').prop('disabled')) {
            campos['fecha_fin'] = 'Ingrese la fecha de fin';
        }
        for (let [id, mensaje] of Object.entries(campos)) {
            const elemento = $(`#${id}`);
            if (elemento.length && !elemento.prop('disabled')) {
                const valor = elemento.val()?.trim();
                if (!valor) {
                    Swal.fire({
                        ...sweetAlertOptions,
                        title: 'Campo Requerido',
                        text: mensaje,
                        icon: 'warning'
                    });
                    elemento.focus();
                    return false;
                }
            }
        }
        const nombre = $('#nombre_descuento').val().trim();
        if (!/^[a-zA-Z0-9\sáéíóúÁÉÍÓÚñÑ]{3,50}$/.test(nombre)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Nombre',
                text: 'El nombre debe tener entre 3 y 50 caracteres (letras, números y espacios)',
                icon: 'error'
            });
            $('#nombre_descuento').focus();
            return false;
        }
        const descripcion = $('#descripcion').val().trim();
        if (descripcion.length < 3) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Descripción',
                text: 'La descripción debe tener al menos 3 caracteres',
                icon: 'error'
            });
            $('#descripcion').focus();
            return false;
        }
        const porcentaje = parseInt($('#porcentaje').val());
        if (isNaN(porcentaje) || porcentaje < 1 || porcentaje > 100) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Porcentaje',
                text: 'El porcentaje debe estar entre 1 y 100',
                icon: 'error'
            });
            $('#porcentaje').focus();
            return false;
        }
        const estado = $('#estado_descuento').val();
        if (!estado || estado === "") {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Estado',
                text: 'Debe seleccionar un estado válido',
                icon: 'error'
            });
            $('#estado_descuento').focus();
            return false;
        }
        if (esPromocion) {
            const fechaInicio = $('#fecha_inicio').val();
            const fechaFin = $('#fecha_fin').val();
            const today = new Date().toISOString().split('T')[0];
            if (fechaInicio < today) {
                Swal.fire({
                    ...sweetAlertOptions,
                    title: 'Error en Fecha',
                    text: 'La fecha de inicio no puede ser anterior a hoy',
                    icon: 'error'
                });
                $('#fecha_inicio').focus();
                return false;
            }
            if (fechaFin < today) {
                Swal.fire({
                    ...sweetAlertOptions,
                    title: 'Error en Fecha',
                    text: 'La fecha fin no puede ser anterior a hoy',
                    icon: 'error'
                });
                $('#fecha_fin').focus();
                return false;
            }
            if (fechaInicio >= fechaFin) {
                Swal.fire({
                    ...sweetAlertOptions,
                    title: 'Error en Fechas',
                    text: 'La fecha de inicio debe ser anterior a la fecha fin',
                    icon: 'error'
                });
                $('#fecha_inicio').focus();
                return false;
            }
        }
        if (isEditPage) {
            Swal.fire({
                ...sweetAlertOptions,
                title: '¿Confirmar cambios?',
                text: '¿Está seguro que desea guardar los cambios realizados?',
                icon: 'question',
                showCancelButton: true
            }).then((result) => {
                if (result.isConfirmed) {
                    this.submit();
                }
            });
        } else {
            this.submit();
        }
    });
});

function calcularHoraLlegada() {
    const horaSalida = $('#hora_salida').val();
    const rutaInput = document.getElementById('ruta_input');
    const tiempoEstimado = rutaInput.getAttribute('data-tiempo');
    if (horaSalida && tiempoEstimado) {
        const [horas, minutos] = tiempoEstimado.split('h ');
        const minutosViaje = (parseInt(horas) * 60) + (parseInt(minutos) || 0);
        const salida = new Date(`2000-01-01T${horaSalida}`);
        const llegada = new Date(salida.getTime() + minutosViaje * 60000);
        $('#hora_llegada').val(llegada.toTimeString().slice(0, 5));
    }
}

$(document).ready(function () {
    $('#hora_salida').on('change', calcularHoraLlegada);
    $(document).on('click', '.searchable-select-option', function () {
        const tiempo = $(this).data('tiempo');
        if (tiempo) {
            $('#ruta_input').attr('data-tiempo', tiempo);
            calcularHoraLlegada();
        }
    });
    $('form').on('submit', function (e) {
        const isEditPage = window.location.href.includes('editar');
        const isHorarioPage = window.location.href.includes('horario');
        if (!isHorarioPage) return true;
        e.preventDefault();
        const campos = {
            'hora_salida': 'Seleccione la hora de salida',
            'ruta_id': 'Seleccione una ruta',
            'estado_horario': 'Seleccione el estado del horario'
        };
        for (let [id, mensaje] of Object.entries(campos)) {
            const valor = $(`#${id}`).val()?.trim();
            if (!valor) {
                Swal.fire({
                    ...sweetAlertOptions,
                    title: 'Campo Requerido',
                    text: mensaje,
                    icon: 'warning'
                });
                $(`#${id}`).focus();
                return false;
            }
        }
        const horaSalida = $('#hora_salida').val();
        const horaLlegada = $('#hora_llegada').val();
        if (!horaSalida || !horaLlegada) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Horario',
                text: 'Debe especificar hora de salida y llegada',
                icon: 'error'
            });
            return false;
        }
        if (isEditPage) {
            Swal.fire({
                ...sweetAlertOptions,
                title: '¿Confirmar cambios?',
                text: '¿Está seguro que desea guardar los cambios realizados?',
                icon: 'question',
                showCancelButton: true
            }).then((result) => {
                if (result.isConfirmed) {
                    this.submit();
                }
            });
        } else {
            this.submit();
        }
    });
});

function calcularTiempoBase() {
    const distancia = parseInt($('#distancia').val()) || 0;
    const busId = $('#bus_id').val();
    const selectedOption = document.querySelector(`.searchable-select-option[data-id="${busId}"]`);
    if (selectedOption && distancia >= 1) {
        const velocidad = parseInt(selectedOption.dataset.velocidad) || 0;
        if (velocidad > 0) {
            const tiempoHoras = distancia / velocidad;
            const horasBase = Math.floor(tiempoHoras);
            const minutosBase = Math.round((tiempoHoras - horasBase) * 60);
            return (horasBase * 60) + minutosBase;
        }
    }
    return 0;
}
function calcularTiempoEscalas() {
    let minutosEscalas = 0;
    document.querySelectorAll('.tiempo-escala').forEach(input => {
        if (input.value) {
            const [horas, minutos] = input.value.split(':');
            minutosEscalas += (parseInt(horas) * 60) + parseInt(minutos);
        }
    });
    return minutosEscalas;
}
function actualizarTiempoEstimado() {
    const tiempoBase = calcularTiempoBase();
    const tiempoEscalas = calcularTiempoEscalas();
    const tiempoTotal = tiempoBase + tiempoEscalas;
    if (tiempoTotal > 0) {
        const horasTotal = Math.floor(tiempoTotal / 60);
        const minutosFinales = tiempoTotal % 60;
        $('#tiempo_estimado').val(`${horasTotal}h ${minutosFinales}min`);
    } else {
        $('#tiempo_estimado').val('');
    }
}
function validarEscalaUnica(inputEscala) {
    const todasLasEscalas = document.querySelectorAll('input[name="lugar_escala[]"]');
    const valorActual = inputEscala.value.trim().toLowerCase();
    let esUnica = true;
    todasLasEscalas.forEach(escala => {
        if (escala !== inputEscala && escala.value.trim().toLowerCase() === valorActual) {
            esUnica = false;
            escala.classList.add('is-invalid');
            inputEscala.classList.add('is-invalid');
        }
    });
    if (esUnica) {
        inputEscala.classList.remove('is-invalid');
    }
    return esUnica;
}
function validarTodasLasEscalas() {
    const lugares = new Set();
    const escalas = document.querySelectorAll('input[name="lugar_escala[]"]');
    let esValido = true;
    escalas.forEach(input => {
        const lugar = input.value.trim().toLowerCase();
        if (lugar) {
            if (lugares.has(lugar)) {
                input.classList.add('is-invalid');
                esValido = false;
            } else {
                lugares.add(lugar);
                input.classList.remove('is-invalid');
            }
        }
    });
    if (!esValido) {
        Swal.fire({
            ...sweetAlertOptions,
            title: 'Error de Validación',
            text: 'No pueden existir escalas con el mismo nombre',
            icon: 'warning'
        });
    }
    return esValido;
}
$(document).on('input', '.tiempo-escala', actualizarTiempoEstimado);
$(document).on('change', '.tiempo-escala', actualizarTiempoEstimado);
$('#distancia').on('input', actualizarTiempoEstimado);
$(document).on('click', '.searchable-select-option', function () {
    setTimeout(actualizarTiempoEstimado, 100);
});
$(document).on('click', '.searchable-select-option', function () {
    const distanciaExistente = $('#distancia').val();
    if (distanciaExistente && parseInt(distanciaExistente) >= MIN_DISTANCIA) {
        actualizarTiempoEstimado();
    }
});
$(document).ready(function () {
    const MIN_PRECIO = 0.25;
    const MAX_PRECIO = 300.00;
    const MIN_DISTANCIA = 1;
    const MAX_DISTANCIA = 500;
    $('#precio_unitario').on('input', function (e) {
        let valor = e.target.value;
        if (valor === '') {
            $(this).val('');
            return;
        }
        let numeroValor = parseFloat(valor);
        if (!isNaN(numeroValor)) {
            if (numeroValor === 0) {
                $(this).val(MIN_PRECIO.toFixed(2));
            } else if (numeroValor > MAX_PRECIO) {
                $(this).val(MAX_PRECIO.toFixed(2));
            } else if (valor.includes('.')) {
                const decimales = valor.split('.')[1];
                if (decimales.length > 2) {
                    $(this).val(parseFloat(valor).toFixed(2));
                }
            }
        }
    });
    $('#precio_unitario').on('blur', function () {
        let valor = $(this).val();
        if (valor === '') {
            $(this).val(MIN_PRECIO.toFixed(2));
            return;
        }
        let numeroValor = parseFloat(valor);
        if (isNaN(numeroValor) || numeroValor < MIN_PRECIO) {
            $(this).val(MIN_PRECIO.toFixed(2));
        }
    });
    $('#origen, #destino').on('input', function () {
        let valor = $(this).val();
        valor = valor.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
        $(this).val(valor);
    });
    $('#distancia').on('input', function () {
        let valor = $(this).val();
        if (valor === '') {
            $(this).val('');
            actualizarTiempoEstimado();
            return;
        }
        let numeroValor = parseInt(valor);
        if (!isNaN(numeroValor)) {
            if (numeroValor === 0) {
                $(this).val('');
            } else if (numeroValor > MAX_DISTANCIA) {
                $(this).val(MAX_DISTANCIA);
            }
        }
        actualizarTiempoEstimado();
    });
    $('form').on('submit', function (e) {
        const isEditPage = window.location.href.includes('editar');
        const isRutaPage = window.location.href.includes('ruta');
        if (!isRutaPage) return true;
        e.preventDefault();
        if (!validarTodasLasEscalas()) {
            e.preventDefault();
            return false;
        }
        const campos = {
            'origen': 'Ingrese el origen',
            'destino': 'Ingrese el destino',
            'precio_unitario': 'Ingrese el precio',
            'distancia': 'Ingrese la distancia',
            'estado_ruta': 'Seleccione un estado',
            'bus_id': 'Seleccione un bus'
        };
        for (let [id, mensaje] of Object.entries(campos)) {
            const valor = $(`#${id}`).val()?.trim();
            if (!valor) {
                Swal.fire({
                    ...sweetAlertOptions,
                    title: 'Campo Requerido',
                    text: mensaje,
                    icon: 'warning'
                });
                $(`#${id}`).focus();
                return false;
            }
        }
        const origen = $('#origen').val().trim();
        const destino = $('#destino').val().trim();
        if (origen.toLowerCase() === destino.toLowerCase()) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error',
                text: 'El origen y destino no pueden ser iguales',
                icon: 'error'
            });
            return false;
        }
        const precio = parseFloat($('#precio_unitario').val());
        if (isNaN(precio) || precio <= 0 || precio > 999.99) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error',
                text: 'El precio debe ser mayor a 0 y menor a 1000',
                icon: 'error'
            });
            $('#precio_unitario').focus();
            return false;
        }
        const distancia = parseInt($('#distancia').val());
        if (isNaN(distancia) || distancia <= 0) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error',
                text: 'La distancia debe ser mayor a 0',
                icon: 'error'
            });
            $('#distancia').focus();
            return false;
        }
        const escalas = document.getElementsByClassName('escala-row');
        if (escalas.length > 0) {
            for (let escala of escalas) {
                const lugarInput = escala.querySelector('input[name*="lugar_escala"]');
                const tiempoInput = escala.querySelector('input[name*="tiempo_escala"]');
                if (!lugarInput.value.trim()) {
                    Swal.fire({
                        ...sweetAlertOptions,
                        title: 'Campo Requerido',
                        text: 'Debe ingresar el lugar de la escala',
                        icon: 'warning'
                    });
                    lugarInput.focus();
                    return false;
                }
                if (!tiempoInput.value) {
                    Swal.fire({
                        ...sweetAlertOptions,
                        title: 'Campo Requerido',
                        text: 'Debe ingresar el tiempo de la escala',
                        icon: 'warning'
                    });
                    tiempoInput.focus();
                    return false;
                }
            }
        }
        if (isEditPage) {
            Swal.fire({
                ...sweetAlertOptions,
                title: '¿Confirmar cambios?',
                text: '¿Está seguro que desea guardar los cambios realizados?',
                icon: 'question',
                showCancelButton: true
            }).then((result) => {
                if (result.isConfirmed) {
                    this.submit();
                }
            });
        } else {
            this.submit();
        }
    });
    $(document).on('input', 'input[name="lugar_escala[]"]', function () {
        validarEscalaUnica(this);
    });
});

$('form').on('submit', function (e) {
    const isEditPage = window.location.href.includes('editar');
    const isBoletoPage = window.location.href.includes('boleto');
    if (!isBoletoPage) return true;
    e.preventDefault();
    const campos = {
        'asientos': 'Ingrese los números de asiento',
        'persona_id': 'Seleccione una persona',
        'turno_id': 'Seleccione un turno'
    };
    for (let [id, mensaje] of Object.entries(campos)) {
        const valor = $(`#${id}`).val()?.trim();
        if (!valor) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Campo Requerido',
                text: mensaje,
                icon: 'warning'
            });
            $(`#${id}`).focus();
            return false;
        }
    }
    const asientos = $('#asientos').val().split(',').filter(x => x.trim() !== '');
    if (asientos.length === 0) {
        Swal.fire({
            ...sweetAlertOptions,
            title: 'Error',
            text: 'Debe seleccionar al menos un asiento',
            icon: 'error'
        });
        $('#asientos').focus();
        return false;
    }
    const capacidadMaxima = parseInt($('#max-asientos').text());
    const asientosInvalidos = asientos.some(a => {
        const num = parseInt(a);
        return isNaN(num) || num < 1 || num > capacidadMaxima;
    });
    if (asientosInvalidos) {
        Swal.fire({
            ...sweetAlertOptions,
            title: 'Error',
            text: `Los números de asiento deben estar entre 1 y ${capacidadMaxima}`,
            icon: 'error'
        });
        $('#asientos').focus();
        return false;
    }
    const precioFinal = parseFloat($('#precio_final').val());
    if (!precioFinal || precioFinal <= 0) {
        Swal.fire({
            ...sweetAlertOptions,
            title: 'Error',
            text: 'El precio final debe ser mayor a 0',
            icon: 'error'
        });
        return false;
    }
    if (isEditPage) {
        Swal.fire({
            ...sweetAlertOptions,
            title: '¿Confirmar cambios?',
            text: '¿Está seguro que desea guardar los cambios realizados?',
            icon: 'question',
            showCancelButton: true
        }).then((result) => {
            if (result.isConfirmed) {
                this.submit();
            }
        });
    } else {
        this.submit();
    }
});

function validarCedula(cedula) {
    if (!/^\d{10}$/.test(cedula)) return false;
    const coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2];
    const provincia = parseInt(cedula.substring(0, 2));
    if (provincia < 1 || provincia > 24) return false;
    const tercerDigito = parseInt(cedula.charAt(2));
    if (tercerDigito > 6) return false;
    let suma = 0;
    for (let i = 0; i < 9; i++) {
        let valor = parseInt(cedula.charAt(i)) * coeficientes[i];
        if (valor > 9) valor -= 9;
        suma += valor;
    }
    const digitoVerificador = 10 - (suma % 10);
    const ultimoDigito = parseInt(cedula.charAt(9));
    return digitoVerificador === 10 ? ultimoDigito === 0 : digitoVerificador === ultimoDigito;
}
function validarLicencia(licencia) {
    return /^[A-Z]\d{8}$/.test(licencia);
}
function validarPasaporte(pasaporte) {
    return /^[A-Z][A-Z0-9]{7,11}$/.test(pasaporte);
}
$(document).ready(function () {
    $('#nombre, #apellido').on('input', function () {
        let valor = $(this).val();
        valor = valor.replace(/[^a-záéíóúñüA-ZÁÉÍÓÚÑÜ\s]/g, '');
        $(this).val(valor);
    });
    $('#telefono').on('input', function () {
        let valor = $(this).val();
        $(this).val(formatearTelefono(valor));
    });
    $('#tipo_identificacion').on('change', function () {
        const tipo = $(this).val();
        const input = $('#numero_identificacion');
        input.val('');
        switch (tipo) {
            case 'CEDULA':
                input.attr('maxlength', '10');
                input.attr('pattern', '\\d{10}');
                break;
            case 'LICENCIA':
                input.attr('maxlength', '9');
                input.attr('pattern', '[A-Z]\\d{8}');
                break;
            case 'PASAPORTE':
                input.attr('maxlength', '12');
                input.attr('pattern', '[A-Z][A-Z0-9]{7,11}');
                break;
        }
    });
    $('#numero_identificacion').on('input', function () {
        let valor = $(this).val();
        const tipo = $('#tipo_identificacion').val();
        switch (tipo) {
            case 'CEDULA':
                valor = valor.replace(/\D/g, '');
                break;
            case 'LICENCIA':
                valor = valor.replace(/[^A-Z0-9]/g, '').toUpperCase();
                if (valor.length >= 1) {
                    const primera = valor.charAt(0);
                    if (!/[A-Z]/.test(primera)) {
                        valor = '';
                    }
                }
                break;
            case 'PASAPORTE':
                valor = valor.replace(/[^A-Z0-9]/g, '').toUpperCase();
                break;
        }
        $(this).val(valor);
    });
    const today = new Date().toISOString().split('T')[0];
    $('#fecha_nacimiento').attr('max', today);
    $('#fecha_nacimiento').on('input', function () {
        const selectedDate = $(this).val();
        if (selectedDate > today) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Fecha',
                text: 'La fecha de nacimiento no puede ser mayor a hoy',
                icon: 'error'
            });
            $(this).val('');
            return false;
        }
    });
    $('form').on('submit', function (e) {
        const isEditPage = window.location.href.includes('editar');
        const isPersonaForm = window.location.href.includes('persona');
        const isRegistroForm = window.location.href.includes('registro');
        if (!isPersonaForm && !isRegistroForm) {
            return true;
        }
        const tipoId = $('#tipo_identificacion').val();
        const numId = $('#numero_identificacion').val();
        if (!tipoId) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Campo Requerido',
                text: 'Seleccione un tipo de identificación',
                icon: 'warning'
            });
            $('#tipo_identificacion').focus();
            return false;
        }
        if (!numId) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Campo Requerido',
                text: 'Ingrese el número de identificación',
                icon: 'warning'
            });
            $('#numero_identificacion').focus();
            return false;
        }
        switch (tipoId) {
            case 'CEDULA':
                if (!validarCedula(numId)) {
                    Swal.fire({
                        ...sweetAlertOptions,
                        title: 'Error de Validación',
                        text: 'El número de cédula ingresado no es válido',
                        icon: 'error'
                    });
                    $('#numero_identificacion').focus();
                    return false;
                }
                break;
            case 'LICENCIA':
                if (!validarLicencia(numId)) {
                    Swal.fire({
                        ...sweetAlertOptions,
                        title: 'Error de Validación',
                        text: 'El número de licencia debe tener formato A12345678',
                        icon: 'error'
                    });
                    $('#numero_identificacion').focus();
                    return false;
                }
                break;
            case 'PASAPORTE':
                if (!validarPasaporte(numId)) {
                    Swal.fire({
                        ...sweetAlertOptions,
                        title: 'Error de Validación',
                        text: 'El número de pasaporte no tiene un formato válido',
                        icon: 'error'
                    });
                    $('#numero_identificacion').focus();
                    return false;
                }
                break;
        }
        const camposComunes = {
            'tipo_identificacion': 'Seleccione un tipo de identificación',
            'numero_identificacion': 'Ingrese el número de identificación',
            'nombre': 'Ingrese el nombre',
            'apellido': 'Ingrese el apellido',
            'fecha_nacimiento': 'Seleccione la fecha de nacimiento',
            'correo': 'Ingrese el correo electrónico',
            'contrasenia': 'Ingrese la contraseña'
        };
        const camposPersona = {
            ...camposComunes,
            'direccion': 'Ingrese la dirección',
            'genero': 'Seleccione el género',
            'telefono': 'Ingrese el teléfono',
            'tipo_tarifa': 'Seleccione el tipo de tarifa',
            'tipo_cuenta': 'Seleccione el tipo de cuenta',
            'estado_cuenta': 'Seleccione el estado de la cuenta'
        };
        // const camposRequeridos = {
        //     'nombre': 'Ingrese el nombre',
        //     'apellido': 'Ingrese el apellido',
        //     'fecha_nacimiento': 'Seleccione la fecha de nacimiento',
        //     'direccion': 'Ingrese la dirección',
        //     'genero': 'Seleccione el género',
        //     'telefono': 'Ingrese el teléfono',
        //     'correo': 'Ingrese el correo electrónico',
        //     'tipo_tarifa': 'Seleccione el tipo de tarifa',
        //     'contrasenia': 'Ingrese la contraseña',
        //     'tipo_cuenta': 'Seleccione el tipo de cuenta',
        //     'estado_cuenta': 'Seleccione el estado de la cuenta'
        // };
        const camposRequeridos = isPersonaForm ? camposPersona : camposComunes;
        for (let [id, mensaje] of Object.entries(camposRequeridos)) {
            const valor = $(`#${id}`).val()?.trim();
            if (!valor) {
                Swal.fire({
                    ...sweetAlertOptions,
                    title: 'Campo Requerido',
                    text: mensaje,
                    icon: 'warning'
                });
                $(`#${id}`).focus();
                return false;
            }
        }
        const correo = $('#correo').val().trim();
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error de Validación',
                text: 'Ingrese un correo electrónico válido',
                icon: 'error'
            });
            $('#correo').focus();
            return false;
        }
        const contrasenia = $('#contrasenia').val();
        if (contrasenia.length < 8) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Contraseña',
                text: 'La contraseña debe tener al menos 8 caracteres',
                icon: 'error'
            });
            $('#contrasenia').focus();
            return false;
        }
        const fechaNacimiento = new Date($('#fecha_nacimiento').val());
        const hoy = new Date();
        const edad = hoy.getFullYear() - fechaNacimiento.getFullYear();
        if (edad < 12) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error de Validación',
                text: 'Debe ser mayor de 12 años para registrarse',
                icon: 'error'
            });
            $('#fecha_nacimiento').focus();
            return false;
        }
        if (isEditPage) {
            Swal.fire({
                ...sweetAlertOptions,
                title: '¿Confirmar cambios?',
                text: '¿Está seguro que desea guardar los cambios realizados?',
                icon: 'question',
                showCancelButton: true
            }).then((result) => {
                if (result.isConfirmed) {
                    this.submit();
                }
            });
        } else {
            this.submit();
        }
    });
});

$(document).ready(function () {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const maxDate = new Date();
    maxDate.setMonth(maxDate.getMonth() + 12);
    const formatDate = (date) => {
        const d = new Date(date);
        let month = '' + (d.getMonth() + 1);
        let day = '' + d.getDate();
        const year = d.getFullYear();
        if (month.length < 2) month = '0' + month;
        if (day.length < 2) day = '0' + day;
        return [year, month, day].join('-');
    };
    $('#fecha_salida').attr('min', formatDate(today));
    $('#fecha_salida').attr('max', formatDate(maxDate));
    $('#fecha_salida').on('blur', function () {
        const selectedDate = $(this).val();
        const currentDate = today;
        if (selectedDate < currentDate) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Fecha',
                text: 'No se pueden seleccionar fechas pasadas',
                icon: 'error'
            });
            $(this).val('');
            return false;
        }
        if (selectedDate > maxDate) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Fecha',
                text: 'Solo se pueden programar turnos hasta 12 meses adelante',
                icon: 'error'
            });
            $(this).val('');
            return false;
        }
    });
    $('form').on('submit', function (e) {
        const isEditPage = window.location.href.includes('editar');
        const isTurnoPage = window.location.href.includes('turno');
        if (!isTurnoPage) return true;
        e.preventDefault();
        const campos = {
            'numero_turno': 'Ingrese el número de turno',
            'fecha_salida': 'Seleccione la fecha de salida',
            'horario_id': 'Seleccione un horario',
            'estado_turno': 'Seleccione un estado'
        };
        for (let [id, mensaje] of Object.entries(campos)) {
            const valor = $(`#${id}, input[name="${id}"]`).val()?.trim();
            if (!valor) {
                Swal.fire({
                    ...sweetAlertOptions,
                    title: 'Campo Requerido',
                    text: mensaje,
                    icon: 'warning'
                });
                $(`#${id}, input[name="${id}"]`).focus();
                return false;
            }
        }
        const fechaSalida = new Date($('#fecha_salida').val() + 'T00:00:00');
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        fechaSalida.setHours(0, 0, 0, 0);
        const maxDate = new Date();
        maxDate.setMonth(maxDate.getMonth() + 12);
        if (fechaSalida.getTime() < today.getTime() - 86400000) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Fecha',
                text: 'No se pueden seleccionar fechas pasadas',
                icon: 'error'
            });
            $('#fecha_salida').focus();
            return false;
        }
        if (fechaSalida > maxDate) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error en Fecha',
                text: 'Solo se pueden programar turnos hasta 12 meses adelante',
                icon: 'error'
            });
            $('#fecha_salida').focus();
            return false;
        }
        if (!$('#horario_id').val()) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Error',
                text: 'Debe seleccionar un horario válido',
                icon: 'error'
            });
            $('#horario_input').focus();
            return false;
        }
        if (isEditPage) {
            Swal.fire({
                ...sweetAlertOptions,
                title: '¿Confirmar cambios?',
                text: '¿Está seguro que desea guardar los cambios realizados?',
                icon: 'question',
                showCancelButton: true
            }).then((result) => {
                if (result.isConfirmed) {
                    this.submit();
                }
            });
        } else {
            this.submit();
        }
    });
});

$(document).ready(function () {
    $('form').on('submit', function (e) {
        const isEditPage = window.location.href.includes('editar');
        const isEscalaPage = window.location.href.includes('escala');
        if (!isEscalaPage) return true;
        e.preventDefault();
        const campos = {
            'lugar_escala': 'Ingrese el lugar de la escala',
            'tiempo': 'Ingrese el tiempo de parada'
        };
        for (let [id, mensaje] of Object.entries(campos)) {
            const valor = $(`#${id}`).val()?.trim();
            if (!valor) {
                Swal.fire({
                    ...sweetAlertOptions,
                    title: 'Campo Requerido',
                    text: mensaje,
                    icon: 'warning'
                });
                $(`#${id}`).focus();
                return false;
            }
        }
        const lugarEscala = $('#lugar_escala').val().trim();
        if (lugarEscala.length < 3) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Validación',
                text: 'El lugar de escala debe tener al menos 3 caracteres',
                icon: 'warning'
            });
            $('#lugar_escala').focus();
            return false;
        }
        const tiempo = $('#tiempo').val();
        const [horas, minutos] = tiempo.split(':').map(Number);
        if (isNaN(horas) || isNaN(minutos)) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Validación',
                text: 'Formato de tiempo inválido',
                icon: 'warning'
            });
            $('#tiempo').focus();
            return false;
        }
        const tiempoTotal = (horas * 60) + minutos;
        if (tiempoTotal < 5 || tiempoTotal > 120) {
            Swal.fire({
                ...sweetAlertOptions,
                title: 'Validación',
                text: 'El tiempo debe estar entre 5 minutos y 2 horas',
                icon: 'warning'
            });
            $('#tiempo').focus();
            return false;
        }
        if (isEditPage) {
            Swal.fire({
                ...sweetAlertOptions,
                title: '¿Confirmar cambios?',
                text: '¿Está seguro que desea guardar los cambios realizados?',
                icon: 'question',
                showCancelButton: true
            }).then((result) => {
                if (result.isConfirmed) {
                    this.submit();
                }
            });
        } else {
            this.submit();
        }
    });
});

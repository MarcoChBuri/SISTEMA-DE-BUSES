document.addEventListener('DOMContentLoaded', function () {
    "{% with messages = get_flashed_messages(with_categories = true) %}"
    "{% if messages %}"
    "{% for category, message in messages %}"
    if ('{{ category }}' === 'success') {
        Swal.fire({
            title: '¡Éxito!',
            text: '{{ message }}',
            icon: 'success',
            confirmButtonColor: '#3085d6'
        });
    }
    "{% endfor %}"
    "{% endif %}"
    "{% endwith %}"
    const deleteForms = document.querySelectorAll('.delete-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            Swal.fire({
                title: '¿Está seguro?',
                text: '¿Realmente desea eliminar este bus?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#d33',
                cancelButtonColor: '#3085d6',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    form.submit();
                }
            });
        });
    });
});
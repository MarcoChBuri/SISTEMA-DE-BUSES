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
});
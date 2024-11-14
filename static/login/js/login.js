if (!localStorage.getItem('token') && !sessionStorage.getItem('token')) {
    alert('Debes iniciar sesión para acceder a esta página.');
    window.location.href = '/login';
}
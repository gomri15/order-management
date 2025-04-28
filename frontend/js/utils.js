function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}

function getToken() {
    return localStorage.getItem("token");
}

if (!getToken()) {
    window.location.href = "login.html";
}
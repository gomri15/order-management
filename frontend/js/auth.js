export function getTokenOrRedirect() {
    const token = localStorage.getItem("token");
    if (!token) {
        window.location.href = "/login";
        throw new Error("No token found");
    }
    return token;
}

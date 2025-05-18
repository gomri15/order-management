window.onload = function () {
    const token = localStorage.getItem("token");
    if (token) {
        window.location.href = "index.html"; // Redirect to main page
    }

    const form = document.querySelector("form");
    form.addEventListener("submit", login);
}

async function login(event) {
    event.preventDefault(); // prevent form submission reload

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    const errorEl = document.getElementById("error");

    try {
        const res = await fetch("/api/users/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ "email": username, password })
        });

        if (!res.ok) throw new Error("Invalid login");

        const data = await res.json();
        localStorage.setItem("token", data.access_token);
        window.location.href = "index.html";
    } catch (err) {
        errorEl.textContent = "Login failed: " + err.message;
    }
}
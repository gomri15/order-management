import {fetchWithAuth} from './fetchWithAuth.js';
import {getTokenOrRedirect} from "./auth.js";

const currentUser = {
    id: "",
    name: "",
    email: ""
};

async function loadUser() {
    const token = getTokenOrRedirect();

    try {
        const user = await fetchWithAuth("http://localhost:8000/users/current", token);

        Object.assign(currentUser, user);

        document.getElementById("user-info").innerHTML = `
      <strong>ID:</strong> ${currentUser.id}<br/>
      <strong>Name:</strong> ${currentUser.name}<br/>
      <strong>Email:</strong> ${currentUser.email}
    `;
    } catch (err) {
        alert("Could not load user info");
    }
}

async function updateProfile() {
    const token = getTokenOrRedirect();

    const userName = document.getElementById("name").value;
    const userEmail = document.getElementById("email").value;

    if (userEmail === currentUser.email && userName === currentUser.name) {
        alert("No changes detected");
        return;
    }

    fetchWithAuth(`http://localhost:8000/users/${currentUser.id}`, token, {
        method: "PUT",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({name: userName, email: userEmail}),
    })
        .then(() => {
            loadUser();
        })
        .catch(err => {
            console.error("Error updating user:", err);
            alert("Could not update user info");
        });
}

addEventListener("DOMContentLoaded", () => {
    loadUser();

    document.getElementById("update-button").addEventListener("click", (e) => {
        e.preventDefault();
        updateProfile();
    });
});

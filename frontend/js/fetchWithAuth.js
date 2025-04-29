export async function fetchWithAuth(url, token, options = {}) {
    try {
        const res = await fetch(url, {
            ...options,
            headers: {
                ...(options.headers || {}),
                "Authorization": `Bearer ${token}`,
                "Content-Type": "application/json",
            },
        });

        if (res.status === 401 || res.status === 403) {
            window.location.href = "/api/login";
            throw new Error("Unauthorized access. Redirecting to login.");
        }

        if (!res.ok) {
            const errorText = await res.text();
            throw new Error(`Request failed with status ${res.status}: ${errorText}`);
        }

        return await res.json();
    } catch (err) {
        console.error("Fetch error:", err);
        throw err;
    }
}

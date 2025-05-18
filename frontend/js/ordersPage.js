import {getTokenOrRedirect} from "./auth.js";
import {fetchWithAuth} from "./fetchWithAuth.js";


 const token = getTokenOrRedirect();

async function getOrderItems(order) {
    const orderItems = await fetchWithAuth(`/api/orders/${order.id}/items/`, token)
    return orderItems.map(item => ({
        name: item.product_display_name,
        unit_price: item.unit_price,
        quantity: item.quantity
    }));
}

async function renderOrderItems(order) {
    const orderItems = await getOrderItems(order);

    const productListElement = document.createElement("ul");
    productListElement.innerHTML = "";
    orderItems.map((item) => {
        const li = document.createElement("li");
        li.textContent = `${item.name} - $${item.unit_price.toFixed(2)} (x${item.quantity})`;
        productListElement.appendChild(li);
    });
    return productListElement;
}

async function createDetailsButton(order) {
    const modal = document.getElementById("myModal");
    const span = document.getElementsByClassName("close")[0];
    const button = document.createElement("button");
    const modalText = document.getElementById("modal-text");

    button.textContent = "Details";
    button.onclick = async () => {
        const productList = await renderOrderItems(order);
        modal.style.display = "block";
        modalText.innerHTML = `
            <h2>Order #${order.id}</h2>
            <p>Status: ${order.status_id}</p>
            <p>Products: </p>
            <div>${productList.outerHTML}</div>
            <p>Total Price: $${order.total_price.toFixed(2)}</p>
            <p>Created At: ${new Date(order.created_at).toLocaleString()}</p>
            <p>Shipping Address: ${order.shipping_address}</p>
        `
    }
    span.onclick = () => {
        modal.style.display = "none";
    }

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
    return button;
}

async function loadOrders() {
    const list = document.getElementById("orders-list");

    try {
        const res = await fetch("/api/orders/", {
            headers: {Authorization: `Bearer ${token}`}
        });

        if (!res.ok) throw new Error("Failed to fetch orders");

        const orders = await res.json();

        for (const order of orders) {
            const li = document.createElement("li");
            const button = await createDetailsButton(order);

            li.textContent = `Order #${order.id} — Status: ${order.status_id}`;
            li.appendChild(button);
            list.appendChild(li);
        }

    } catch (err) {
        const li = document.createElement("li");
        li.textContent = "Error: " + err.message;
        list.appendChild(li);
    }
}

window.onload = loadOrders;
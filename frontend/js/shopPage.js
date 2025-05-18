import {getTokenOrRedirect} from "./auth.js";


let cart = {}; 
const productCache = {}; 
const token = getTokenOrRedirect();

loadProducts()

async function loadProducts() {
    const list = document.getElementById("product-list");
    list.innerHTML = "";

    try {
        const res = await fetch("/api/products/", {
            headers: {Authorization: `Bearer ${token}`}
        });

        const products = await res.json();

        products.forEach(p => {
            productCache[p.id] = p; 

            const li = document.createElement("li");
            li.textContent = `${p.name} - $${p.price.toFixed(2)} `;

            const btn = document.createElement("button");
            btn.textContent = "Add to Cart";
            btn.onclick = () => addToCart(p);
            li.appendChild(btn);

            list.appendChild(li);
        });

    } catch (e) {
        list.innerHTML = `<li>Error: ${e.message}</li>`;
    }
}

function addToCart(product) {
    if (cart[product.id]) {
        alert("Product already in cart!");
        return;
    }
    cart[product.id] = 1;
    renderCart();
}

function createPlusBtn(id) {
    const plusBtn = document.createElement("button");
    plusBtn.textContent = "+";
    plusBtn.onclick = () => {
        cart[id] += 1;
        renderCart();
    };
    return plusBtn;
}

function createMinusBtn(id) {
    const minusBtn = document.createElement("button");
    minusBtn.textContent = "-";
    minusBtn.onclick = () => {
        if (cart[id] > 1) {
            cart[id] -= 1;
        } else {
            delete cart[id];
        }
        renderCart();
    };
    return minusBtn;
}

function createCartItem(product, quantity) {
    const li = document.createElement("li");
    li.textContent = `${product.name} × ${quantity}`;
    return li;
}

function renderCart() {
    const cartList = document.getElementById("cart-list");
    cartList.innerHTML = "";

    for (const [id, quantity] of Object.entries(cart)) {
        const product = productCache[id];
        const cartItem = createCartItem(product, quantity);
        const minusBtn = createPlusBtn(id);
        const plusBtn = createMinusBtn(id);
        cartItem.appendChild(plusBtn);
        cartItem.appendChild(minusBtn);
        cartList.appendChild(cartItem);
    }
}

async function checkOut() {
    if (Object.keys(cart).length === 0) {
        alert("Your cart is empty!");
        return;
    }

    const items = Object.entries(cart).map(([product_id, quantity]) => {
        const product = productCache[product_id];
        return {
            product_id,
            quantity,
            unit_price: product.price
        };
    });

    const body = {
        items,
        shipping_address: "123 Developer Lane",
        shipping_city: "Codeville",
        shipping_postal_code: "12345",
        shipping_country: "Devland"
    };

    try {
        const res = await fetch("/api/orders/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`
            },
            body: JSON.stringify(body)
        });

        const result = await res.json();
        alert("Purchase complete! Order ID: " + result.id);
        cart = {};
        renderCart();

    } catch (e) {
        alert("Purchase failed: " + e.message);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("checkout-button").addEventListener("click", (e) => {
        e.preventDefault();
        checkOut();
    });
});
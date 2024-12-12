function updateCart(checkbox) {
    const cart = document.getElementById("selected-terpenes");
    const terpene = checkbox.value;
    const buttonColor = checkbox.closest(".terpene-option").style.backgroundColor; // Get the button color

    if (checkbox.checked) {
        // Add the selected terpene to the cart
        const listItem = document.createElement("li");
        listItem.textContent = terpene;
        listItem.setAttribute("id", `cart-${terpene}`);
        listItem.classList.add("cart-item");
        listItem.style.backgroundColor = buttonColor; // Set the background color to match the button
        cart.appendChild(listItem);
    } else {
        // Remove the terpene from the cart
        const itemToRemove = document.getElementById(`cart-${terpene}`);
        if (itemToRemove) {
            cart.removeChild(itemToRemove);
        }
    }
}

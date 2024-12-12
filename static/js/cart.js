function updateCart(checkbox) {
    const button = checkbox.closest(".terpene-option");

    if (checkbox.checked) {
        // Add the selected style
        button.classList.add("selected");
    } else {
        // Remove the selected style
        button.classList.remove("selected");
    }
}

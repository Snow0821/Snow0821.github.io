async function loadComponent(elementId, url) {
    try {
        const response = await fetch(url);
        const data = await response.text();
        const element = document.getElementById(elementId);
        element.innerHTML = data;
    } catch (error) {
        console.error(`Error loading component from ${url}:`, error);
    }
}

// Load header and footer on page load
document.addEventListener('DOMContentLoaded', () => {
    loadComponent('header-placeholder', '/components/header.html');
    loadComponent('footer-placeholder', '/components/footer.html');
});

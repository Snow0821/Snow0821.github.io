function loadComponent(componentName) {
    const path = `components/${componentName}/${componentName}`;
    
    // Load HTML
    fetch(`${path}.html`)
        .then(response => response.text())
        .then(data => {
            document.querySelector(componentName).outerHTML = data;

            // Load CSS
            const link = document.createElement("link");
            link.rel = "stylesheet";
            link.href = `${path}.css`;
            document.head.appendChild(link);

            // Load JavaScript
            const script = document.createElement("script");
            script.src = `${path}.js`;
            document.body.appendChild(script);
        });
}

function loadHeaderFooter() {
    loadComponent("header");
    loadComponent("footer");
}

document.addEventListener("DOMContentLoaded", loadHeaderFooter);

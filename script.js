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

    // Check which page is loaded and call the appropriate function
    if (document.getElementById('projects-container')) {
        loadProjects();
    }
    if (document.getElementById('portfolio-container')) {
        loadProjects('portfolio-container');
    }
    if (document.getElementById('notes-container')) {
        loadNotes();
    }
    if (document.getElementById('learnings-container')) {
        loadLearnings();
    }
    if (document.getElementById('todo-list')) {
        initializeTodoList();
    }
    if (document.getElementById('experiments-container')) {
        loadExperiments();
    }
});

function loadProjects(containerId = 'projects-container') {
    const container = document.getElementById(containerId);
    if (!container || typeof projects === 'undefined') {
        return;
    }

    // Filter for featured projects if on the homepage
    const projectsToDisplay = containerId === 'projects-container' 
        ? projects.filter(p => p.featured) 
        : projects;

    if (projectsToDisplay.length === 0 && containerId === 'projects-container') {
        container.innerHTML = "<p>Featured projects will be displayed here. See the full list in the portfolio.</p>";
        return;
    }

    const projectCards = projectsToDisplay.map(project => `
        <div class="card">
            <h3>${project.title}</h3>
            <p>${project.description}</p>
            <p>${project.status}</p>
            <div class="links">
                ${project.links.github ? `<a href="${project.links.github}" target="_blank">GitHub</a>` : ''}
                ${project.links.paper ? `<a href="${project.links.paper}" target="_blank">Paper</a>` : ''}
            </div>
        </div>
    `).join('');

    container.innerHTML = projectCards;
}

function loadNotes() {
    const container = document.getElementById('notes-container');
    if (!container || typeof notes === 'undefined') {
        return;
    }

    const noteLinks = notes.map(note => `
        <li>
            <a href="/dailynotes/notes/${note.file}">${note.date} - ${note.title}</a>
        </li>
    `).join('');

    container.innerHTML = `<ul>${noteLinks}</ul>`;
}

function loadLearnings() {
    const container = document.getElementById('learnings-container');
    if (!container || typeof learnings === 'undefined' || learnings.length === 0) {
        container.innerHTML = "<p>No learnings posted yet.</p>";
        return;
    }

    const learningLinks = learnings.map(learning => `
        <li>
            <a href="/learnings/${learning.file}">${learning.title}</a>
        </li>
    `).join('');

    container.innerHTML = `<ul>${learningLinks}</ul>`;
}

function loadExperiments() {
    const container = document.getElementById('experiments-container');
    if (!container || typeof experiments === 'undefined') {
        return;
    }

    const experimentCards = experiments.map(exp => `
        <div class="card">
            <h3>${exp.title}</h3>
            <p>${exp.description}</p>
            <p>${exp.status}</p>
            <div class="links">
                ${exp.links.live ? `<a href="${exp.links.live}" target="_blank">Live Demo</a>` : ''}
                ${exp.links.github ? `<a href="${exp.links.github}" target="_blank">GitHub</a>` : ''}
            </div>
        </div>
    `).join('');

    container.innerHTML = experimentCards;
}

function initializeTodoList() {
    const form = document.getElementById('todo-form');
    const input = document.getElementById('todo-input');
    const list = document.getElementById('todo-list');

    let todos = JSON.parse(localStorage.getItem('todos')) || [];

    const saveTodos = () => {
        localStorage.setItem('todos', JSON.stringify(todos));
    };

    const renderTodos = () => {
        list.innerHTML = '';
        todos.forEach((todo, index) => {
            const li = document.createElement('li');
            li.textContent = todo.text;
            if (todo.completed) {
                li.classList.add('completed');
            }

            li.addEventListener('click', () => {
                todos[index].completed = !todos[index].completed;
                saveTodos();
                renderTodos();
            });

            const deleteButton = document.createElement('button');
            deleteButton.textContent = 'Delete';
            deleteButton.addEventListener('click', (e) => {
                e.stopPropagation();
                todos.splice(index, 1);
                saveTodos();
                renderTodos();
            });

            li.appendChild(deleteButton);
            list.appendChild(li);
        });
    };

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const newTodoText = input.value.trim();
        if (newTodoText) {
            todos.push({ text: newTodoText, completed: false });
            input.value = '';
            saveTodos();
            renderTodos();
        }
    });

    renderTodos();
}

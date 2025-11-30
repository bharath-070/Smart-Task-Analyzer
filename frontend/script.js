// GLOBAL TASK STORAGE
let tasks = [];

/* -----------------------------
   ADD TASK MANUALLY
------------------------------ */
document.getElementById("addTaskBtn").onclick = () => {
    const title = document.getElementById("title").value.trim();
    const due = document.getElementById("due_date").value;
    const hours = parseFloat(document.getElementById("hours").value);
    const importance = parseInt(document.getElementById("importance").value);
    const deps = document.getElementById("dependencies").value
        .split(",")
        .map(x => x.trim())
        .filter(x => x !== "");

    if (!title) {
        alert("Title is required");
        return;
    }

    const newTask = {
        id: "t" + (tasks.length + 1),
        title,
        due_date: due || null,
        estimated_hours: isNaN(hours) ? 1 : hours,
        importance: isNaN(importance) ? 5 : importance,
        dependencies: deps
    };

    tasks.push(newTask);
    renderAddedTasks();

    alert("Task added!");
};


/* -----------------------------
   RENDER ADDED TASKS (LEFT PANEL)
------------------------------ */
function renderAddedTasks() {
    const box = document.getElementById("addedTasks");
    box.innerHTML = "";

    tasks.forEach(t => {
        const card = document.createElement("div");
        card.className = "task-card";

        card.innerHTML = `
            <div class="task-title">${t.title}</div>
            <div class="task-details">
                <strong>ID:</strong> ${t.id}<br>
                <strong>Due:</strong> ${t.due_date || "None"}<br>
                <strong>Effort:</strong> ${t.estimated_hours} hrs<br>
                <strong>Importance:</strong> ${t.importance}<br>
                <strong>Dependencies:</strong> ${t.dependencies.length ? t.dependencies.join(", ") : "None"}
            </div>
        `;

        box.appendChild(card);
    });
}


/* -----------------------------
   LOAD JSON INPUT
------------------------------ */
document.getElementById("loadJsonBtn").onclick = () => {
    const text = document.getElementById("jsonInput").value.trim();

    if (!text) {
        alert("Please paste valid JSON");
        return;
    }

    try {
        const parsed = JSON.parse(text);

        if (!Array.isArray(parsed)) {
            alert("JSON must be an array of tasks");
            return;
        }

        tasks = parsed;
        renderAddedTasks();
        alert("JSON loaded!");

    } catch (err) {
        alert("Invalid JSON");
    }
};


/* -----------------------------
   STRATEGY WEIGHTS
------------------------------ */
function getWeights(strategy) {
    if (strategy === "fast")
        return { urgency: 0.1, importance: 0.1, effort: 0.7, dependency: 0.1 };
    if (strategy === "impact")
        return { urgency: 0.1, importance: 0.8, effort: 0.05, dependency: 0.05 };
    if (strategy === "deadline")
        return { urgency: 0.8, importance: 0.1, effort: 0.05, dependency: 0.05 };

    return null; // smart balance
}


/* -----------------------------
   ANALYZE TASKS
------------------------------ */
document.getElementById("analyzeBtn").onclick = async () => {
    if (tasks.length === 0) {
        alert("No tasks to analyze");
        return;
    }

    // Always call backend for Smart Balance score
    const res = await fetch("http://localhost:8000/api/tasks/analyze/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tasks)
    });

    let analyzed = await res.json();

    // Apply strategy sorting
    const strategy = document.getElementById("strategySelect").value;

    if (strategy === "fast") {
        // Fastest Wins → lowest effort first
        analyzed.sort((a, b) => a.estimated_hours - b.estimated_hours);
    }

    else if (strategy === "impact") {
        // High Impact → highest importance first
        analyzed.sort((a, b) => b.importance - a.importance);
    }

    else if (strategy === "deadline") {
        // Deadline Driven → earliest due date first
        analyzed.sort((a, b) => {
            if (!a.due_date) return 1; 
            if (!b.due_date) return -1;
            return new Date(a.due_date) - new Date(b.due_date);
        });
    }

    // Smart Balance = default backend sorted order
    // No sorting needed

    renderAnalyzedTasks(analyzed);
    fetchSuggestions(analyzed);
};


/* -----------------------------
   RENDER ANALYZED TASKS (RIGHT PANEL)
------------------------------ */
function renderAnalyzedTasks(list) {
    const box = document.getElementById("results");
    box.innerHTML = "";

    list.forEach(t => {
        const level =
            t.score >= 15 ? "high" :
            t.score >= 8 ? "medium" :
            "low";

        const card = document.createElement("div");
        card.className = `task-card ${level}`;

        card.innerHTML = `
            <div class="task-title">${t.title}</div>
            <div class="task-details">
                <strong>Score:</strong> ${t.score}<br>
                <strong>Due:</strong> ${t.due_date || "None"}<br>
                <strong>Effort:</strong> ${t.estimated_hours} hrs<br>
                <strong>Importance:</strong> ${t.importance}<br>
                <strong>Dependencies:</strong> ${t.dependencies.length ? t.dependencies.join(", ") : "None"}
            </div>
        `;

        box.appendChild(card);
    });
}


/* -----------------------------
   FETCH SUGGESTIONS (TOP 3)
------------------------------ */
async function fetchSuggestions(list) {
    const url =
        "http://localhost:8000/api/tasks/suggest/?tasks=" +
        encodeURIComponent(JSON.stringify(list));

    const res = await fetch(url);
    const data = await res.json();

    const box = document.getElementById("suggested");
    box.innerHTML = "";

    data.forEach(t => {
        const card = document.createElement("div");
        card.className = "task-card high"; // suggestions always highlighted

        card.innerHTML = `
            <div class="task-title">${t.title}</div>
            <div class="task-details">
                <strong>Score:</strong> ${t.score}<br>
                <strong>Reason:</strong><br>
                ${t.explanation.map(e => "- " + e).join("<br>")}
            </div>
        `;

        box.appendChild(card);
    });
}

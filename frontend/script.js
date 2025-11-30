// FRONTEND LOGIC FOR SMART TASK ANALYZER

let tasks = [];

// Add task manually
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
    alert("Task added!");
};

// Load JSON input
document.getElementById("loadJsonBtn").onclick = () => {
    try {
        const json = JSON.parse(document.getElementById("jsonInput").value);
        tasks = json;
        alert("JSON loaded!");
    } catch (e) {
        alert("Invalid JSON");
    }
};

// Strategy → select weights
function getWeights(strategy) {
    if (strategy === "fast") {
        return { urgency: 0.1, importance: 0.1, effort: 0.7, dependency: 0.1 };
    }
    if (strategy === "impact") {
        return { urgency: 0.1, importance: 0.8, effort: 0.05, dependency: 0.05 };
    }
    if (strategy === "deadline") {
        return { urgency: 0.8, importance: 0.1, effort: 0.05, dependency: 0.05 };
    }
    return null; // smart balance (default backend weights)
}

// Analyze button
document.getElementById("analyzeBtn").onclick = async () => {
    if (tasks.length === 0) {
        alert("No tasks to analyze");
        return;
    }

    const strategy = document.getElementById("strategySelect").value;
    const weights = getWeights(strategy);

    let analyzeURL = "http://localhost:8000/api/tasks/analyze/";

    // Pass weights to backend via ?weights=...
    if (weights) {
        analyzeURL += "?weights=" + encodeURIComponent(JSON.stringify(weights));
    }

    const res = await fetch(analyzeURL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(tasks)
    });

    const data = await res.json();
    renderTasks(data);
    fetchSuggestions(data);
};

// Render analyzed tasks
function renderTasks(list) {
    const box = document.getElementById("results");
    box.innerHTML = "";

    list.forEach(t => {
        const level = t.score >= 15 ? "high" : t.score >= 8 ? "medium" : "low";

        const div = document.createElement("div");
        div.className = `task-card ${level}`;

        div.innerHTML = `
            <strong>${t.title}</strong> (Score: ${t.score})
            <br>Due: ${t.due_date || "None"}
            <br>Effort: ${t.estimated_hours} hrs
            <br>Importance: ${t.importance}
        `;

        box.appendChild(div);
    });
}

// Fetch suggestions
async function fetchSuggestions(fullList) {

    // Suggest endpoint expects tasks as query param
    const url = "http://localhost:8000/api/tasks/suggest/?tasks=" + encodeURIComponent(JSON.stringify(fullList));

    const res = await fetch(url);
    const data = await res.json();
    const box = document.getElementById("suggested");
    box.innerHTML = "";

    data.forEach(t => {
        const div = document.createElement("div");
        div.className = "task-card high"; // always highlight suggestions

        div.innerHTML = `
            <strong>${t.title}</strong>
            <br>Score: ${t.score}
            <div class="explanation">
                ${t.explanation.join("<br>")}
            </div>
        `;

        box.appendChild(div);
    });
}

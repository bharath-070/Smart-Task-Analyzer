async function analyzeTasks() {
    const taskInput = document.getElementById('taskInput').value;
    const tasks = JSON.parse(taskInput); // Convert text to JSON

    try {
        const response = await fetch('/api/tasks/analyze/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tasks) // Send data to Django
        });

        const sortedTasks = await response.json();
        displayResults(sortedTasks); // Custom function to show UI
    } catch (error) {
        console.error('Error:', error);
        alert("Failed to analyze tasks. Check your JSON format.");
    }
}
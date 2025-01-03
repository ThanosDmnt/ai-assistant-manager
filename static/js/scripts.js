document.addEventListener("DOMContentLoaded", () => {
    // Handle task form submission
    const taskForm = document.getElementById("task-form");
    if (taskForm) {
        taskForm.addEventListener("submit", async (event) => {
            event.preventDefault(); // Prevent the form from reloading the page

            const taskInput = document.getElementById("task-input").value;
            const taskResponse = document.getElementById("task-response");


            try {
                const response = await fetch("/process", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ user_input: taskInput }),
                });

                console.log(response);

                const result = await response.json();
                taskResponse.textContent = result.response;
                taskResponse.style.display = "block";
            } catch (error) {
                taskResponse.textContent = "An error occurred. Please try again.";
                taskResponse.style.display = "block";
                console.error("Error:", error);
            }
        });
    }

    // Handle event form submission
    const eventForm = document.getElementById("event-form");
    if (eventForm) {
        eventForm.addEventListener("submit", async (event) => {
            event.preventDefault(); // Prevent the form from reloading the page

            const eventInput = document.getElementById("event-input").value;
            const eventResponse = document.getElementById("event-response");

            try {
                const response = await fetch("/events", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ user_input: eventInput }),
                });

                const result = await response.json();
                eventResponse.textContent = result.response;
                eventResponse.style.display = "block";
            } catch (error) {
                eventResponse.textContent = "An error occurred. Please try again.";
                eventResponse.style.display = "block";
                console.error("Error:", error);
            }
        });
    }
});

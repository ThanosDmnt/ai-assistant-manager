document.addEventListener("DOMContentLoaded", () => {
    const userInput = document.getElementById("userInput");
    const submitButton = document.getElementById("submitButton");
    const charCount = document.getElementById("charCount");
    const responseContainer = document.getElementById("response");
    const tasksArea = document.querySelector(".tasksArea");
    const clearTasksButton = document.getElementById("clearTasksButton");

    // Function to fetch and display tasks
    function displayTasks() {
        fetch("/tasks")
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Failed to fetch tasks.");
                }
                return response.json();
            })
            .then((data) => {
                const taskList = document.createElement("ol");

                for (const [id, task] of Object.entries(data)) {
                    const listItem = document.createElement("li");

                    // Set task description
                    listItem.textContent = task.description;

                    // Add a strikethrough for completed tasks
                    if (task.completed) {
                        listItem.style.textDecoration = "line-through";
                        listItem.style.color = "gray";
                    }

                    taskList.appendChild(listItem);
                }

                // Clear any existing content and append the task list
                tasksArea.innerHTML = "";
                tasksArea.appendChild(taskList);
            })
            .catch((error) => {
                console.error("Error:", error);
                tasksArea.innerHTML = "<p>Failed to load tasks.</p>";
            });
    }

    // Call the displayTasks function to load and render tasks
    displayTasks();

    // Update character count as user types
    userInput.addEventListener("input", () => {
        const currentLength = userInput.value.length;
        charCount.textContent = `${currentLength}/100`;
    });

    // Handle submit button click
    submitButton.addEventListener("click", async () => {
        const userText = userInput.value.trim();
        modelResponse = "";

        if (userText === "") {
            return;
        }

        try {
            const response = await fetch("/process", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ user_input: userText }),
            });

            console.log(response);

            const result = await response.json();
            modelResponse = result.response;
            displayTasks();
        } catch (error) {
            modelResponse = "An error occurred. Please try again.";
            console.error("Error:", error);
        }

        // Clear the input field
        userInput.value = "";
        charCount.textContent = "0/100";

        // Simulate a chatbot response with typing animation
        setTimeout(() => {
            animateTyping(modelResponse);
        }, 1000); // 1-second delay
    });

    // Typing animation function
    function animateTyping(text) {
        let index = 0;
        responseContainer.textContent = ""; // Clear previous content
        submitButton.disabled = true;
        submitButton.style.opacity = 0.5;

        const interval = setInterval(() => {
            if (index < text.length) {
                responseContainer.textContent += text[index];
                index++;
            } else {
                submitButton.disabled = false;
                submitButton.style.opacity = 1;
                clearInterval(interval); // Stop animation when text is fully displayed
            }
        }, 50); // Adjust the speed of typing (in milliseconds)
    }


    // Handle clear tasks button click
    clearTasksButton.addEventListener("click", async () => {
        try {
            const response = await fetch("/clear-tasks", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
            });
    
            if (response.ok) {
                const result = await response.json();
                console.log(result);
                // Refresh the tasks displayed on the page
                tasksArea.innerHTML = "<p>No tasks available.</p>";
            } else {
                console.error("Failed to clear tasks. Please try again.");
            }
        } catch (error) {
            console.error("Error clearing tasks:", error);
        }
    });
});


document.addEventListener("DOMContentLoaded", () => {
    // Handle user's submission
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


    const userInput = document.getElementById("userInput");
    const submitButton = document.getElementById("submitButton");
    const charCount = document.getElementById("charCount");
    const responseContainer = document.getElementById("response");

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
});

# AI Assistant Manager

An AI-powered application designed to assist users with task management and scheduling using GPT-3.5, Google Calendar API, and a dynamic front-end interface.

## Table of Contents
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features
- **Task Management:** Add, delete, get help, and clear tasks dynamically.
- **Scheduling Integration:** Interact with Google Calendar for event management.
- **Conversational Interface:** Engage with the AI chatbot for a seamless experience.
- **Dynamic Front-End:** Real-time updates and interactive UI components.

## Technologies Used
- **Back-End:** Flask, OpenAI GPT-3.5
- **Front-End:** HTML, CSS, JavaScript
- **APIs:** Google Calendar API
- **Other Tools:** Python, dotenv, OAuth2

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/ThanosDmnt/ai-assistant-manager.git
   cd ai-assistant-manager
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your environment variables:
   - Create a `.env` file in the root directory.
   - Add your OpenAI API key and Google API credentials:
     ```
     OPENAI_API_KEY=your-openai-api-key
     GOOGLE_API_CREDENTIALS_PATH=your-client-secret
     ```
4. Run the application:
   ```bash
   python app.py
   ```

## Usage
1. Navigate to `http://localhost:5000` in your browser.
2. Interact with the chatbot to:
   - Add, delete and get step-by-step instructions for your tasks.
   - Manage schedules with Google Calendar.
3. View responses dynamically in the chat interface.

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add a new feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgments
- [OpenAI](https://openai.com) for the GPT-3.5 API.
- [Google](https://developers.google.com/calendar) for the Calendar API.
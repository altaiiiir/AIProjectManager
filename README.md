# AI Project Manager

## Overview

The AI Project Manager is a Streamlit application designed to generate Agile user stories based on a project idea and tech stack. The application uses OpenAI's GPT model to create structured user stories and automatically upload them as issues to GitHub.

## Features

- Generate Agile user stories in JSON format.
- Automatically create GitHub issues from the generated user stories.
- Easy-to-use interface for entering project details.

## Technologies Used

- **Python** (v3.11)
- **Streamlit** for the web interface
- **LangChain** for interacting with OpenAI's API
- **Pydantic** for data validation
- **Requests** for making HTTP requests
- **GitHub API** for issue management

## Getting Started

### Prerequisites

- Python 3.11 installed
- A GitHub account
- A GitHub repository where issues will be created
- A GitHub personal access token with repo permissions
- An OpenAI account with an access token

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/altaiiiir/AIProjectManager.git
   cd AIProjectManager
2. Setup your Github and OpenAI API Keys:
   ```bash
   export GITHUB_API_KEY='your_personal_access_token'
   export OPENAI_API_KEY='your_personal_access_token'
3. Install required packages:
   ```bash
   pip install -r requirements.txt
4. Run the streamlit app locally:
   ```bash
   ./run_streamlit.py
   
### Notes:
- Replace `repo` in the code with your username and repo you want to create issues in. For example: `repo = "example_user_name/example_repo"`
- Update the contact email at the end.
- You can modify any sections to better fit your project or add additional details as needed.

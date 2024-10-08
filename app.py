import os
import requests
import streamlit as st
from langchain.schema import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

# Initialize OpenAI client
client = ChatOpenAI(model="gpt-3.5-turbo")


# Define data models
class Task(BaseModel):
    """Model representing a task."""
    task: str


class UserStory(BaseModel):
    """Model representing a user story."""
    title: str
    description: str
    implementation_suggestion: str
    tasks: list[Task]


class UserStoriesResponse(BaseModel):
    """Model representing a response containing user stories."""
    user_stories: list[UserStory]


def create_prompt(project_idea: str, tech_stack: str) -> str:
    """Creates a prompt for generating user stories based on project idea and tech stack."""
    return (
        f"Based on the project idea: '{project_idea}', and using any/all technologies/frameworks included within the tech stack: {tech_stack}, "
        "please provide unique Agile user stories for each component of the project, ensuring that each user story is broken down into manageable tasks that are small, specific, and suitable for individual GitHub issues."
        "If the tech stack includes a broad platform or service (like AWS, Azure, GCP), consider the appropriate services (e.g., AWS Lambda, Step Functions, Bedrock, etc.), Python libraries, or frameworks that align with the project’s context and best practices without explicitly forcing their use."
        "Where applicable, naturally incorporate relevant cloud services, libraries, or frameworks that would help accomplish the task efficiently."
        "If a task contains multiple actions or steps, further break it down into sub-tasks with detailed explanations."
        "The output should be in JSON format with the following structure:\n"
        "{\n"
        '  "user_stories": [\n'
        '    {\n'
        '      "title": "[Title of the user story, must be descriptive and concise. Must not start with As a user, ]",\n'
        '      "description": "GIVEN [context]. WHEN[event].THEN [outcome].",\n'
        '      "implementation_suggestion": "[How this could be implemented, considering relevant services and libraries without explicitly dictating them]",\n'
        '      "tasks": [\n'
        '        {"task": "[Detailed numbered steps using markdown, ensuring each task is granular and focused on a single action]"},\n'
        '        {"task": "[Task 2 with additional breakdowns if necessary, implicitly considering relevant services]"}\n'
        '      ]\n'
        '    }\n'
        '  ]\n'
        "}\n\n"
        "**Ensure the JSON is valid and properly formatted. Each task should be specific enough to be a GitHub issue. Break down tasks into smaller sub-tasks if necessary, and naturally incorporate relevant services and libraries where applicable.**\n\n"
        "Start generating the user stories now:"
    )


def generate_tasks(project_idea: str, tech_stack: str) -> str:
    """Generates tasks using OpenAI based on the provided project idea and tech stack."""
    prompt = create_prompt(project_idea, tech_stack)
    messages = [
        SystemMessage(content="You are an experienced Project Manager and Agile coach tasked with generating user "
                              "stories."),
        HumanMessage(content=prompt)
    ]
    response = client(messages)
    return response.content


def create_github_issue(repo: str, title: str, body: str, token: str) -> dict:
    """Creates a GitHub issue with the specified title and body."""
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    issue = {"title": title, "body": body}
    response = requests.post(url, json=issue, headers=headers)

    if response.status_code != 201:
        raise Exception(f"GitHub API error: {response.status_code} - {response.json().get('message', 'Unknown error')}")
    return response.json()


def parse_generated_output(generated_output: str) -> UserStoriesResponse:
    """Cleans and parses the generated output into UserStoriesResponse."""
    cleaned_output = generated_output.split('```json')[-1].strip('` \n')
    return UserStoriesResponse.parse_raw(cleaned_output)


def format_issue_body(story: UserStory) -> str:
    """Formats the issue body from a user story."""
    tasks = "\n".join(f"- {task.task}" for task in story.tasks)
    return (
        f"**Description:** {story.description.strip()}\n\n"
        f"**Implementation Suggestion:** {story.implementation_suggestion.strip()}\n\n"
        f"**Tasks:**\n{tasks}"
    )


# Streamlit UI
st.title("AI Project Management Assistant")
st.write("Enter your project details below:")

# Input fields for project idea and tech stack
project_idea = st.text_input("Project Idea")
tech_stack = st.text_input("Tech Stack (e.g., Python, AWS, GitHub)")
REPO = "altaiiiir/test"
GITHUB_TOKEN = os.environ.get("GITHUB_API_KEY")
if not GITHUB_TOKEN:
    st.error("GitHub API key not found in environment variables.")

# Generate button
if st.button("Generate and Upload"):
    if project_idea and tech_stack:
        with st.spinner("Generating stories and tasks..."):
            generated_output = generate_tasks(project_idea, tech_stack)
            st.success("Generation Complete!")

            # Parse the JSON response
            try:
                user_stories_response = parse_generated_output(generated_output)
                for story in user_stories_response.user_stories:
                    title = story.title.strip()
                    body = format_issue_body(story)

                    # Create GitHub issue
                    create_response = create_github_issue(REPO, title, body, GITHUB_TOKEN)
                    if 'id' in create_response:
                        st.success(f"Issue created: {create_response['html_url']}")
                    else:
                        st.error(f"Error creating issue: {create_response.get('message', 'Unknown error')}")
            except Exception as e:
                st.error(f"Failed to parse JSON response. Error: {str(e)}")
    else:
        st.error("Please fill in all fields.")

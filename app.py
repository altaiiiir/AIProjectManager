import os

import streamlit as st
import requests
from pydantic import BaseModel
from openai import OpenAI

client = OpenAI()


# Define data models
class Task(BaseModel):
    task: str


class UserStory(BaseModel):
    title: str
    description: str
    implementation_suggestion: str
    tasks: list[Task]


class UserStoriesResponse(BaseModel):
    user_stories: list[UserStory]


# Function to generate user stories using OpenAI
def generate_tasks(project_idea, tech_stack):
    prompt = create_prompt(project_idea, tech_stack)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an experienced Agile coach tasked with generating user stories."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.7,
        top_p=1.0,
        n=1,
        stop=None
    )
    return response.choices[0].message.content


# Helper function to create the prompt
def create_prompt(project_idea, tech_stack):
    return (
        f"Based on the project idea: '{project_idea}', and using the tech stack: {tech_stack}, "
        "please provide 3 unique Agile user stories in JSON format with the following structure:\n"
        "{\n"
        '  "user_stories": [\n'
        '    {\n'
        '      "title": "[Title of the user story]",\n'
        '      "description": "Given [context], when [event], then [outcome].",\n'
        '      "implementation_suggestion": "[How this could be implemented]",\n'
        '      "tasks": [\n'
        '        {"task": "[Task 1]"},\n'
        '        {"task": "[Task 2]"}\n'
        '      ]\n'
        '    }\n'
        '  ]\n'
        "}\n\n"
        "**Ensure the JSON is valid and properly formatted.**\n\n"
        "Start generating the user stories now:"
    )


# Function to create a GitHub issue
def create_github_issue(repo, title, body, token):
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    issue = {"title": title, "body": body}
    return requests.post(url, json=issue, headers=headers).json()


# Function to clean and parse the generated output
def parse_generated_output(generated_output):
    cleaned_output = generated_output.split('```json')[-1].strip('` \n')
    return UserStoriesResponse.parse_raw(cleaned_output)


# Function to format the issue body from user story
def format_issue_body(story):
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
repo = "altaiiiir/test"
token = os.environ["GITHUB_API_KEY"]

# Generate button
if st.button("Generate and Upload"):
    if project_idea and tech_stack:
        with st.spinner("Generating stories and tasks..."):
            generated_output = generate_tasks(project_idea, tech_stack)
            st.success("Generation Complete!")
            #st.write("Raw Output:", generated_output)  # Debugging line

            # Parse the JSON response
            try:
                user_stories_response = parse_generated_output(generated_output)
                for story in user_stories_response.user_stories:
                    title = story.title.strip()
                    body = format_issue_body(story)

                    # Create GitHub issue
                    create_response = create_github_issue(repo, title, body, token)
                    if 'id' in create_response:
                        st.success(f"Issue created: {create_response['html_url']}")
                    else:
                        st.error(f"Error creating issue: {create_response.get('message', 'Unknown error')}")
            except Exception as e:
                st.error(f"Failed to parse JSON response. Error: {str(e)}")
    else:
        st.error("Please fill in all fields.")

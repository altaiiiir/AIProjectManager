import subprocess


def main():
    # Define the path to your Streamlit app
    streamlit_app_path = 'app.py'  # Adjust if your app has a different name

    # Run the Streamlit app
    subprocess.run(["streamlit", "run", streamlit_app_path])


if __name__ == '__main__':
    main()

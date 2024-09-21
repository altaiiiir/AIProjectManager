import subprocess


def main():
    streamlit_app_path = 'app.py' 

    # Run the Streamlit app
    subprocess.run(["streamlit", "run", streamlit_app_path])


if __name__ == '__main__':
    main()

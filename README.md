# Compressor Acceleration Analysis Dashboard

An interactive Python-based web application for high-fidelity vibration signal processing, FFT diagnostics, and CSV data export.

This dashboard is built using **Streamlit** and **Plotly** and can be deployed directly to the web via **Streamlit Community Cloud** linked with a **GitHub** repository.

---

## Workspace Files

*   `streamlit_app.py`: The core Streamlit web application.
*   `requirements.txt`: Package dependency definitions.
*   `TVN6_0124_1822_50deg_Time.csv`: Time-domain vibration acceleration data (for analysis).
*   `Compressor_Acceleration_Analysis.html`: Local standalone HTML version of the dashboard.
*   `run_dashboard.py`: Local Python server launcher for the HTML dashboard.

---

## Local Execution Instructions

To run the Streamlit app locally on your machine:

1.  **Open a terminal** in the project directory:
    ```bash
    cd d:/01_Python_Code/30_Antigravity/04_FFT
    ```
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Launch the Streamlit app**:
    ```bash
    streamlit run streamlit_app.py
    ```
4.  Your browser will automatically open the application at `http://localhost:8501`.
5.  Upload the data file `TVN6_0124_1822_50deg_Time.csv` using the file uploader in the sidebar.

---

## GitHub & Streamlit Community Cloud Deployment Guide

Follow these steps to host your application online so anyone can access it:

### Step 1: Create a GitHub Repository
1.  Go to [GitHub](https://github.com/) and log in (or sign up for a free account).
2.  Click **New** to create a new repository.
3.  Name your repository (e.g., `compressor-acceleration-analysis`).
4.  Choose **Public** and do **NOT** initialize it with a README, `.gitignore`, or license.
5.  Click **Create repository**.
6.  Copy the remote repository URL (looks like `https://github.com/your-username/compressor-acceleration-analysis.git`).

### Step 2: Push the Local Code to GitHub
Open your terminal in the workspace directory and execute the following Git commands:

1.  **Initialize Git**:
    ```bash
    git init -b main
    ```
2.  **Create a `.gitignore` file** to prevent uploading heavy data files or python cache:
    Create a file named `.gitignore` in this folder and add:
    ```text
    __pycache__/
    *.pyc
    .streamlit/
    .ipynb_checkpoints/
    ```
    *(Note: If you wish to upload the 2.8MB CSV file `TVN6_0124_1822_50deg_Time.csv` so it is already in the repository, you can skip adding it to gitignore. If you want to keep the repository lightweight, you can add `*.csv` to gitignore.)*
3.  **Stage all project files**:
    ```bash
    git add streamlit_app.py requirements.txt README.md .gitignore run_dashboard.py Compressor_Acceleration_Analysis.html TVN6_0124_1822_50deg_Time.csv
    ```
4.  **Commit the files**:
    ```bash
    git commit -m "Initialize Compressor Acceleration Analysis Streamlit application"
    ```
5.  **Link to GitHub and Push**:
    *(Replace the URL below with your actual copied GitHub repository URL)*
    ```bash
    git remote add origin https://github.com/your-username/compressor-acceleration-analysis.git
    git push -u origin main
    ```

### Step 3: Deploy to Streamlit Community Cloud
1.  Go to [Streamlit Community Cloud](https://share.streamlit.io/) and click **Sign up** or **Sign in** (choose **Continue with GitHub** to link accounts).
2.  Once logged in, click **Create app** (or **New app**) in the top right corner.
3.  Fill out the deployment form:
    *   **Repository**: Select your newly created repository (e.g., `your-username/compressor-acceleration-analysis`).
    *   **Branch**: Select `main`.
    *   **Main file path**: Set this to `streamlit_app.py`.
4.  Click **Deploy!**
5.  Streamlit will allocate resources, install the dependencies listed in `requirements.txt`, and boot up your app. This takes about 1-2 minutes.
6.  Once deployed, your app will be live at a URL like `https://compressor-acceleration-analysis.streamlit.app/`.

You can now open that public URL from any computer or mobile device, upload your local `TVN6_0124_1822_50deg_Time.csv` file, and interact with the diagnostics charts in real-time!

# Weathora <!-- omit in toc -->

A simple Python CLI tool to fetch live weather data from any city using the OpenWeather API.

## Table of Contents <!-- omit in toc -->

- [Installation](#installation)
  - [Create and activate a virtual environment:](#create-and-activate-a-virtual-environment)
- [Setup API Key 🔑](#setup-api-key-)
  - [Step 1: Create an Account](#step-1-create-an-account)
  - [Step 2: Get Your API Key](#step-2-get-your-api-key)
  - [Step 3: Store the API Key](#step-3-store-the-api-key)
    - [🔹 PowerShell](#-powershell)
    - [🔹Bash](#bash)
- [Usage](#usage)
  - [Command Line Usage](#command-line-usage)

---

## Installation

-   Clone the repository:

    ```bash
    git clone https://github.com/bhatishan2003/weathora
    cd weathora
    ```

### Create and activate a virtual environment:

1. **Create a Virtual Environment [Optional, but recommended]**

    Run the following command to create a [virtual environment](https://docs.python.org/3/library/venv.html):

    ```bash
    python3 -m venv .venv
    ```

-   **Activate:**

    -   **Windows (PowerShell):**

        ```bash
        .venv\Scripts\activate
        ```

    -   **Linux/Mac (Bash):**

        ```bash
        source .venv/bin/activate
        ```

-   **Deactivate:**

    ```bash
    deactivate
    ```

-   **Install the package:**

    ```bash
    pip install .
    ```

-   **For development (editable mode):**

    ```bash
    pip install -e .
    ```

## Setup API Key 🔑

To use this project, you’ll need an API key from **OpenWeather**.

### Step 1: Create an Account

1. Go to [OpenWeather API](https://home.openweathermap.org/).
2. Sign up (or log in if you already have an account).

### Step 2: Get Your API Key

1. Navigate to your **API Keys** section in the OpenWeather dashboard.
2. Copy your **API Key**.

### Step 3: Store the API Key

Depending on your shell, use one of the following commands:

#### 🔹 PowerShell

```powershell
$Env:OPENWEATHER_API_KEY = "YOUR_SECRET_KEY"
```

#### 🔹Bash

```bash
export OPENWEATHER_API_KEY="YOUR_SECRET_KEY"
```

## Usage

### Command Line Usage

-   Following commands should be entered to get weather information.

    ```powershell
    weathora --city "Delhi"
    weathora --city "London"
    weathora --city "Jammu"
    ```

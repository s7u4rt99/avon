# avon

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#usage)

## Getting Started

These instructions will help you get the project up and running on your local machine.

### Prerequisites

- Python (version specified in `requirements.txt`)
- Virtual environment tool (e.g., `venv` or `virtualenv`)
- Git (for cloning the repository)

### Setup

- Create and activate a virtual environment:

  - Using venv (recommended):

    ```bash
    python -m venv venv
    source venv/bin/activate # On Linux/macOS
    venv\Scripts\activate # On Windows
    ```

  - Using virtualenv:

    ```bash
    virtualenv venv
    source venv/bin/activate # On Linux/macOS
    venv\Scripts\activate # On Windows
    ```

- Install the project dependencies:

  ```bash
  pip3 install -r requirements.txt
  ```

## Usage

Explain how to run or use your project here.

If you installed more dependencies in python, run the code below to update `requirements.txt`.

```bash
pip3 freeze > requirements.txt
```


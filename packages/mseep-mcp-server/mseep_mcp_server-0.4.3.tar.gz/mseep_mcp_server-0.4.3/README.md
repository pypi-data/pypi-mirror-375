# GitHub MCP Server

## Overview

GitHub MCP Server is an API-based tool that interacts with GitHub using the [MCP (Modular Command Processor)](https://github.com/mcp-framework) framework. It provides various functionalities, including fetching user details, repository information, and authenticated user data using GitHub's REST API.

This project is built using Python and leverages `httpx` for asynchronous API calls. It also uses `dotenv` for secure handling of GitHub authentication tokens.

## Features

- Fetch GitHub user information by username.
- Retrieve details of a GitHub repository.
- Get authenticated user details using a GitHub personal access token.
- Utilizes `FastMCP` for modular command processing.

## Project Structure
```bash
D:/MCP_Project/ 
|----.env
│----.gitignore
│----claude_desktop_config.json  (Create this file in C:\Users\your_username\AppData\Roaming\Claude\)
│----main.py
│----pyproject.toml
│----README.md
│----requirements.txt
```

<br>

- `main.py`: Core logic of the GitHub MCP Server.
- `.env`: Stores environment variables (e.g., GitHub Token).
- `claude_desktop_config.json`: Configuration for running the MCP Server.
- `requirements.txt`: Lists required dependencies.
- `explanation_video.mp4`: A video explaining the project.

## Setup Instructions

### Prerequisites

- Python >=3.10
- GitHub personal access token (for authenticated requests)
- `conda` or `venv` for virtual environment management

### Setup and Usage

1. **Clone the Repository**
   ```bash
   git clone https://github.com/DivyanshKushwaha/GitHub-MCP-Server-Claude.git
   cd GitHub-MCP-Server-Claude
   ```
2. **Create Python environment**
```bash 
python -m venv venv
source venv/bin/activate  
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Set Up Environment Variables (Create .env file)**
```bash
GITHUB_TOKEN=your_personal_access_token
```

5. **Setup claude_desktop_config.json**

```bash
{
    "mcpServers": {
        "MCP_Server": {
            "command": "my_env/Scripts/uv",
            "args": [
                "run",
                "D:/MCP_Project/main.py"
            ]
        }
    }
}
```

- The command key specifies the path to the uv script located in the conda environment. This is used to run the server.

- The args key provides additional arguments for the uv script:

    - "run": Indicates the action to run the server.
    - my_env : python environment 'my_env'
    - "D:/MCP_Project/main.py": Specifies the path to the main.py script, which contains the implementation of the MCP server.


6. **Launch the Claude Desktop Application**
- Open the Claude Desktop Application. 
- It will use the MCP Server as configured in the claude_desktop_config.json file to fetch and process data.
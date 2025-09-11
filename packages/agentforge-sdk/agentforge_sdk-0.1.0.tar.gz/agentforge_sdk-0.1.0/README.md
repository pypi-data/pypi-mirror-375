# AgentForge SDK

[![PyPI version](https://badge.fury.io/py/agentforge-sdk.svg)](https://badge.fury.io/py/agentforge-sdk)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Welcome to the official Software Development Kit (SDK) for **AgentForge**, the next-generation platform for building, deploying, and monetizing AI agents. This SDK provides the essential tools and command-line interface (CLI) to create powerful plugins that extend the capabilities of any agent on the AgentForge platform.

## What is AgentForge?

AgentForge is a platform that empowers users to create dynamic, interactive AI agents without needing to code. Instead of static workflows, agents are customized with powerful plugins created by developers like you. This SDK is your entry point into the AgentForge ecosystem, allowing you to build and distribute your tools to thousands of users.

## Features of the SDK

- **Simple and Intuitive Base Classes**: Inherit from `BaseTool` to create your tools with a clear and simple structure.
- **Secure Configuration Access**: Safely access user-provided configurations (like API keys) via the `ToolContext`.
- **Powerful CLI (`ag-cli`)**: A command-line tool to initialize, validate, and package your plugin for upload.
- **Standardized Manifest**: A simple `agentforge.json` file to define your plugin's metadata, tools, and dependencies.

## Getting Started

### 1. Installation

The AgentForge SDK is available on PyPI. You can install it using pip:

```bash
pip install agentforge-sdk
```

This will also install the `ag-cli` command-line tool.

### 2. Initializing a New Plugin

To start a new plugin project, navigate to your desired directory and run the `init` command:

```bash
ag-cli init my-awesome-plugin
```

This will create a new directory named `my-awesome-plugin` with the following structure:

```
my-awesome-plugin/
├── agentforge.json      # Your plugin's manifest file
└── tools/
    ├── __init__.py
    └── sample_tool.py   # An example tool to get you started
```

### 3. Developing Your Tool

Open `tools/sample_tool.py` to see the basic structure of a tool. Every tool must inherit from `BaseTool` and implement the `run` method.

```python
# in tools/sample_tool.py
from agentforge_sdk.base import BaseTool, ToolContext

class SampleTool(BaseTool):
    def __init__(self, context: ToolContext):
        super().__init__(context)
        # You can access user-defined configurations here
        # For example, if you defined a config "api_key" in your manifest:
        # self.api_key = self.context.get_config("api_key")

    def run(self, **kwargs) -> str:
        # The LLM will provide arguments based on the user's prompt
        # and the parameters defined in your manifest.
        location = kwargs.get("location", "world")

        if not location:
            return "Error: Location was not provided."

        # Your tool's logic goes here
        return f"Hello, {location}! The weather is sunny."
```

### 4. Configuring the Manifest

The `agentforge.json` file is the heart of your plugin. It tells the AgentForge platform everything it needs to know about your plugin, including its name, description, tools, and dependencies.

Make sure to edit this file to match your plugin's details. The `entrypoint` for each tool should point to your class in the format `module.path:ClassName`.

### 5. Validating and Packaging

Before you can upload your plugin, you should validate its manifest:

```bash
# Navigate into your plugin's root directory
cd my-awesome-plugin

ag-cli validate
```

If the validation is successful, you can package your plugin into a `.afp` file. This file contains all your code and is ready for upload.

```bash
ag-cli package
```

This will create a file like `My_Awesome_Plugin-v1.0.0.afp` in your current directory. You can now upload this file through the AgentForge developer dashboard.

## Contributing

We welcome contributions to the AgentForge SDK! If you have ideas for new features, bug fixes, or improvements, please feel free to open an issue or submit a pull request on our GitHub repository. (Link to be added)

## License

This SDK is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
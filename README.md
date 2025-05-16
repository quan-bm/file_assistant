File Assistant
---
Read and modify your files with the help of an AI assistant.

The program uses Local MCP server with Azure OpenAI API to interact with your files.

https://github.com/user-attachments/assets/2050bbf4-860f-42e7-8abf-1614e43369b8

# Usage
```bash
> python main.py -h   
usage: fa [-h] {setup,start} ...

Read and modify your files with the help of an AI assistant.

options:
  -h, --help     show this help message and exit

commands:
  {setup,start}
    setup        Setup program variables
    start        Start the program
```

Example of listing files in the specified directory:
```bash
> python main.py start
Please specify the working directory: /your/folder/in/absolute/path
Working directory set to: '/your/folder/in/absolute/path'
Secure MCP Filesystem Server running on stdio
Allowed directories: [ '/your/folder/in/absolute/path' ]

(Say 'thank you' to exit)
Your message: list the file names in the current folder
AI response: In the current folder, the following files are present:

- 001_Favorite_Sports.txt
- 002_Books_about_AI.txt
- 003_How_to_Grow_Trees.txt
```



# Installation
## Requirements
1. `Python` >= 3.12
2. `npx` >= 10.2
3. A model deployment on Azure OpenAI (or Azure AI Foundry)

## Setup
Run the following command to setup your program:

```bash
> python main.py setup
Please provide the endpoint for your model: https://your-endpoint.cognitiveservices.azure.com/
Please provide the API version (default: '2024-12-01-preview'): 
Please provide the name of the deployment: gpt-4o-mini
Please provide your API key: 
Please provide the model name: gpt-4o-mini
Setup successfully!
```

# Todos

- [ ] Add OpenAI API support
- [ ] Add conversation history when interacting with the assistant

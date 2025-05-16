import sys
import asyncio
import os
import shutil
import argparse
import getpass
from dotenv import load_dotenv
from mcp import McpError
from openai import AsyncAzureOpenAI
from agents import Agent, Runner, ModelProvider, Model, OpenAIChatCompletionsModel, \
    RunConfig, ModelSettings, set_tracing_disabled
from agents.mcp import MCPServer, MCPServerStdio

set_tracing_disabled(disabled=True)
load_dotenv()


client = AsyncAzureOpenAI(
    api_version=os.environ.get("AOAI_API_VERSION"),
    azure_endpoint=os.environ.get("AOAI_ENDPOINT"),
    azure_deployment=os.environ.get("AOAI_DEPLOYMENT"),
    api_key=os.environ.get("AOAI_API_KEY"),
)


class AzureOpenAIModelProvider(ModelProvider):
    def get_model(self, model_name: str | None) -> Model:
        return OpenAIChatCompletionsModel(model=model_name or os.environ.get("AOAI_MODEL_NAME"),
                                          openai_client=client)
        
def ai_print(message: str):
    print(f"AI response: {message}")


async def run(mcp_server: MCPServer):
    agent = Agent(
        name="Assistant",
        instructions="""Use the tools to read the files in the given directory, 
answer questions based on those files, 
and interact with the files following the user's command.
""",
        mcp_servers=[mcp_server],
    )

    run_config = RunConfig(model_provider=AzureOpenAIModelProvider(),
                           model_settings=ModelSettings(
                               temperature=0.9, max_tokens=1000),
                           )
    print("\n(Say 'thank you' to exit)")
    while True:
        user_input = input("Your message: ")
        message = user_input.strip()
        if message == "thank you":
            ai_print("Goodbye!")
            break

        result = await Runner.run(starting_agent=agent, input=message,
                                  run_config=run_config)

        ai_print(f"{result.final_output}\n\n")


async def main():
    workdir = input("Please specify the working directory: ")
    print(f"Working directory set to: '{workdir}'")

    async with MCPServerStdio(
            name="Filesystem Server, via npx",
            params={
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    workdir
                ],
            },
    ) as server:
        await run(server)


def start(args):
    try:
        asyncio.run(main())
    except McpError as e:
        ai_print("I cannot access the specified directory. Please check and try again.")
        sys.exit(2)
    except Exception as e:
        ai_print(f"An error occurred, please try again. Error: {e}")
        sys.exit(2)


def setup(args):
    default_api_version = "2024-12-01-preview"
    endpoint = None
    api_version = None
    deployment = None
    platform = "azure" # input("Please specify your AI platform ('openai' or 'azure'): ")
    if platform == "openai":
        pass
    elif platform == "azure":
        endpoint = input("Please provide the endpoint for your model: ")
        api_version = input(
            f"Please provide the API version (default: '{default_api_version}'): ")
        deployment = input("Please provide the name of the deployment: ")
    else:
        raise ValueError("Invalid platform. Please try again.")
    api_key = getpass.getpass("Please provide your API key: ")
    model_name = input("Please provide the model name: ")

    file_content = f"""
AI_PLATFORM={platform or ''}
API_VERSION={api_version or default_api_version}
API_KEY={api_key or ''}
AOAI_ENDPOINT={endpoint or ''}
AOAI_DEPLOYMENT={deployment or ''}
MODEL_NAME={model_name or ''}
""".strip()

    env_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(env_dir, ".env")
    with open(env_path, "w") as file:
        file.write(file_content)

    print("Setup successfully!")
    sys.exit(0)


if __name__ == "__main__":
    # Make sure the user has `npx` installed
    if not shutil.which("npx"):
        raise RuntimeError(
            "npx is not installed. Please install it with `npm install -g npx`.")

    parser = argparse.ArgumentParser(
        prog="fa",
        description="Read and modify your files with the help of an AI assistant.",
    )
    commands = parser.add_subparsers(title="commands")
    setup_cmd = commands.add_parser("setup", help="Setup program variables")
    setup_cmd.set_defaults(func=setup)
    start_cmd = commands.add_parser("start", help="Start the program")
    start_cmd.set_defaults(func=start)
    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as e:
        parser.print_help()

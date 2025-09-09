import asyncio
import subprocess

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

# Store notes as a simple key-value dict to demonstrate state management
notes: dict[str, str] = {}

server = Server("mcp-server-macos-defaults")

# @server.list_resources()
# async def handle_list_resources() -> list[types.Resource]:
#     """
#     List available note resources.
#     Each note is exposed as a resource with a custom note:// URI scheme.
#     """
#     return [
#         types.Resource(
#             uri=AnyUrl(f"note://internal/{name}"),
#             name=f"Note: {name}",
#             description=f"A simple note named {name}",
#             mimeType="text/plain",
#         )
#         for name in notes
#     ]
#
# @server.read_resource()
# async def handle_read_resource(uri: AnyUrl) -> str:
#     """
#     Read a specific note's content by its URI.
#     The note name is extracted from the URI host component.
#     """
#     if uri.scheme != "note":
#         raise ValueError(f"Unsupported URI scheme: {uri.scheme}")
#
#     name = uri.path
#     if name is not None:
#         name = name.lstrip("/")
#         return notes[name]
#     raise ValueError(f"Note not found: {name}")
#
# @server.list_prompts()
# async def handle_list_prompts() -> list[types.Prompt]:
#     """
#     List available prompts.
#     Each prompt can have optional arguments to customize its behavior.
#     """
#     return [
#         types.Prompt(
#             name="summarize-notes",
#             description="Creates a summary of all notes",
#             arguments=[
#                 types.PromptArgument(
#                     name="style",
#                     description="Style of the summary (brief/detailed)",
#                     required=False,
#                 )
#             ],
#         )
#     ]
#
# @server.get_prompt()
# async def handle_get_prompt(
#     name: str, arguments: dict[str, str] | None
# ) -> types.GetPromptResult:
#     """
#     Generate a prompt by combining arguments with server state.
#     The prompt includes all current notes and can be customized via arguments.
#     """
#     if name != "summarize-notes":
#         raise ValueError(f"Unknown prompt: {name}")
#
#     style = (arguments or {}).get("style", "brief")
#     detail_prompt = " Give extensive details." if style == "detailed" else ""
#
#     return types.GetPromptResult(
#         description="Summarize the current notes",
#         messages=[
#             types.PromptMessage(
#                 role="user",
#                 content=types.TextContent(
#                     type="text",
#                     text=f"Here are the current notes to summarize:{detail_prompt}\n\n"
#                     + "\n".join(
#                         f"- {name}: {content}"
#                         for name, content in notes.items()
#                     ),
#                 ),
#             )
#         ],
#     )

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    return [
        types.Tool(
            name="list-domains",
            description="List all available macOS domains, same as `defaults domains`",
            inputSchema= {
                "type": "object",
                "properties": {},
            }, # TODO filter domains?
        ),
        types.Tool(
            name="find",
            description="Find entries container given word",
            inputSchema= {
                "type": "object",
                "properties": {
                    "word": {
                        "type": "string",
                        "description": "Word to search for",
                    },
                },
            },
        ),
        # defaults read <domain> <key> # key is optional, domain required
        types.Tool(
            name="defaults-read",
            description = "use the `defaults read <domain> <key>` command",
            inputSchema = {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain to read from",
                    },
                    "key": {
                        "type": "string",
                        "description": "Key to read from",
                    },
                },
                "required": ["domain"],
            },
        ),
        # defaults write <domain> <key> <value>
        types.Tool(
            name="defaults-write",
            description = "use the `defaults write <domain> <key> <value>` command",
            inputSchema = {
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Domain to write to",
                    },
                    "key": {
                        "type": "string",
                        "description": "Key to write to",
                    },
                    "value": {
                        "type": "string",
                        "description": "Value to write",
                    },
                },
                "required": ["domain", "key", "value"],
            },
        ),
        # TODO dictionary values?
        # defaults read-type <domain> <key>
        # defaults delete <domain> <key> # key is optional, domain required
    ]

def defaults_read(arguments: dict | None) -> list[types.TextContent]:
    if arguments is None:
        return []
    domain = arguments["domain"]
    key = arguments.get("key")

    if key is None:
        result = subprocess.run(["defaults", "read", domain], capture_output=True)
        return [types.TextContent(type="text", text=result.stdout.decode("utf-8"))]

    result = subprocess.run(["defaults", "read", domain, key], capture_output=True)
    value = result.stdout.decode("utf-8").strip()
    return [types.TextContent(type="text", text=f"{key}: {value}")]

def defaults_write(arguments: dict | None) -> list[types.TextContent]:
    if arguments is None:
        return []
    domain = arguments["domain"]
    key = arguments["key"]
    value = arguments["value"]

    # TODO do I need to notify client that resource changed? can't it just ask for it again?
    result = subprocess.run(["defaults", "write", domain, key, value], capture_output=True)
    return [types.TextContent(type="text", text=result.stdout.decode("utf-8"))]

def list_domains() -> list[types.TextContent]: # get array of domains:
    # run command `defaults domains`
    result = subprocess.run(["defaults", "domains"], capture_output=True)
    domains = result.stdout.decode("utf-8").split(",")
    domains = [domain.strip() for domain in domains]
    return [types.TextContent(type="text", text=f"Domains: {domains}")]

def find(arguments: dict | None) -> list[types.TextContent]: # ask for help to find a setting, that alone is possibly very useful
    if arguments is None:
        raise ValueError("Arguments are required")
    word = arguments["word"]
    result = subprocess.run(["defaults", "find", word], capture_output=True)
    return [types.TextContent(type="text", text=f"Found: {result.stdout.decode('utf-8')}")]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    # TODO => other types? | types.ImageContent | types.EmbeddedResource]:

    # # Notify clients that resources have changed (if server changes resources)
    # await server.request_context.session.send_resource_list_changed()

    if name == "list-domains":
        return list_domains()
    elif name == "find":
        return find(arguments)
    elif name == "defaults-read":
        return defaults_read(arguments)
    elif name == "defaults-write":
        return defaults_write(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-server-macos-defaults",
                server_version="0.1.2",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

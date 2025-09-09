import json
import asyncio
import logging

from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

from .fetcher import Fetcher
from .scheme import SurveyTypeStr, LocalizeLanguageStr

logger = logging.getLogger('surveymars-mcp')


@dataclass
class AppContext:
    """Application context for SurveyMars MCP Server."""

    fetcher: Fetcher | None = None

@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[AppContext]:
    """Initialize and clean up application resources."""

    try:
        # Initialize services
        fetcher = Fetcher()

        # Log the startup information
        logger.info("Starting SurveyMars MCP Server")

        logger.info(f"Base URL: {fetcher.config.base_url}")
        logger.info(f"Account ID: {fetcher.config.account_id}")
        logger.info(f"Secret Key: {fetcher.config.secret_key}")

        # Provide context to the application
        yield AppContext(fetcher=fetcher)
    finally:
        # Cleanup resources if needed
        pass

server = Server("surveymars-mcp", lifespan=server_lifespan)

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available note resources.
    Each note is exposed as a resource with a custom note:// URI scheme.
    """
    return []

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific note's content by its URI.
    The note name is extracted from the URI host component.
    """
    raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts.
    Each prompt can have optional arguments to customize its behavior.
    """
    return []

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt by combining arguments with server state.
    The prompt includes all current notes and can be customized via arguments.
    """
    raise ValueError(f"Unknown prompt: {name}")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
    ctx = server.request_context.lifespan_context

    return [
        types.Tool(
            name="survey_create",
            description="""Create survey with SurveyMars, Returns a set of links to the generated survey. With this AI-powered survey generator, you can enter essential details like target audience, brand, and research objectives, and I will produce a personalized questionnaire for you. The more specific your input, the more precise the questionnaire content will be.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Survey Title: Enter a survey title summarizing your research topic."
                    },
                    "purpose": {
                        "type": "string",
                        "description": "Survey Topic Prompts: Provide a detailed description of the survey, including its topic and purpose."
                    },
                    "num_questions": {
                        "type": "number",
                        "description": "Number of questions for survey (1-): A shorter survey with fewer questions is preferable.",
                        "default": 10,
                        "minimum": 1,
                    },
                    "survey_type": {
                        "type": "number",
                        "description": (
                            "Survey Type of Survey (1-6)",
                            SurveyTypeStr,
                        ),
                        "default": 1,
                        "minimum": 1,
                        "maximum": 6,
                    },
                    "language": {
                        "type": "number",
                        "description": (
                            "Survey Language (1-49): Surveys will be generated in your selected language.",
                            LocalizeLanguageStr,
                        ),
                        "default": 1,
                        "minimum": 1,
                        "maximum": 49,
                    },
                },
                "required": ["title", "purpose", "num_questions", "survey_type", "language"],
            },
        )
    ]

# tool_handlers = {
# }

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    ctx = server.request_context.lifespan_context

    if name == 'survey_create':
        result_url_dict = await ctx.fetcher.surveys_create(
            title=arguments.get('title', ''),
            purpose=arguments.get('purpose', ''),
            num_questions=arguments.get('num_questions', 10),
            language=arguments.get('language', 1),
            survey_type=arguments.get('survey_type', 1)
        )

        if result_url_dict is None:
            result_text = 'Survey create failed'
        else:
            result_text=json.dumps(result_url_dict, indent=2, ensure_ascii=False)
        return [
            types.TextContent(
                type="text",
                text=result_text,
            )
        ]

    # if name in tool_handlers:
    #     return await tool_handlers[name].handle(name, arguments)
    # else:
    #     raise ValueError(f"Unknown tool: {name}")

async def run_server():
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="surveymars-mcp",
                server_version="0.1.1",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
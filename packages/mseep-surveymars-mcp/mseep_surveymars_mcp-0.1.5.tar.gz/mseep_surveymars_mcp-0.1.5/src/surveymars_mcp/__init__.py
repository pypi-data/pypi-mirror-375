import os
import click
import logging
import asyncio
from dotenv import load_dotenv
from . import server

__version__ = "0.1.1"

# log config
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.StreamHandler(),
#         # logging.FileHandler('surveymars-mcp.log')
#     ]
# )

logger = logging.getLogger('surveymars-mcp')

@click.command()
@click.option("--account-id", help="Account ID")
@click.option("--secret-key", help="Account Secret Key")
@click.option("--env-file", type=click.Path(exists=True, dir_okay=False), help="Path to .env file")
def main(account_id: str | None, secret_key: str | None, env_file: str | None):
    """
    SurveyMars MCP Server.
    """
    # Load environment variables from file if specified, otherwise try default .env
    if env_file:
        logger.info(f"Loading environment from file: {env_file}")
        load_dotenv(env_file)
    else:
        logger.info("Attempting to load environment from default .env file")
        load_dotenv()

    if account_id:
        os.environ["ACCOUNT_ID"] = account_id
    if secret_key:
        os.environ["SECRET_KEY"] = secret_key

    try:
        asyncio.run(server.run_server())
    except Exception as e:
        logger.error(f"Server Error: {e}", exc_info=True)
        raise

# Optionally expose other important items at package level
__all__ = ['main', 'server', '__version__', 'logger']

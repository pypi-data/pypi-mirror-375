import httpx
import logging
import asyncio
import enum
from typing import Dict
from .config import FetcherConfig

logger = logging.getLogger('surveymars-mcp')

JobStatus = enum.Enum('JobStatus', ('None', 'Created', 'Running', 'Canceled', 'Success', 'Failure'), start=0)


class Fetcher:
    """Main entry point for operations, providing backward compatibility."""

    def __init__(self, config: FetcherConfig | None = None) -> None:
        """Initialize the Fetcher with given or environment config.

        Args:
            config: Configuration for Fetcher. If None, will load from
                environment.

        Raises:
            ValueError: If configuration is invalid or environment variables are missing
        """
        self.config = config or FetcherConfig.from_env()

    async def get_access_token(self) -> str:
        """
        User authentication, get Access token

        Args:
            account_id: User ID
            secret_key: Credential

        Returns:
            Access token
        """

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.config.base_url}/v1/authenticate',
                # headers={'Content-Type': 'application/json'},
                json={
                  "id": self.config.account_id,
                  "credential": self.config.secret_key 
                }
            )

            res_dict = response.json()
            logger.info(f"[authenticate] [success] [account_id={self.config.account_id}] [secret_key={self.config.secret_key}] [res={res_dict}]")
            
            access_token_dict = res_dict.get('data', {}).get('access_token', {})
            token_type = access_token_dict.get('token_type', '')
            token = access_token_dict.get('token', '')
            return f'{token_type} {token}'

    async def surveys_create(self, 
                             title: str, 
                             purpose: str, 
                             language: int = 1, 
                             num_questions: int = 10, 
                             survey_type: int = 1) -> Dict[str, str] | None:
        """
        AI Create Survey

        Args:
            title: Survey title
            purpose: Survey purpose
            language: Survey Language
            num_questions: Number of questions
            survey_type: Type

        Returns:
            Survey link dictionary
        """
        token = await self.get_access_token()

        req_data={
            "language": language,
            "title": title,
            "purpose": purpose,
            "num_questions": num_questions,
            "survey_type": survey_type
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f'{self.config.base_url}/v1/surveys/ai',
                headers={'Authorization': token},
                json=req_data
            )

            res_dict = response.json()
            url_callback = res_dict.get('data', {}).get('url_callback', '')
            if not url_callback:
                logger.error("[surveys create] [task create failed] [callback_url empty]")
                return

            logger.info(f"[surveys create] [task create success] [req={req_data}] [res={res_dict}]")

            max_retries = 50
            initial_delay = 2

            retry_count = 0
            while retry_count < max_retries:
                retry_count += 1
                
                try:
                    callback_response = await client.get(
                        url_callback,
                        headers={'Authorization': token},
                    )
                    
                    callback_res_dict = callback_response.json()
                    logger.info(f"[survey create] [callback] [times={retry_count}] [res={callback_res_dict}]")
                    
                    data = callback_res_dict.get('data', {})
                    task_status = data.pop('task_status', None)
                    
                    if task_status == JobStatus.Success.value:
                        return data
                    elif task_status in [JobStatus.Failure.value, JobStatus.Canceled.value]:
                        logger.warning(f"[survey create] [callback] [task failed] [times={retry_count}] [task_status={task_status}]")
                        return
                    
                except Exception as e:
                    logger.error(f"[survey create] [callback] [error] [times={retry_count}] [{str(e)}]")
                
                await asyncio.sleep(initial_delay)
            
            logger.error(f"[survey create] [callback] [timeout, maxretries={max_retries}]")
            return

                

__all__ = ["Fetcher"]

"""Configuration module for the client."""

import os
from dataclasses import dataclass


@dataclass
class FetcherConfig:
    """Fetcher configuration."""

    account_id: str  # Account ID
    secret_key: str  # Secret Key
    base_url: str = "https://api.surveymars.com"  # Base URL

    @classmethod
    def from_env(cls) -> "FetcherConfig":
        """Create configuration from environment variables.

        Returns:
            FetcherConfig with values from environment variables

        Raises:
            ValueError: If any required environment variable is missing
        """
        account_id = os.getenv("ACCOUNT_ID")
        if not account_id:
            error_msg = "Missing required ACCOUNT_ID environment variable"
            raise ValueError(error_msg)

        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            error_msg = "Missing required SECRET_KEY environment variable"
            raise ValueError(error_msg)

        return cls(
            account_id=account_id,
            secret_key=secret_key,
        )

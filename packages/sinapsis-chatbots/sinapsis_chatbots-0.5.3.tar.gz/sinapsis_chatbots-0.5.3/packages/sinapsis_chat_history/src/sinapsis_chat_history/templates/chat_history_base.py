# -*- coding: utf-8 -*-
from typing import Literal

from pydantic import Field
from pydantic.dataclasses import dataclass
from sinapsis_core.template_base.base_models import (
    OutputTypes,
    TemplateAttributes,
    TemplateAttributeType,
    UIPropertiesMetadata,
)
from sinapsis_core.template_base.template import Template

from sinapsis_chat_history.helpers.database_env_var_keys import DatabaseEnvVars
from sinapsis_chat_history.helpers.factory import StorageProviderFactory
from sinapsis_chat_history.helpers.postgres_provider import PostgresDatabaseConfig


@dataclass
class ChatHistoryColumns:
    user_id: str = "user_id"
    role: str = "role"
    session_id: str = "session_id"
    timestamp: str = "timestamp"
    content: str = "content"
    metadata: str = "metadata"


class ChatHistoryBaseAttributes(TemplateAttributes):
    """Attribute configuration for chat history templates.

    Attributes:
        provider (Literal["postgres"]): The storage backend to use (currently only "postgres" is supported).
        db_config (dict[str, Any]): Configuration dictionary for initializing the selected storage provider.
    """

    provider: Literal["postgres"] = "postgres"
    db_config: PostgresDatabaseConfig = Field(default_factory=PostgresDatabaseConfig)


class ChatHistoryBase(Template):
    """Base class for all chat history-related templates.

    Handles shared initialization logic and provides a database connection instance (`self.db`)
    based on the provider and configuration supplied via attributes.
    """

    AttributesBaseModel = ChatHistoryBaseAttributes
    UIProperties = UIPropertiesMetadata(category="databases", output_type=OutputTypes.TEXT)

    def __init__(self, attributes: TemplateAttributeType) -> None:
        super().__init__(attributes)
        env_map = {
            "user": DatabaseEnvVars.DB_USER,
            "password": DatabaseEnvVars.DB_PASSWORD,
            "host": DatabaseEnvVars.DB_HOST,
            "port": DatabaseEnvVars.DB_PORT,
        }

        for attr_name, env_var in env_map.items():
            if env_var.value:
                value = int(env_var.value) if attr_name == "port" else env_var.value
                setattr(self.attributes.db_config, attr_name, value)

        self.db = StorageProviderFactory.create(provider=self.attributes.provider, config=self.attributes.db_config)

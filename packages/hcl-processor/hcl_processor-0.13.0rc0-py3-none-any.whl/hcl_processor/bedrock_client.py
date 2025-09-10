import json
import os

import boto3
from botocore.config import Config
from botocore.exceptions import (ClientError, EndpointConnectionError,
                                 ReadTimeoutError)

from .utils import measure_time
from .logger_config import get_logger, log_exception

logger = get_logger("bedrock_client")


def aws_bedrock(prompt: str, modules_data: str | None, config: dict, system_config: dict) -> str:
    """
    Call the AWS Bedrock API with the given prompt and configuration.
    Args:
        prompt (str): The prompt to send to the Bedrock API.
        modules_data (str): Additional data for modules.
        config (dict): Configuration for the Bedrock API.
        system_config (dict): System configuration.
    Returns:
        str: The response from the Bedrock API.
    Raises:
        Exception: If the Bedrock API call fails or the response cannot be parsed.
    """

    timeout_config = {
        "read_timeout": config["bedrock"].get(
            "read_timeout",
            system_config["default_bedrock"]["timeout_config"]["read_timeout"],
        ),
        "connect_timeout": config["bedrock"].get(
            "connect_timeout",
            system_config["default_bedrock"]["timeout_config"]["connect_timeout"],
        ),
        "retries": config["bedrock"].get(
            "retries",
            {
                "max_attempts": system_config["default_bedrock"]["timeout_config"][
                    "retries"
                ]["max_attempts"],
                "mode": system_config["default_bedrock"]["timeout_config"]["retries"][
                    "mode"
                ],
            },
        ),
    }
    bedrock_config = Config(**timeout_config)
    if config["bedrock"].get("aws_profile") is not None:
        logger.info(
            f"Using AWS profile: {config['bedrock'].get('aws_profile')}"
        )
        session = boto3.Session(profile_name=config["bedrock"].get("aws_profile"))
    else:
        logger.info(
            "No AWS profile specified, using environment variables for credentials."
        )
        aws_access_key_id = config.get("aws_access_key_id") or os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = config.get("aws_secret_access_key") or os.getenv("AWS_SECRET_ACCESS_KEY")
        aws_session_token = config.get("aws_session_token") or os.getenv("AWS_SESSION_TOKEN")
        if aws_access_key_id and aws_secret_access_key:
            session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                aws_session_token=aws_session_token,
            )
        else:
            logger.error(
                "No AWS credentials provided. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
            )
            raise Exception("AWS credentials not found. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables.")
    logger.info(
        f"Using AWS region: {config['bedrock'].get('aws_region','us-east-1')}"
    )
    bedrock = session.client(
        "bedrock-runtime", region_name=config['bedrock'].get('aws_region','us-east-1'), config=bedrock_config
    )

    modules_enabled = config.get("modules", {}).get("enabled", True)
    modules_data_str = modules_data if (modules_data is not None) else ""

    final_system_prompt = (
        system_config["system_prompt"]
        + "\n"
        + config["bedrock"]["system_prompt"]
    )
    final_system_prompt = final_system_prompt.replace(
        "{modules_data}", modules_data_str if modules_enabled else ""
    )
    logger.debug(f"Prompt: {prompt}")
    messages = [{"role": "user", "content": [{"text": prompt}]}]
    system = [{"text": final_system_prompt}]

    inference_config = {
        "maxTokens": config["bedrock"]["payload"].get(
            "max_tokens", system_config["default_bedrock"]["payload"]["max_tokens"]
        ),
        "temperature": config["bedrock"]["payload"].get(
            "temperature", system_config["default_bedrock"]["payload"]["temperature"]
        ),
        "topP": config["bedrock"]["payload"].get(
            "top_p", system_config["default_bedrock"]["payload"]["top_p"]
        )
    }

    tool_config = {
        "tools": [
            {
                "toolSpec": {
                    "name": "json_validator",
                    "description": "Validates and formats JSON output",
                    "inputSchema": {
                        "json": {
                            "type": "object",
                            "properties": {
                                "monitors": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": config["bedrock"]["output_json"].get("items", {}).get("properties", {})
                                    }
                                }
                            }
                        }
                    }
                }
            }
        ],
        "toolChoice": {
            "tool": {
                "name": "json_validator"
            }
        }
    }

    try:
        model_id = config["bedrock"].get("model_id", system_config["constants"]["bedrock"]["default_model_id"])
        with measure_time(f"AWS Bedrock API call: {model_id}", logger):
            response = bedrock.converse(
                modelId=model_id,
                messages=messages,
                system=system,
                inferenceConfig=inference_config,
                toolConfig=tool_config
            )
        logger.debug(f"Bedrock response:\n {response}")
        try:
            logger.debug(f"Full response structure: {json.dumps(response, indent=2)}")
            output = response.get("output", {})
            message = output.get("message", {})
            if message is None:
                logger.error(f"Response structure: {response}")
                raise AttributeError("Response message is None")
            content = message.get("content", [{}])[0]
            # Handle tool use response
            if "toolUse" in content:
                tool_use = content["toolUse"]
                logger.debug(f"Tool use response: {json.dumps(tool_use, indent=2, ensure_ascii=False)}")
                if tool_use["name"] == system_config["constants"]["bedrock"]["tool_name"]:
                    result = json.dumps(tool_use["input"].get(system_config["constants"]["bedrock"]["target_json_key"], []), ensure_ascii=False)
                    logger.debug(f"JSON validation result: {result}")
                    return result

            # Handle text response
            if "text" in content:
                return content.get("text", "")

            raise json.JSONDecodeError("Invalid response format: missing text or toolUse", "", 0)
        except (AttributeError, TypeError, json.JSONDecodeError) as e:
            log_exception(logger, e, "Failed to parse Bedrock response")
            raise
    except EndpointConnectionError as e:
        log_exception(logger, e, "Bedrock endpoint connection failed")
        raise
    except ReadTimeoutError as e:
        log_exception(logger, e, "Bedrock read timeout")
        raise
    except ClientError as e:
        log_exception(logger, e, "Bedrock client error")
        raise
    except Exception as e:
        log_exception(logger, e, "Unexpected error during Bedrock invocation")
        raise

# encoding: utf-8
import logging

from httpx import (AsyncClient, AsyncHTTPTransport, Client, HTTPTransport,
                   Request, Response)

from .exceptions import AuthenticationError, BadRequestError, ItemNotFoundError

logger = logging.getLogger(__name__)


def log_request(request: Request) -> None:
    logger.debug(
        f"Send Request: {request.method} {request.url} - Waiting for response")


def check_response(response: Response) -> None:
    if response.is_success or response.is_redirect:
        return
    if response.status_code == 404:
        raise ItemNotFoundError(f'404 Not found {response.url}')
    if response.status_code == 401:
        raise AuthenticationError(
            f'401 Invalid authorization for {response.url}')
    if response.status_code == 403:
        raise PermissionError(f'403 No permission to access {response.url}')
    if response.status_code == 400:
        raise BadRequestError(f'400 {response.headers["X-Error"]}')
    response.raise_for_status()


def new_http_client(**kwargs) -> Client:
    return Client(
        transport=HTTPTransport(
            verify=kwargs.pop('verify', True),
            cert=kwargs.pop('cert', None),
            http1=kwargs.pop('http1', True),
            http2=kwargs.pop('http2', False),
            trust_env=kwargs.pop('trust_env', True),
            proxy=kwargs.pop('proxy', None),
            uds=kwargs.pop('uds', None),
            local_address=kwargs.pop('local_address', None),
            retries=kwargs.pop('retries', 0),
            socket_options=kwargs.pop('socket_options', None)
        ),
        **kwargs,
        event_hooks={'request': [log_request], 'response': [check_response]}
    )


async def async_log_request(request: Request) -> None:
    logger.debug(
        f"Send Request: {request.method} {request.url} - Waiting for response")


async def async_check_response(response: Response) -> None:
    check_response(response)


def new_async_http_client(**kwargs) -> AsyncClient:
    return AsyncClient(
        transport=AsyncHTTPTransport(
            verify=kwargs.pop('verify', True),
            cert=kwargs.pop('cert', None),
            http1=kwargs.pop('http1', True),
            http2=kwargs.pop('http2', False),
            trust_env=kwargs.pop('trust_env', True),
            proxy=kwargs.pop('proxy', None),
            uds=kwargs.pop('uds', None),
            local_address=kwargs.pop('local_address', None),
            retries=kwargs.pop('retries', 0),
            socket_options=kwargs.pop('socket_options', None)
        ),
        **kwargs,
        event_hooks={'request': [async_log_request],
                     'response': [async_check_response]}
    )

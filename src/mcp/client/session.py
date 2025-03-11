from datetime import timedelta
from typing import Any, Protocol

from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from pydantic import AnyUrl, TypeAdapter

import mcp.types as types
from mcp.shared.context import RequestContext
from mcp.shared.session import BaseSession, RequestResponder
from mcp.shared.version import SUPPORTED_PROTOCOL_VERSIONS


class SamplingFnT(Protocol):
    async def __call__(
        self,
        context: RequestContext["ClientSession", Any],
        params: types.CreateMessageRequestParams,
    ) -> types.CreateMessageResult | types.ErrorData: ...


class ListRootsFnT(Protocol):
    async def __call__(
        self, context: RequestContext["ClientSession", Any]
    ) -> types.ListRootsResult | types.ErrorData: ...


async def _default_sampling_callback(
    context: RequestContext["ClientSession", Any],
    params: types.CreateMessageRequestParams,
) -> types.CreateMessageResult | types.ErrorData:
    return types.ErrorData(
        code=types.INVALID_REQUEST,
        message="Sampling not supported",
    )


async def _default_list_roots_callback(
    context: RequestContext["ClientSession", Any],
) -> types.ListRootsResult | types.ErrorData:
    return types.ErrorData(
        code=types.INVALID_REQUEST,
        message="List roots not supported",
    )


ClientResponse = TypeAdapter(types.ClientResult | types.ErrorData)


class ClientSession(
    BaseSession[
        types.ClientRequest,
        types.ClientNotification,
        types.ClientResult,
        types.ServerRequest,
        types.ServerNotification,
    ]
):
    def __init__(
        self,
        read_stream: MemoryObjectReceiveStream[types.JSONRPCMessage | Exception],
        write_stream: MemoryObjectSendStream[types.JSONRPCMessage],
        read_timeout_seconds: timedelta | None = None,
        sampling_callback: SamplingFnT | None = None,
        list_roots_callback: ListRootsFnT | None = None,
    ) -> None:
        super().__init__(
            read_stream,
            write_stream,
            types.ServerRequest,
            types.ServerNotification,
            read_timeout_seconds=read_timeout_seconds,
        )
        self._sampling_callback = sampling_callback or _default_sampling_callback
        self._list_roots_callback = list_roots_callback or _default_list_roots_callback

    async def initialize(self) -> types.InitializeResult:
        sampling = (
            types.SamplingCapability() if self._sampling_callback is not None else None
        )
        roots = (
            types.RootsCapability(
                # TODO: Should this be based on whether we
                # _will_ send notifications, or only whether
                # they're supported?
                listChanged=True,
            )
            if self._list_roots_callback is not None
            else None
        )

        result = await self.send_request(
            types.ClientRequest(
                types.InitializeRequest(
                    method="initialize",
                    params=types.InitializeRequestParams(
                        protocolVersion=types.LATEST_PROTOCOL_VERSION,
                        capabilities=types.ClientCapabilities(
                            sampling=sampling,
                            experimental=None,
                            roots=roots,
                        ),
                        clientInfo=types.Implementation(name="mcp", version="0.1.0"),
                    ),
                )
            ),
            types.InitializeResult,
        )

        if result.protocolVersion not in SUPPORTED_PROTOCOL_VERSIONS:
            raise RuntimeError(
                "Unsupported protocol version from the server: "
                f"{result.protocolVersion}"
            )

        await self.send_notification(
            types.ClientNotification(
                types.InitializedNotification(method="notifications/initialized")
            )
        )

        return result

    async def send_ping(self) -> types.EmptyResult:
        """Send a ping request."""
        return await self.send_request(
            types.ClientRequest(
                types.PingRequest(
                    method="ping",
                )
            ),
            types.EmptyResult,
        )

    async def send_progress_notification(
        self, progress_token: str | int, progress: float, total: float | None = None
    ) -> None:
        """Send a progress notification."""
        await self.send_notification(
            types.ClientNotification(
                types.ProgressNotification(
                    method="notifications/progress",
                    params=types.ProgressNotificationParams(
                        progressToken=progress_token,
                        progress=progress,
                        total=total,
                    ),
                ),
            )
        )

    async def set_logging_level(self, level: types.LoggingLevel) -> types.EmptyResult:
        """Send a logging/setLevel request."""
        return await self.send_request(
            types.ClientRequest(
                types.SetLevelRequest(
                    method="logging/setLevel",
                    params=types.SetLevelRequestParams(level=level),
                )
            ),
            types.EmptyResult,
        )

    async def list_resources(self) -> types.ListResourcesResult:
        """Send a resources/list request."""
        return await self.send_request(
            types.ClientRequest(
                types.ListResourcesRequest(
                    method="resources/list",
                )
            ),
            types.ListResourcesResult,
        )

    async def list_resource_templates(self) -> types.ListResourceTemplatesResult:
        """Send a resources/templates/list request."""
        return await self.send_request(
            types.ClientRequest(
                types.ListResourceTemplatesRequest(
                    method="resources/templates/list",
                )
            ),
            types.ListResourceTemplatesResult,
        )

    async def read_resource(self, uri: AnyUrl) -> types.ReadResourceResult:
        """Send a resources/read request."""
        return await self.send_request(
            types.ClientRequest(
                types.ReadResourceRequest(
                    method="resources/read",
                    params=types.ReadResourceRequestParams(uri=uri),
                )
            ),
            types.ReadResourceResult,
        )

    async def subscribe_resource(self, uri: AnyUrl) -> types.EmptyResult:
        """Send a resources/subscribe request."""
        return await self.send_request(
            types.ClientRequest(
                types.SubscribeRequest(
                    method="resources/subscribe",
                    params=types.SubscribeRequestParams(uri=uri),
                )
            ),
            types.EmptyResult,
        )

    async def unsubscribe_resource(self, uri: AnyUrl) -> types.EmptyResult:
        """Send a resources/unsubscribe request."""
        return await self.send_request(
            types.ClientRequest(
                types.UnsubscribeRequest(
                    method="resources/unsubscribe",
                    params=types.UnsubscribeRequestParams(uri=uri),
                )
            ),
            types.EmptyResult,
        )

    async def call_tool(
        self, name: str, arguments: dict | None = None
    ) -> types.CallToolResult:
        """Send a tools/call request."""
        return await self.send_request(
            types.ClientRequest(
                types.CallToolRequest(
                    method="tools/call",
                    params=types.CallToolRequestParams(name=name, arguments=arguments),
                )
            ),
            types.CallToolResult,
        )

    async def list_prompts(self) -> types.ListPromptsResult:
        """Send a prompts/list request."""
        return await self.send_request(
            types.ClientRequest(
                types.ListPromptsRequest(
                    method="prompts/list",
                )
            ),
            types.ListPromptsResult,
        )

    async def get_prompt(
        self, name: str, arguments: dict[str, str] | None = None
    ) -> types.GetPromptResult:
        """Send a prompts/get request."""
        return await self.send_request(
            types.ClientRequest(
                types.GetPromptRequest(
                    method="prompts/get",
                    params=types.GetPromptRequestParams(name=name, arguments=arguments),
                )
            ),
            types.GetPromptResult,
        )

    async def complete(
        self, ref: types.ResourceReference | types.PromptReference, argument: dict
    ) -> types.CompleteResult:
        """Send a completion/complete request."""
        return await self.send_request(
            types.ClientRequest(
                types.CompleteRequest(
                    method="completion/complete",
                    params=types.CompleteRequestParams(
                        ref=ref,
                        argument=types.CompletionArgument(**argument),
                    ),
                )
            ),
            types.CompleteResult,
        )

    async def list_tools(self) -> types.ListToolsResult:
        """Send a tools/list request."""
        return await self.send_request(
            types.ClientRequest(
                types.ListToolsRequest(
                    method="tools/list",
                )
            ),
            types.ListToolsResult,
        )

    async def send_roots_list_changed(self) -> None:
        """Send a roots/list_changed notification."""
        await self.send_notification(
            types.ClientNotification(
                types.RootsListChangedNotification(
                    method="notifications/roots/list_changed",
                )
            )
        )

    async def _received_request(
        self, responder: RequestResponder[types.ServerRequest, types.ClientResult]
    ) -> None:
        ctx = RequestContext[ClientSession, Any](
            request_id=responder.request_id,
            meta=responder.request_meta,
            session=self,
            lifespan_context=None,
        )

        match responder.request.root:
            case types.CreateMessageRequest(params=params):
                with responder:
                    response = await self._sampling_callback(ctx, params)
                    client_response = ClientResponse.validate_python(response)
                    await responder.respond(client_response)

            case types.ListRootsRequest():
                with responder:
                    response = await self._list_roots_callback(ctx)
                    client_response = ClientResponse.validate_python(response)
                    await responder.respond(client_response)

            case types.PingRequest():
                with responder:
                    return await responder.respond(
                        types.ClientResult(root=types.EmptyResult())
                    )

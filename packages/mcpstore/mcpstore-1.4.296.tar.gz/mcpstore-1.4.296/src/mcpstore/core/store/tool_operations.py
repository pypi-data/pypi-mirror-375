"""
工具操作模块
负责处理 MCPStore 的工具相关功能
"""

from typing import Optional, List, Dict, Any
import logging
import time

from mcpstore.core.models.tool import ToolExecutionRequest, ToolInfo
from mcpstore.core.models.common import ExecutionResponse

logger = logging.getLogger(__name__)


class ToolOperationsMixin:
    """工具操作 Mixin"""
    
    async def process_tool_request(self, request: ToolExecutionRequest) -> ExecutionResponse:
        """
        处理工具执行请求（FastMCP 标准）

        Args:
            request: 工具执行请求

        Returns:
            ExecutionResponse: 工具执行响应
        """
        start_time = time.time()

        try:
            # 验证请求参数
            if not request.tool_name:
                raise ValueError("Tool name cannot be empty")
            if not request.service_name:
                raise ValueError("Service name cannot be empty")

            logger.debug(f"Processing tool request: {request.service_name}::{request.tool_name}")

            # 检查服务生命周期状态
            # 🔧 对于 Agent 透明代理，全局服务存在于 global_agent_store 中
            if request.agent_id and "_byagent_" in request.service_name:
                # Agent 透明代理：全局服务在 global_agent_store 中
                state_check_agent_id = self.client_manager.global_agent_store_id
            else:
                # Store 模式或普通 Agent 服务
                state_check_agent_id = request.agent_id or self.client_manager.global_agent_store_id

            service_state = self.orchestrator.lifecycle_manager.get_service_state(state_check_agent_id, request.service_name)

            # 如果服务处于不可用状态，返回错误
            from mcpstore.core.models.service import ServiceConnectionState
            if service_state in [ServiceConnectionState.RECONNECTING, ServiceConnectionState.UNREACHABLE,
                               ServiceConnectionState.DISCONNECTING, ServiceConnectionState.DISCONNECTED]:
                error_msg = f"Service '{request.service_name}' is currently {service_state.value} and unavailable for tool execution"
                logger.warning(error_msg)
                return ExecutionResponse(
                    success=False,
                    result=None,
                    error=error_msg,
                    execution_time=time.time() - start_time,
                    service_name=request.service_name,
                    tool_name=request.tool_name,
                    agent_id=request.agent_id
                )

            # 执行工具（使用 FastMCP 标准）
            result = await self.orchestrator.execute_tool_fastmcp(
                service_name=request.service_name,
                tool_name=request.tool_name,
                arguments=request.args,
                agent_id=request.agent_id,
                timeout=request.timeout,
                progress_handler=request.progress_handler,
                raise_on_error=request.raise_on_error
            )

            # 📊 记录成功的工具执行
            try:
                duration_ms = (time.time() - start_time) * 1000

                # 获取对应的Context来记录监控数据
                if request.agent_id:
                    context = self.for_agent(request.agent_id)
                else:
                    context = self.for_store()

                # 使用新的详细记录方法
                context._monitoring.record_tool_execution_detailed(
                    tool_name=request.tool_name,
                    service_name=request.service_name,
                    params=request.args,
                    result=result,
                    error=None,
                    response_time=duration_ms
                )
            except Exception as monitor_error:
                logger.warning(f"Failed to record tool execution: {monitor_error}")

            return ExecutionResponse(
                success=True,
                result=result
            )
        except Exception as e:
            # 📊 记录失败的工具执行
            try:
                duration_ms = (time.time() - start_time) * 1000

                # 获取对应的Context来记录监控数据
                if request.agent_id:
                    context = self.for_agent(request.agent_id)
                else:
                    context = self.for_store()

                # 使用新的详细记录方法
                context._monitoring.record_tool_execution_detailed(
                    tool_name=request.tool_name,
                    service_name=request.service_name,
                    params=request.args,
                    result=None,
                    error=str(e),
                    response_time=duration_ms
                )
            except Exception as monitor_error:
                logger.warning(f"Failed to record failed tool execution: {monitor_error}")

            logger.error(f"Tool execution failed: {e}")
            return ExecutionResponse(
                success=False,
                error=str(e)
            )

    async def call_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        调用工具（通用接口）

        Args:
            tool_name: 工具名称，格式为 service_toolname
            args: 工具参数

        Returns:
            Any: 工具执行结果
        """
        from mcpstore.core.models.tool import ToolExecutionRequest

        # 构造请求
        request = ToolExecutionRequest(
            tool_name=tool_name,
            args=args
        )

        # 处理工具请求
        return await self.process_tool_request(request)

    async def use_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """
        使用工具（通用接口）- 向后兼容别名

        注意：此方法是 call_tool 的别名，保持向后兼容性。
        推荐使用 call_tool 方法，与 FastMCP 命名保持一致。
        """
        return await self.call_tool(tool_name, args)

    def _get_client_id_for_service(self, agent_id: str, service_name: str) -> str:
        """获取服务对应的client_id"""
        try:
            # 1. 从agent_clients映射中查找
            client_ids = self.registry.get_agent_clients_from_cache(agent_id)
            if not client_ids:
                self.logger.warning(f"No client_ids found for agent {agent_id}")
                return ""

            # 2. 遍历每个client_id，查找包含该服务的client
            for client_id in client_ids:
                client_config = self.registry.client_configs.get(client_id, {})
                if service_name in client_config.get("mcpServers", {}):
                    return client_id

            # 3. 如果没找到，返回第一个client_id作为默认值
            if client_ids:
                self.logger.warning(f"Service {service_name} not found in any client config, using first client_id: {client_ids[0]}")
                return client_ids[0]

            return ""
        except Exception as e:
            self.logger.error(f"Error getting client_id for service {service_name}: {e}")
            return ""

    async def list_tools(self, id: Optional[str] = None, agent_mode: bool = False) -> List[ToolInfo]:
        """
        列出工具列表：
        - store未传id 或 id==global_agent_store：聚合 global_agent_store 下所有 client_id 的工具
        - store传普通 client_id：只查该 client_id 下的工具
        - agent级别：聚合 agent_id 下所有 client_id 的工具；如果 id 不是 agent_id，尝试作为 client_id 查
        """
        from mcpstore.core.client_manager import ClientManager
        client_manager: ClientManager = self.client_manager
        tools = []
        # 1. store未传id 或 id==global_agent_store，聚合 global_agent_store 下所有 client_id 的工具
        if not agent_mode and (not id or id == self.client_manager.global_agent_store_id):
            # 🔧 修复：直接从Registry缓存获取工具，而不是通过ClientManager
            agent_id = self.client_manager.global_agent_store_id
            self.logger.debug(f"🔧 [STORE.LIST_TOOLS] 直接从Registry缓存获取工具，agent_id={agent_id}")

            # 直接从tool_cache获取所有工具
            tool_cache = self.registry.tool_cache.get(agent_id, {})
            self.logger.debug(f"🔧 [STORE.LIST_TOOLS] Registry中的工具数量: {len(tool_cache)}")

            for tool_name, tool_def in tool_cache.items():
                # 获取工具对应的session来确定service_name
                session = self.registry.tool_to_session_map.get(agent_id, {}).get(tool_name)
                service_name = None

                # 通过session找到service_name
                for svc_name, svc_session in self.registry.sessions.get(agent_id, {}).items():
                    if svc_session is session:
                        service_name = svc_name
                        break

                # 🔧 获取该服务对应的client_id
                service_client_id = self._get_client_id_for_service(agent_id, service_name)

                # 构造ToolInfo对象
                if isinstance(tool_def, dict) and "function" in tool_def:
                    function_data = tool_def["function"]
                    tools.append(ToolInfo(
                        name=tool_name,
                        description=function_data.get("description", ""),
                        service_name=service_name or "unknown",
                        client_id=service_client_id,  # 🎯 使用正确的client_id
                        inputSchema=function_data.get("parameters", {})
                    ))
                else:
                    # 兼容其他格式
                    tools.append(ToolInfo(
                        name=tool_name,
                        description=tool_def.get("description", ""),
                        service_name=service_name or "unknown",
                        client_id=service_client_id,  # 🎯 使用正确的client_id
                        inputSchema=tool_def.get("inputSchema", {})
                    ))

            self.logger.debug(f"🔧 [STORE.LIST_TOOLS] 最终工具数量: {len(tools)}")
            return tools
        # 2. store传普通 client_id，只查该 client_id 下的工具
        if not agent_mode and id:
            if id == self.client_manager.global_agent_store_id:
                return tools
            tool_dicts = self.registry.get_all_tool_info(id)
            for tool in tool_dicts:
                # 使用存储的键名作为显示名称（现在键名就是显示名称）
                display_name = tool.get("name", "")
                tools.append(ToolInfo(
                    name=display_name,
                    description=tool.get("description", ""),
                    service_name=tool.get("service_name", ""),
                    client_id=tool.get("client_id", ""),
                    inputSchema=tool.get("inputSchema", {})
                ))
            return tools
        # 3. agent级别，聚合 agent_id 下所有 client_id 的工具；如果 id 不是 agent_id，尝试作为 client_id 查
        if agent_mode and id:
            # 🔧 修复：Agent模式也直接从Registry缓存获取工具
            self.logger.debug(f"🔧 [STORE.LIST_TOOLS] Agent模式，直接从Registry缓存获取工具，agent_id={id}")

            # 直接从tool_cache获取所有工具
            tool_cache = self.registry.tool_cache.get(id, {})
            self.logger.debug(f"🔧 [STORE.LIST_TOOLS] Agent模式Registry中的工具数量: {len(tool_cache)}")

            for tool_name, tool_def in tool_cache.items():
                # 获取工具对应的session来确定service_name
                session = self.registry.tool_to_session_map.get(id, {}).get(tool_name)
                service_name = None

                # 通过session找到service_name
                for svc_name, svc_session in self.registry.sessions.get(id, {}).items():
                    if svc_session is session:
                        service_name = svc_name
                        break

                # 🔧 获取该服务对应的client_id（Agent模式使用global_agent_store）
                service_client_id = self._get_client_id_for_service(self.client_manager.global_agent_store_id, service_name)

                # 构造ToolInfo对象
                if isinstance(tool_def, dict) and "function" in tool_def:
                    function_data = tool_def["function"]
                    tools.append(ToolInfo(
                        name=tool_name,
                        description=function_data.get("description", ""),
                        service_name=service_name or "unknown",
                        client_id=service_client_id,  # 🎯 使用正确的client_id
                        inputSchema=function_data.get("parameters", {})
                    ))
                else:
                    # 兼容其他格式
                    tools.append(ToolInfo(
                        name=tool_name,
                        description=tool_def.get("description", ""),
                        service_name=service_name or "unknown",
                        client_id=service_client_id,  # 🎯 使用正确的client_id
                        inputSchema=tool_def.get("inputSchema", {})
                    ))

            self.logger.debug(f"🔧 [STORE.LIST_TOOLS] Agent模式最终工具数量: {len(tools)}")
            return tools
        return tools

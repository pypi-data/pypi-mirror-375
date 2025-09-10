"""
MCP tools implementation for LogMCP server
"""

from typing import Optional
from fastmcp import FastMCP, Context

from .services import loki_service
from .logger import logger


def register_tools(mcp: FastMCP) -> None:
    """Register MCP tools with the FastMCP server"""
    
    @mcp.tool()
    async def loki_keyword_query(
        env: str,
        keywords: str,
        service_name: Optional[str] = "zkme-token",
        namespace: Optional[str] = None,
        limit: Optional[int] = 1000,
        ctx: Optional[Context] = None
    ) -> str:
        """
        通过Loki查询包含关键字的日志（最近30天）

        Args:
            env: 环境名称 (如: test, dev, prod)
            keywords: 搜索关键字 (多个关键字用逗号分隔)
            service_name: 服务名称 (可选，默认为zkme-token)
                         💡 可用的service_name列表可通过 loki_service_names 工具获取
            namespace: Loki命名空间 (可选，默认基于环境推断)
            limit: 结果限制 (可选，默认1000)
            ctx: MCP上下文 (自动注入)

        建议使用流程：
        1. 调用 loki_service_names 获取可用的service_name列表
        2. 选择目标service_name
        3. 使用选定的service_name执行关键字查询

        Returns:
            格式化的日志查询结果
        """
        try:
            if ctx:
                await ctx.info(f"Starting Loki keyword query for env: {env}, keywords: {keywords}")
            
            logger.info(f"MCP loki_keyword_query called: env={env}, keywords={keywords}, service={service_name}")
            
            # Validate required parameters
            if not env:
                error_msg = "Environment parameter is required"
                if ctx:
                    await ctx.error(error_msg)
                return error_msg
                
            if not keywords:
                error_msg = "Keywords parameter is required"
                if ctx:
                    await ctx.error(error_msg)
                return error_msg
            
            # Execute query
            result = loki_service.query_keyword_logs(
                env=env,
                keywords=keywords,
                service_name=service_name,
                namespace=namespace,
                limit=limit
            )
            
            if ctx:
                await ctx.info(f"Loki keyword query completed successfully")
            
            return result
            
        except Exception as e:
            error_msg = f"Loki keyword query failed: {str(e)}"
            logger.error_with_traceback("MCP Loki keyword query error", e)
            if ctx:
                await ctx.error(error_msg)
            return error_msg
    
    @mcp.tool()
    async def loki_range_query(
        env: str,
        start_date: str,
        end_date: str,
        keywords: str,
        service_name: Optional[str] = "zkme-token",
        namespace: Optional[str] = None,
        limit: Optional[int] = 1000,
        ctx: Optional[Context] = None
    ) -> str:
        """
        通过Loki查询指定时间范围内包含关键字的日志

        Args:
            env: 环境名称 (如: test, dev, prod)
            start_date: 开始日期 (YYYYMMDD格式)
            end_date: 结束日期 (YYYYMMDD格式)
            keywords: 搜索关键字 (多个关键字用逗号分隔)
            service_name: 服务名称 (可选，默认为zkme-token)
                         💡 可用的service_name列表可通过 loki_service_names 工具获取
            namespace: Loki命名空间 (可选，默认基于环境推断)
            limit: 结果限制 (可选，默认1000)
            ctx: MCP上下文 (自动注入)

        建议使用流程：
        1. 调用 loki_service_names 获取可用的service_name列表
        2. 选择目标service_name
        3. 使用选定的service_name执行时间范围查询

        Returns:
            格式化的日志查询结果
        """
        try:
            if ctx:
                await ctx.info(f"Starting Loki range query for env: {env}, dates: {start_date}-{end_date}")
            
            logger.info(f"MCP loki_range_query called: env={env}, start={start_date}, end={end_date}, keywords={keywords}")
            
            # Validate required parameters
            if not env:
                error_msg = "Environment parameter is required"
                if ctx:
                    await ctx.error(error_msg)
                return error_msg
                
            if not start_date or not end_date:
                error_msg = "Start date and end date parameters are required"
                if ctx:
                    await ctx.error(error_msg)
                return error_msg
                
            if not keywords:
                error_msg = "Keywords parameter is required"
                if ctx:
                    await ctx.error(error_msg)
                return error_msg
            
            # Execute query
            result = loki_service.query_range_logs_by_dates(
                env=env,
                start_date=start_date,
                end_date=end_date,
                keywords=keywords,
                service_name=service_name,
                namespace=namespace,
                limit=limit
            )
            
            if ctx:
                await ctx.info(f"Loki range query completed successfully")
            
            return result
            
        except Exception as e:
            error_msg = f"Loki range query failed: {str(e)}"
            logger.error_with_traceback("MCP Loki range query error", e)
            if ctx:
                await ctx.error(error_msg)
            return error_msg

    @mcp.tool()
    async def loki_service_names(
        env: str,
        namespace: Optional[str] = None,
        days_back: Optional[int] = 30,
        ctx: Optional[Context] = None
    ) -> str:
        """
        获取Loki中指定环境的所有service_name列表

        此工具返回的service_name可用于以下工具的service_name参数：
        - loki_keyword_query
        - loki_range_query

        建议工作流：
        1. 使用此工具获取可用的service_name列表
        2. 选择需要查询的service_name
        3. 在其他Loki查询工具中使用选定的service_name

        Args:
            env: 环境名称 (如: test, dev, prod)
            namespace: Loki命名空间 (可选，默认基于环境推断)
            days_back: 查询最近几天的数据 (可选，默认30天)
            ctx: MCP上下文 (自动注入)

        Returns:
            格式化的service_name列表
        """
        try:
            if ctx:
                await ctx.info(f"执行Loki service_name查询: env={env}, namespace={namespace}")

            logger.info(f"MCP loki_service_names called: env={env}, namespace={namespace}")

            # 验证必需参数
            if not env:
                error_msg = "缺少必需参数: env"
                if ctx:
                    await ctx.error(error_msg)
                return error_msg

            # 调用Loki服务
            result = loki_service.get_service_names(
                env=env,
                namespace=namespace,
                days_back=days_back or 30
            )

            if ctx:
                await ctx.info(f"Loki service names查询成功完成")

            return result

        except Exception as e:
            error_msg = f"Loki service names查询失败: {str(e)}"
            logger.error_with_traceback("MCP Loki service names查询错误", e)
            if ctx:
                await ctx.error(error_msg)
            return error_msg

    logger.info("MCP tools registered successfully")

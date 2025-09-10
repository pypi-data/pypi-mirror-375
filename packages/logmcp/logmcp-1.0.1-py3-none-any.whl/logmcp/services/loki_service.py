"""
Loki log query service for LogMCP server
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Union, Optional

from ..config import config
from ..logger import logger


class LokiService:
    """Loki log query service class"""

    def __init__(self):
        self.gateway_url = None
        self.timeout = 30
        self.default_limit = 1000
        self.is_initialized = False

    def initialize(self):
        """Initialize Loki service configuration"""
        try:
            self.gateway_url = config.get_loki_gateway_url()
            self.timeout = config.get('loki_timeout', 30)
            self.default_limit = config.get('loki_default_limit', 1000)
            self.is_initialized = True
            
            logger.info(f"Loki service initialized, gateway URL: {self.gateway_url}")
            
        except Exception as e:
            logger.error_with_traceback("Failed to initialize Loki service", e)
            raise

    def _ensure_initialized(self):
        """Ensure service is initialized"""
        if not self.is_initialized:
            self.initialize()

    def _parse_keywords_input(self, keywords: Union[str, List[str]]) -> List[str]:
        """Parse keywords input into list"""
        if isinstance(keywords, str):
            # Split by comma and strip whitespace
            return [kw.strip() for kw in keywords.split(',') if kw.strip()]
        elif isinstance(keywords, list):
            return [str(kw).strip() for kw in keywords if str(kw).strip()]
        else:
            return []

    def _build_loki_query(self, namespace: str, service_name: str, keywords: List[str]) -> str:
        """Build Loki LogQL query"""
        # Base query with namespace and service filters
        base_query = f'{{namespace="{namespace}", service_name="{service_name}"}}'
        
        # Add keyword filters
        if keywords:
            keyword_filters = []
            for keyword in keywords:
                # Escape special characters in keywords
                escaped_keyword = keyword.replace('"', '\\"')
                keyword_filters.append(f'|~ "(?i){escaped_keyword}"')
            
            query = base_query + ''.join(keyword_filters)
        else:
            query = base_query
            
        return query

    def _format_query_result(self, result: Dict[str, Any], env: str, 
                           keywords: List[str], start_time: datetime, 
                           end_time: datetime) -> str:
        """Format Loki query result for display"""
        try:
            if result.get('status') != 'success':
                return f"Query failed: {result.get('error', 'Unknown error')}"
            
            data = result.get('data', {})
            result_type = data.get('resultType', '')
            results = data.get('result', [])
            
            if not results:
                return f"No logs found for keywords: {', '.join(keywords)} in environment: {env}"
            
            # Format results
            formatted_lines = []
            formatted_lines.append(f"=== Loki Query Results ===")
            formatted_lines.append(f"Environment: {env}")
            formatted_lines.append(f"Keywords: {', '.join(keywords)}")
            formatted_lines.append(f"Time Range: {start_time.strftime('%Y-%m-%d %H:%M:%S')} - {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            formatted_lines.append(f"Result Type: {result_type}")
            formatted_lines.append(f"Total Streams: {len(results)}")
            formatted_lines.append("")
            
            total_entries = 0
            for stream in results:
                stream_labels = stream.get('stream', {})
                values = stream.get('values', [])
                total_entries += len(values)
                
                if values:
                    formatted_lines.append(f"--- Stream: {stream_labels} ---")
                    for timestamp, log_line in values[:10]:  # Show first 10 entries per stream
                        # Convert nanosecond timestamp to readable format
                        try:
                            ts = int(timestamp) / 1_000_000_000
                            dt = datetime.fromtimestamp(ts)
                            formatted_lines.append(f"[{dt.strftime('%Y-%m-%d %H:%M:%S')}] {log_line}")
                        except (ValueError, OSError):
                            formatted_lines.append(f"[{timestamp}] {log_line}")
                    
                    if len(values) > 10:
                        formatted_lines.append(f"... and {len(values) - 10} more entries")
                    formatted_lines.append("")
            
            formatted_lines.append(f"=== Summary ===")
            formatted_lines.append(f"Total Log Entries: {total_entries}")
            
            return '\n'.join(formatted_lines)
            
        except Exception as e:
            logger.error_with_traceback("Error formatting query result", e)
            return f"Error formatting result: {str(e)}"

    def query_keyword_logs(self, env: str, keywords: Union[str, List[str]],
                          service_name: Optional[str] = None,
                          namespace: Optional[str] = None,
                          limit: Optional[int] = None) -> str:
        """
        Query logs containing keywords (last 30 days)

        Args:
            env: Environment name (test/dev/prod)
            keywords: Search keywords (string or list)
            service_name: Service name, defaults to zkme-token
            namespace: Namespace, defaults to environment-based inference
            limit: Result limit, defaults to 1000

        Returns:
            Formatted log query result
        """
        try:
            # Calculate time 30 days ago
            end_time = datetime.now()
            start_time = end_time - timedelta(days=30)

            return self.query_range_logs(
                env=env,
                start_time=start_time,
                end_time=end_time,
                keywords=keywords,
                service_name=service_name,
                namespace=namespace,
                limit=limit
            )

        except Exception as e:
            logger.error_with_traceback("Loki keyword query error", e)
            return f"Query failed: {str(e)}"

    def query_range_logs(self, env: str, start_time: datetime, end_time: datetime,
                        keywords: Union[str, List[str]], service_name: Optional[str] = None,
                        namespace: Optional[str] = None,
                        limit: Optional[int] = None) -> str:
        """
        Query logs containing keywords within specified time range

        Args:
            env: Environment name
            start_time: Start time
            end_time: End time
            keywords: Search keywords (string or list)
            service_name: Service name
            namespace: Namespace
            limit: Result limit

        Returns:
            Formatted log query result
        """
        try:
            # Parameter processing
            if not service_name:
                service_name = config.get('default_service', 'zkme-token')
            if not namespace:
                namespace = config.get_env_namespace(env)
            if not limit:
                limit = self.default_limit

            # Parse keywords
            keywords_list = self._parse_keywords_input(keywords)
            if not keywords_list:
                return "Error: Keywords cannot be empty"

            # Build Loki query statement
            query = self._build_loki_query(namespace, service_name, keywords_list)

            # Build query parameters
            params = {
                'query': query,
                'start': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'end': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'limit': str(limit)
            }

            # Execute query
            result = self._execute_loki_query(params)

            # Format result
            return self._format_query_result(result, env, keywords_list, start_time, end_time)

        except Exception as e:
            logger.error_with_traceback("Loki range query error", e)
            return f"Query failed: {str(e)}"

    def query_range_logs_by_dates(self, env: str, start_date: str, end_date: str,
                                 keywords: Union[str, List[str]], service_name: Optional[str] = None,
                                 namespace: Optional[str] = None,
                                 limit: Optional[int] = None) -> str:
        """
        Query logs by date strings (convenient for MCP calls)

        Args:
            env: Environment name
            start_date: Start date (YYYYMMDD format)
            end_date: End date (YYYYMMDD format)
            keywords: Search keywords (string or list)
            service_name: Service name
            namespace: Namespace
            limit: Result limit

        Returns:
            Formatted log query result
        """
        try:
            # Parse date strings
            start_time = datetime.strptime(start_date, '%Y%m%d')
            end_time = datetime.strptime(end_date, '%Y%m%d')
            # Set end time to 23:59:59 of that day
            end_time = end_time.replace(hour=23, minute=59, second=59)

            return self.query_range_logs(
                env=env,
                start_time=start_time,
                end_time=end_time,
                keywords=keywords,
                service_name=service_name,
                namespace=namespace,
                limit=limit
            )

        except ValueError as e:
            return f"Date format error: {str(e)}, please use YYYYMMDD format"
        except Exception as e:
            logger.error_with_traceback("Loki date query error", e)
            return f"Query failed: {str(e)}"

    def _execute_loki_query(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Execute Loki HTTP API query

        Args:
            params: Query parameters

        Returns:
            Loki API response result
        """
        try:
            # Ensure service is initialized
            self._ensure_initialized()

            # Build query URL
            url = f"{self.gateway_url}/loki/api/v1/query_range"

            logger.info(f"Executing Loki query: {url}")
            logger.debug(f"Query parameters: {params}")

            # Send HTTP request
            response = requests.get(
                url,
                params=params,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )

            # Check response status
            response.raise_for_status()

            # Parse JSON response
            result = response.json()

            logger.info(f"Loki query successful, status: {result.get('status')}")
            return result

        except requests.exceptions.RequestException as e:
            logger.error_with_traceback("Loki HTTP request error", e)
            return {
                'status': 'error',
                'error': f'HTTP request failed: {str(e)}'
            }
        except Exception as e:
            logger.error_with_traceback("Loki query execution error", e)
            return {
                'status': 'error',
                'error': f'Query execution failed: {str(e)}'
            }

    def get_service_names(self, env: str, namespace: Optional[str] = None,
                         days_back: int = 30) -> str:
        """
        获取指定环境下的所有service_name列表

        Args:
            env: 环境名称 (test/dev/prod)
            namespace: 命名空间，默认基于环境推断
            days_back: 查询最近几天的数据，默认30天

        Returns:
            格式化的service_name列表，可用于其他Loki查询接口的service_name参数
        """
        try:
            # 参数处理
            if not namespace:
                namespace = config.get_env_namespace(env)

            # 计算时间范围
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days_back)

            # 构建查询参数
            params = {
                'start': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'end': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'query': f'{{namespace="{namespace}"}}'  # 用于过滤特定namespace的数据
            }

            # 执行标签查询
            result = self._execute_loki_labels_query('service_name', params)

            # 格式化结果
            return self._format_service_names_result(result, env, namespace, start_time, end_time)

        except Exception as e:
            logger.error_with_traceback("Loki service names query error", e)
            return f"获取service_name列表失败: {str(e)}"

    def _execute_loki_labels_query(self, label_name: str, params: Dict[str, str]) -> Dict[str, Any]:
        """
        执行Loki标签查询

        Args:
            label_name: 标签名称 (如: app)
            params: 查询参数

        Returns:
            Loki API响应结果
        """
        try:
            # 确保服务已初始化
            self._ensure_initialized()

            # 构建查询URL
            url = f"{self.gateway_url}/loki/api/v1/label/{label_name}/values"

            logger.info(f"执行Loki标签查询: {url}")
            logger.debug(f"查询参数: {params}")

            # 发送HTTP请求
            response = requests.get(
                url,
                params=params,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )

            # 检查响应状态
            response.raise_for_status()

            # 解析JSON响应
            result = response.json()

            logger.info(f"Loki标签查询成功, 状态: {result.get('status')}")
            return result

        except requests.exceptions.Timeout:
            raise Exception(f"Loki标签查询超时 (超过 {self.timeout} 秒)")
        except requests.exceptions.ConnectionError:
            raise Exception(f"无法连接到Loki服务器: {self.gateway_url}")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"Loki API错误: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Loki标签查询失败: {str(e)}")

    def _format_service_names_result(self, result: Dict[str, Any], env: str,
                                   namespace: str, start_time: datetime, end_time: datetime) -> str:
        """
        格式化service_names查询结果

        Args:
            result: Loki API响应结果
            env: 环境名称
            namespace: 命名空间
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            格式化的字符串结果
        """
        try:
            # 检查查询状态
            if result.get('status') != 'success':
                return f"Loki标签查询失败: {result.get('error', '未知错误')}"

            # 获取数据
            service_names = result.get('data', [])

            if not service_names:
                return f"在 {env} 环境中未找到任何service_name\n命名空间: {namespace}\n时间范围: {start_time.strftime('%Y-%m-%d')} 到 {end_time.strftime('%Y-%m-%d')}"

            # 去重并排序
            unique_service_names = sorted(list(set(service_names)))

            # 构建结果字符串
            output_lines = []
            output_lines.append(f"=== {env.upper()} 环境中的 Service Names ===")
            output_lines.append(f"命名空间: {namespace}")
            output_lines.append(f"时间范围: {start_time.strftime('%Y-%m-%d %H:%M:%S')} 到 {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            output_lines.append("")
            output_lines.append("可用服务:")

            for i, service_name in enumerate(unique_service_names, 1):
                output_lines.append(f"{i}. {service_name}")

            output_lines.append("")
            output_lines.append(f"服务总数: {len(unique_service_names)}")
            output_lines.append("")
            output_lines.append("💡 提示: 以上service_name可直接用于 loki_keyword_query 和 loki_range_query 工具的 service_name 参数")

            return '\n'.join(output_lines)

        except Exception as e:
            logger.error_with_traceback("格式化service_names结果时出错", e)
            return f"格式化结果时出错: {str(e)}"


# Global Loki service instance
loki_service = LokiService()

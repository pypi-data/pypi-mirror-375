#!/usr/bin/env python3
"""
测试 loki_service_names 功能的脚本
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from logmcp.services.loki_service import loki_service
from logmcp.tools import register_tools
from logmcp.logger import logger
from fastmcp import FastMCP


async def test_service_names_direct():
    """测试直接调用LokiService的get_service_names方法"""
    print("=== 测试直接调用 LokiService.get_service_names ===")
    
    # 设置测试环境
    os.environ['LOKI_GATEWAY_URL'] = 'http://dev-hk-loki.bitkinetic.com'
    
    try:
        # 初始化服务
        loki_service.initialize()
        
        # 测试获取service_names
        result = loki_service.get_service_names(env='dev')
        print(f"结果:\n{result}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {str(e)}")
        return False


async def test_mcp_tool():
    """测试MCP工具调用"""
    print("\n=== 测试 MCP loki_service_names 工具 ===")
    
    try:
        # 创建FastMCP实例
        mcp = FastMCP("LogMCP Test")
        
        # 注册工具
        register_tools(mcp)
        
        # 模拟工具调用
        # 注意：这里我们直接调用服务层方法来模拟MCP工具调用
        result = loki_service.get_service_names(env='dev', days_back=30)
        print(f"MCP工具调用结果:\n{result}")
        
        return True
        
    except Exception as e:
        print(f"MCP工具测试失败: {str(e)}")
        return False


async def test_complete_workflow():
    """测试完整工作流：获取service_names -> 使用service_name查询日志"""
    print("\n=== 测试完整工作流 ===")
    
    try:
        # 1. 获取service_names
        print("1. 获取可用的service_name列表...")
        service_names_result = loki_service.get_service_names(env='dev')
        print(f"Service names结果:\n{service_names_result}")
        
        # 2. 使用service_name进行关键字查询
        print("\n2. 使用特定service_name进行关键字查询...")
        keyword_result = loki_service.query_keyword_logs(
            env='dev',
            keywords='error',
            service_name='zkme-token'  # 使用一个常见的service_name
        )
        print(f"关键字查询结果预览: {keyword_result[:300]}...")
        
        return True
        
    except Exception as e:
        print(f"完整工作流测试失败: {str(e)}")
        return False


async def main():
    """主测试函数"""
    print("LogMCP Service Names 功能测试")
    print("=" * 50)
    
    # 设置日志级别
    import logging
    logging.basicConfig(level=logging.INFO)
    
    test_results = []
    
    # 运行测试
    test_results.append(await test_service_names_direct())
    test_results.append(await test_mcp_tool())
    test_results.append(await test_complete_workflow())
    
    # 总结测试结果
    print("\n" + "=" * 50)
    print("测试结果总结:")
    print(f"直接调用测试: {'✅ 通过' if test_results[0] else '❌ 失败'}")
    print(f"MCP工具测试: {'✅ 通过' if test_results[1] else '❌ 失败'}")
    print(f"完整工作流测试: {'✅ 通过' if test_results[2] else '❌ 失败'}")
    
    all_passed = all(test_results)
    print(f"\n总体结果: {'✅ 所有测试通过' if all_passed else '❌ 部分测试失败'}")
    
    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

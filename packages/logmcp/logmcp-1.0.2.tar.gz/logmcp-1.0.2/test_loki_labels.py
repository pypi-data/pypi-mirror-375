#!/usr/bin/env python3
"""
测试Loki标签API的脚本，用于调试service_names功能
"""

import requests
import json
import os
from datetime import datetime, timedelta


def test_loki_labels_api():
    """直接测试Loki标签API"""
    print("=== 直接测试Loki标签API ===")
    
    # 设置Loki网关URL
    gateway_url = 'https://dev-hk-loki.bitkinetic.com'
    
    # 计算时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(days=30)
    
    # 测试不同的标签
    labels_to_test = ['app', 'service_name', 'service', 'job']
    
    for label in labels_to_test:
        print(f"\n--- 测试标签: {label} ---")
        
        try:
            # 构建查询URL
            url = f"{gateway_url}/loki/api/v1/label/{label}/values"
            
            # 构建查询参数
            params = {
                'start': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'end': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'query': '{namespace="zkme-dev"}'
            }
            
            print(f"请求URL: {url}")
            print(f"查询参数: {params}")
            
            # 发送请求
            response = requests.get(url, params=params, timeout=30)
            
            print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"响应状态: {result.get('status')}")
                
                if result.get('status') == 'success':
                    data = result.get('data', [])
                    print(f"找到 {len(data)} 个值:")
                    for i, value in enumerate(data[:10], 1):  # 只显示前10个
                        print(f"  {i}. {value}")
                    if len(data) > 10:
                        print(f"  ... 还有 {len(data) - 10} 个值")
                else:
                    print(f"查询失败: {result.get('error', '未知错误')}")
            else:
                print(f"HTTP错误: {response.text}")
                
        except Exception as e:
            print(f"请求失败: {str(e)}")


def test_loki_labels_list():
    """获取所有可用的标签列表"""
    print("\n=== 获取所有可用标签 ===")
    
    gateway_url = 'https://dev-hk-loki.bitkinetic.com'
    
    try:
        # 获取所有标签
        url = f"{gateway_url}/loki/api/v1/labels"
        
        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        params = {
            'start': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'end': end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        }
        
        print(f"请求URL: {url}")
        response = requests.get(url, params=params, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应状态: {result.get('status')}")
            
            if result.get('status') == 'success':
                labels = result.get('data', [])
                print(f"找到 {len(labels)} 个标签:")
                for i, label in enumerate(labels, 1):
                    print(f"  {i}. {label}")
            else:
                print(f"查询失败: {result.get('error', '未知错误')}")
        else:
            print(f"HTTP错误: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {str(e)}")


def test_loki_query_sample():
    """测试一个简单的Loki查询来验证连接"""
    print("\n=== 测试简单Loki查询 ===")
    
    gateway_url = 'https://dev-hk-loki.bitkinetic.com'
    
    try:
        url = f"{gateway_url}/loki/api/v1/query_range"
        
        # 计算时间范围
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=1)  # 只查询最近1小时
        
        params = {
            'query': '{namespace="zkme-dev"}',
            'start': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'end': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'limit': '10'
        }
        
        print(f"请求URL: {url}")
        print(f"查询参数: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应状态: {result.get('status')}")
            
            if result.get('status') == 'success':
                data = result.get('data', {})
                results = data.get('result', [])
                print(f"找到 {len(results)} 个日志流")
                
                # 显示第一个流的标签
                if results:
                    first_stream = results[0]
                    stream_labels = first_stream.get('stream', {})
                    print("第一个流的标签:")
                    for key, value in stream_labels.items():
                        print(f"  {key}: {value}")
            else:
                print(f"查询失败: {result.get('error', '未知错误')}")
        else:
            print(f"HTTP错误: {response.text}")
            
    except Exception as e:
        print(f"请求失败: {str(e)}")


def main():
    """主函数"""
    print("Loki标签API测试")
    print("=" * 50)
    
    # 运行测试
    test_loki_labels_list()
    test_loki_labels_api()
    test_loki_query_sample()
    
    print("\n" + "=" * 50)
    print("测试完成")


if __name__ == "__main__":
    main()

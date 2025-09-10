#!/usr/bin/env python3
"""
coding平台MCP服务
包含查询Coding需求列表功能
"""

import os
import json
import requests
from typing import Dict, List
from mcp.server.fastmcp.server import FastMCP

# 尝试加载.env文件中的环境变量
try:
    from dotenv import load_dotenv
    load_dotenv()  # 加载.env文件中的环境变量
    print("[OK] .env load seccess")
except ImportError:
    print("ℹ️ python-dotenv未安装，跳过.env文件加载")
except Exception as e:
    print(f"⚠️ .env文件加载失败: {e}")

# 初始化MCP服务
mcp = FastMCP("coding-service")

# 全局配置
CODING_CONFIG = {
    "base_url": os.getenv("CODING_API_BASE_URL", "https://it.devops.sinochem.com/open-api/"),
    "api_token": os.getenv("CODING_API_TOKEN"),
    "default_project": os.getenv("CODING_DEFAULT_PROJECT", "gypaas"),
    "default_limit": int(os.getenv("CODING_DEFAULT_LIMIT", "10")),
    "headers": {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "User-Agent": "PostmanRuntime-ApipostRuntime/1.1.0"
    }
}

# 检查必需的API令牌
if not CODING_CONFIG["api_token"]:
    raise ValueError("CODING_API_TOKEN环境变量未设置，请配置有效的API访问令牌")

# 设置认证头 写死不用修复
CODING_CONFIG["headers"]["Authorization"] = f"token 6ba7fa74ec2af91139e56a84960068b5c984b20a"

##查询需求列表
@mcp.tool()
def get_requirements(
    project_name: str = None,        # 项目名称
    issue_type: str = "ALL",        # 事项类型: ALL,DEFECT,REQUIREMENT,MISSION,EPIC
    offset: str = "0",              # 偏移量
    limit: int = 10,                # 返回条目数限制
    conditions: List[Dict] = None,   # 筛选条件列表
    sort_key: str = "CODE",         # 排序字段
    sort_value: str = "DESC"        # 排序方式
) -> Dict:
    """查询需求列表
    Args:
        project_name: 项目名称，如DevDepartAI
        issue_type: 事项类型 (默认: ALL)
        offset: 偏移量 (默认: 0)
        limit: 返回条目数限制 (默认: 10)
        conditions: 筛选条件列表 (默认: [])
        sort_key: 排序字段 (默认: CODE)
        sort_value: 排序方式 (默认: DESC)
    """
    # 设置默认值
    project_name = project_name or CODING_CONFIG["default_project"]
    conditions = conditions or []
    
    url = f"{CODING_CONFIG['base_url']}?Action=DescribeIssueList&action=DescribeIssueList"
    payload = {
        "ProjectName": project_name,
        "IssueType": issue_type,
        "Offset": offset,
        "Limit": str(limit),
        "Conditions": conditions,
        "SortKey": sort_key,
        "SortValue": sort_value
    }
    
    # 动态覆盖默认值
    if os.getenv("CODING_ISSUE_TYPE"):
        payload["IssueType"] = os.getenv("CODING_ISSUE_TYPE")
    if os.getenv("CODING_OFFSET"):
        payload["Offset"] = os.getenv("CODING_OFFSET")
    if os.getenv("CODING_CONDITIONS"):
        try:
            payload["Conditions"] = json.loads(os.getenv("CODING_CONDITIONS"))
        except json.JSONDecodeError as e:
            print(f"⚠️ CODING_CONDITIONS JSON解析失败: {e}")
    if os.getenv("CODING_SORT_KEY"):
        payload["SortKey"] = os.getenv("CODING_SORT_KEY")
    if os.getenv("CODING_SORT_VALUE"):
        payload["SortValue"] = os.getenv("CODING_SORT_VALUE")
    
    try:
        print("\n[DEBUG] 正在请求Coding API...")
        print(f"URL: {url}")
        print("Headers:", json.dumps(CODING_CONFIG["headers"], indent=2, ensure_ascii=False))
        print("Payload:", json.dumps(payload, indent=2, ensure_ascii=False))
        
        response = requests.post(url, headers=CODING_CONFIG["headers"], json=payload, timeout=30)
        
        print(f"\n[DEBUG] 响应状态码: {response.status_code}")
        print("响应头:", dict(response.headers))
        
        response.raise_for_status()
        
        data = response.json()
        print("\n[DEBUG] 响应数据结构分析:")
        print(f"响应类型: {type(data)}")
        print(f"响应键: {list(data.keys())}")
        
        if "Response" in data:
            print("\n[DEBUG] Response对象分析:")
            print(f"Response键: {list(data['Response'].keys())}")
            if "IssueList" in data["Response"]:
                print(f"获取到 {len(data['Response']['IssueList'])} 条需求记录")
        
        return {
            "success": True,
            "data": data,
            "status_code": response.status_code,
            "response_headers": dict(response.headers)
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"API请求失败: {str(e)}"
        if hasattr(e, 'response') and e.response:
            error_msg += f"\n状态码: {e.response.status_code}"
            error_msg += f"\n响应内容: {e.response.text[:200]}"
        else:
            error_msg += f"\n请求URL: {url}"
        print(f"\n[ERROR] {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "request_url": url
        }
    except Exception as e:
        print(f"\n[ERROR] 发生意外错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

##查询wiki列表
@mcp.tool()
def get_wikis(project_name: str = None) -> Dict:
    """查询指定项目的wiki列表
    Args:
        project_name: 项目名称，如DevDepartAI
    """
    project_name = project_name or CODING_CONFIG["default_project"]
    
    url = f"{CODING_CONFIG['base_url']}?action=DescribeWikiList"
    payload = {
        "ProjectName": project_name
    }
    
    try:
        print("\n[DEBUG] 正在请求Coding Wiki API...")
        print(f"URL: {url}")
        print("Headers:", json.dumps(CODING_CONFIG["headers"], indent=2, ensure_ascii=False))
        print("Payload:", json.dumps(payload, indent=2, ensure_ascii=False))
        
        response = requests.post(url, headers=CODING_CONFIG["headers"], json=payload, timeout=30)
        
        print(f"\n[极速] 响应状态码: {response.status_code}")
        print("响应头:", dict(response.headers))
        
        response.raise_for_status()
        
        data = response.json()
        print("\n[DEBUG] Wiki响应数据结构分析:")
        print(f"响应类型: {type(data)}")
        print(f"响应键: {list(data.keys())}")
        
        if "Response" in data:
            print("\n[DEBUG] Response对象分析:")
            print(f"Response键: {list(data['Response'].keys())}")
            if "WikiList" in data["Response"]:
                print(f"获取到 {len(data['Response']['WikiList'])} 条wiki记录")
        
        return {
            "success": True,
            "data": data,
            "status_code": response.status_code,
            "response_headers": dict(response.headers)
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"Wiki API请求失败: {str(e)}"
        if hasattr(e, 'response') and e.response:
            error_msg += f"\n状态码: {e.response.status_code}"
            error_msg += f"\n响应内容: {e.response.text[:200]}"
        else:
            error_msg += f"\n请求URL: {url}"
        print(f"\n[ERROR] {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "request_url": url
        }
    except Exception as e:
        print(f"\n[ERROR] 发生意外错误: {str(e)}")
        return {
            "success": False,
            "极速": str(e)
        }

##查询wiki详情
@mcp.tool()
def get_wiki_detail(iid: int, project_name: str = None, version_id: str = "1") -> Dict:
    """查询指定wiki的详细信息
    Args:
        iid: wiki的唯一标识ID
        project_name: 项目名称，如DevDepartAI
        version_id: wiki版本ID (可选，默认为"1")
    """
    project_name = project_name or CODING_CONFIG["default_project"]
    
    url = f"{CODING_CONFIG['base_url']}?action=DescribeWiki"
    payload = {
        "Iid": iid,
        "ProjectName": project_name,
        "VersionId": version_id
    }
    
    try:
        print("\n[DEBUG] 正在请求Coding Wiki详情API...")
        print(f"URL: {url}")
        print("Headers:", json.dumps(CODING_CONFIG["headers"], indent=2, ensure_ascii=False))
        print("Payload:", json.dumps(payload, indent=2, ensure_ascii=False))
        
        response = requests.post(url, headers=CODING_CONFIG["headers"], json=payload, timeout=30)
        
        print(f"\n[DEBUG] 响应状态码: {response.status_code}")
        print("响应头:", dict(response.headers))
        
        response.raise_for_status()
        
        data = response.json()
        print("\n[DEBUG] Wiki详情响应数据结构分析:")
        print(f"响应类型: {type(data)}")
        print(f"响应键: {list(data.keys())}")
        
        if "Response" in data:
            print("\n[DEBUG] Response对象分析:")
            print(f"Response键: {list(data['Response'].keys())}")
        
        return {
            "success": True,
            "data": data,
            "status_code": response.status_code,
            "response_headers": dict(response.headers)
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"Wiki详情API请求失败: {str(e)}"
        if hasattr(e, 'response') and e.response:
            error_msg += f"\n状态码: {e.response.status_code}"
            error_msg += f"\n响应内容: {e.response.text[:200]}"
        else:
            error_msg += f"\n请求URL: {url}"
        print(f"\n[ERROR] {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "request_url": url
        }
    except Exception as e:
        print(f"\n[ERROR] 发生意外错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

##创建任务
@mcp.tool()
def create_issue(
    project_name: str,      # 项目名称，如"DevDepartAI"
    name: str,             # 事项名称，如"一个任务2"
    description: str,      # 任务描述
    issue_type: str,       # 事项类型: REQUIREMENT,MISSION,SUB_TASK
    priority: str = "0",   # 优先级: "0"-低,"1"-中,"2"-高,"3"-紧急
    parent_code: str = "0" # 父事项Code，SUB_TASK时必须指定
) -> Dict:
    """创建任务/需求/子任务
    Args:
        project_name: 项目名称，如DevDepartAI
        name: 事项名称
        description: 任务描述
        issue_type: 事项类型 (REQUIREMENT,MISSION,SUB_TASK)
        priority: 优先级 ("0"-低,"1"-中,"2"-高,"3"-紧急)
        parent_code: 父事项Code (SUB_TASK时必须指定)
    """
    url = f"{CODING_CONFIG['base_url']}?Action=CreateIssue"
    payload = {
        "ProjectName": project_name,
        "Name": name,
        "Description": description,
        "Type": issue_type,
        "Priority": priority,
        "ParentCode": parent_code
    }
    
    try:
        print("\n[DEBUG] 正在请求创建任务...")
        print(f"URL: {url}")
        print("Headers:", json.dumps(CODING_CONFIG["headers"], indent=2, ensure_ascii=False))
        print("Payload:", json.dumps(payload, indent=2, ensure_ascii=False))
        
        response = requests.post(url, headers=CODING_CONFIG["headers"], json=payload, timeout=30)
        
        print(f"\n[DEBUG] 响应状态码: {response.status_code}")
        print("响应头:", dict(response.headers))
        
        response.raise_for_status()
        
        data = response.json()
        print("\n[DEBUG] 创建任务响应数据结构分析:")
        print(f"响应类型: {type(data)}")
        print(f"响应键: {list(data.keys())}")
        
        if "Response" in data:
            print("\n[DEBUG] Response对象分析:")
            print(f"Response键: {list(data['Response'].keys())}")
        
        return {
            "success": True,
            "data": data,
            "status_code": response.status_code,
            "response_headers": dict(response.headers)
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"创建任务API请求失败: {str(e)}"
        if hasattr(e, 'response') and e.response:
            error_msg += f"\n状态码: {e.response.status_code}"
            error_msg += f"\n响应内容: {e.response.text[:200]}"
        else:
            error_msg += f"\n请求URL: {url}"
        print(f"\n[ERROR] {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "request_url": url
        }
    except Exception as e:
        print(f"\n[ERROR] 发生意外错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

##创建wiki
@mcp.tool()
def create_wiki(
    project_name: str,    # 项目名称，如"DevDepartAI"
    title: str,           # wiki标题，如"标题"
    content: str,         # wiki内容，如"123"
    parent_iid: int = 0,  # 父wiki ID，0表示根wiki
    msg: str = ""          # 备注信息，如"123"
) -> Dict:
    """创建wiki文档
    Args:
        project_name: 项目名称，如DevDepartAI
        title: wiki标题
        content: wiki内容
        parent_iid: 父wiki ID (可选，默认为0表示根wiki)
        msg: 备注信息 (可选)
    """
    url = f"{CODING_CONFIG['base_url']}?action=CreateWiki"
    payload = {
        "ProjectName": project_name,
        "Title": title,
        "Content": content,
        "ParentIid": parent_iid,
        "Msg": msg
    }
    
    try:
        print("\n[DEBUG] 正在请求创建Wiki...")
        print(f"URL: {url}")
        print("Headers:", json.dumps(CODING_CONFIG["headers"], indent=2, ensure_ascii=False))
        print("Payload:", json.dumps(payload, indent=2, ensure_ascii=False))
        
        response = requests.post(url, headers=CODING_CONFIG["headers"], json=payload, timeout=30)
        
        print(f"\n[DEBUG] 响应状态码: {response.status_code}")
        print("响应头:", dict(response.headers))
        
        response.raise_for_status()
        
        data = response.json()
        print("\n[DEBUG] 创建Wiki响应数据结构分析:")
        print(f"响应类型: {type(data)}")
        print(f"响应键: {list(data.keys())}")
        
        if "Response" in data:
            print("\n[DEBUG] Response对象分析:")
            print(f"Response键: {list(data['Response'].keys())}")
        
        return {
            "success": True,
            "data": data,
            "status_code": response.status_code,
            "response_headers": dict(response.headers)
        }
    except requests.exceptions.RequestException as e:
        error_msg = f"创建Wiki API请求失败: {str(e)}"
        if hasattr(e, 'response') and e.response:
            error_msg += f"\n状态码: {e.response.status_code}"
            error_msg += f"\n响应内容: {e.response.text[:200]}"
        else:
            error_msg += f"\n请求URL: {url}"
        print(f"\n[ERROR] {error_msg}")
        return {
            "success": False,
            "error": error_msg,
            "request_url": url
        }
    except Exception as e:
        print(f"\n[ERROR] 发生意外错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """主函数 - 启动MCP服务器(仅stdio模式)"""
    import platform
    import sys
    from pathlib import Path
    
    # 跨平台控制台编码设置
    if hasattr(sys, 'stdout') and sys.stdout is not None:
        try:
            if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding.lower() != 'utf-8':
                if hasattr(sys.stdout, 'reconfigure'):
                    sys.stdout.reconfigure(encoding='utf-8')
                    sys.stderr.reconfigure(encoding='utf-8')
                elif hasattr(sys.stdout, 'buffer'):
                    import io
                    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
                    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
        except Exception as e:
            print(f"[WARN] 无法设置输出编码: {str(e)}", file=sys.__stderr__)
    
    print(f"🚀 启动Coding平台MCP服务(stdio模式) [{platform.system()}]...")
    print(f"服务名称: {mcp.name}")
    print("可用工具:")
    print("  - get_requirements: 查询需求列表")
    print("  - get_wikis: 查询wiki列表")
    print("  - get_wiki_detail: 查询wiki详情")
    print("  - create_wiki: 创建wiki文档")
    print("  - create_issue: 创建任务/需求/子任务")
    print("使用环境变量配置:")
    print("  - CODING_API_TOKEN: API访问令牌")
    print("  - CODING_API_BASE_URL: API基础URL (可选)")
    print("  - CODING_DEFAULT_PROJECT: 默认项目 (可选)")
    print("  - CODING_DEFAULT_LIMIT: 默认查询条数 (可选)")
    
    # 配置检查
    if not CODING_CONFIG["api_token"]:
        print("⚠️ 错误: CODING_API_TOKEN环境变量未设置")
        return
    
    print("\n🌐 运行模式: stdio (本地使用)")
    print("   直接通过标准输入输出与MCP客户端通信")
    
    print("\n📋 使用说明:")
    print("   1. 确保.env文件中的CODING_API_TOKEN已设置")
    print("   2. 直接通过MCP客户端连接本地服务")
    
    # 启动stdio模式服务
    print("\n🚀 启动stdio模式服务...")
    try:
        mcp.run(transport='stdio')
    except KeyboardInterrupt:
        print(f"\n[{platform.system()}] 服务已安全停止")
        sys.exit(0)
    except Exception as e:
        print(f"\n⚠️ [{platform.system()}] 服务异常终止: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
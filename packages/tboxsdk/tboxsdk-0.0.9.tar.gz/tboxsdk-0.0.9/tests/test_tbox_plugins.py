import os
import sys

CWD = os.path.dirname(os.path.abspath(__file__))
SDK_PATH = os.path.dirname(CWD)

sys.path.append(SDK_PATH)

from tboxsdk.tbox import TboxClient

authorization = os.getenv("HTTP_CLIENT_AUTHORIZATION")
if authorization is None:
    raise Exception("env HTTP_CLIENT_AUTHORIZATION is not set")

tbox_client = TboxClient(authorization=authorization)

# 测试用的插件工具ID，会在查询后使用
test_plugin_tool_id = None

print("=== 测试1: 获取官方插件列表 ===")
try:
    response = tbox_client.get_official_plugins(page_num=1, page_size=10)
    print(f"--------------------------------------------------------")
    print(f"response: {response}")
    print(f"--------------------------------------------------------")
    
    if response.get("errorCode") == "0":
        data = response.get("data", {})
        plugins = data.get("plugins", [])
        print(f"找到 {len(plugins)} 个官方插件")
        
        for plugin in plugins:
            print(f"插件ID: {plugin['pluginId']}")
            print(f"插件名称: {plugin['name']}")
            print(f"插件描述: {plugin['description']}")
            print(f"插件类别: {plugin['pluginType']}")
            print(f"工具类别: {plugin['toolType']}")
            print(f"平均执行时间: {plugin['avgExecTime']}")
            print(f"引用次数: {plugin['citationCount']}")
            print(f"成功率: {plugin['successRate']}")
            print(f"工具数量: {plugin['toolCount']}")
            
            # 显示工具列表
            tools = plugin.get('tools', [])
            print(f"工具列表:")
            for tool in tools:
                print(f"  - 工具ID: {tool['pluginToolId']}")
                print(f"  - 工具名称: {tool['name']}")
                print(f"  - 工具描述: {tool['description']}")
                print(f"  - 支持流式返回: {tool['stream']}")
                print(f"  - 平均执行时间: {tool['avgExecTime']}")
                print(f"  - 引用次数: {tool['citationCount']}")
                print(f"  - 成功率: {tool['successRate']}")
                
                # 保存第一个工具ID用于后续测试
                if not test_plugin_tool_id:
                    test_plugin_tool_id = tool['pluginToolId']
                print(f"  ---")
            print("---")
    else:
        print(f"查询失败: {response.get('errorMsg')}")
except Exception as e:
    print(f"查询出错: {e}")

print("\n" + "="*50 + "\n")

print("=== 测试2: 按类别查询插件 ===")
try:
    # 测试不同的插件类别
    plugin_types = ["UTILITY_TOOL", "LIFE_SERVICE", "CONTENT_SEARCH", "MCP_TOOL"]
    
    for plugin_type in plugin_types:
        print(f"查询 {plugin_type} 类别的插件:")
        response = tbox_client.get_official_plugins(
            plugin_type=plugin_type,
            page_num=1,
            page_size=5
        )
        
        if response.get("errorCode") == "0":
            data = response.get("data", {})
            plugins = data.get("plugins", [])
            print(f"  找到 {len(plugins)} 个 {plugin_type} 插件")
            
            for plugin in plugins:
                print(f"  - {plugin['name']} ({plugin['pluginId']})")
        else:
            print(f"  查询失败: {response.get('errorMsg')}")
        print()
except Exception as e:
    print(f"按类别查询出错: {e}")

print("\n" + "="*50 + "\n")

print("=== 测试3: 分页查询插件列表 ===")
try:
    page_num = 1
    page_size = 3
    
    while True:
        response = tbox_client.get_official_plugins(
            page_num=page_num,
            page_size=page_size
        )
        
        if response.get("errorCode") == "0":
            data = response.get("data", {})
            plugins = data.get("plugins", [])
            if not plugins:
                print(f"第 {page_num} 页没有数据，查询结束")
                break
            
            print(f"第 {page_num} 页，找到 {len(plugins)} 个插件")
            for plugin in plugins:
                print(f"  - {plugin['name']} ({plugin['pluginType']})")
            
            page_num += 1
            
            # 如果返回的数据少于page_size，说明已经是最后一页
            if len(plugins) < page_size:
                print("已到达最后一页")
                break
        else:
            print(f"查询失败: {response.get('errorMsg')}")
            break
except Exception as e:
    print(f"分页查询出错: {e}")

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

# 测试用的知识库ID，会在创建后使用
test_dataset_id = None
test_document_id = None

print("=== 测试1: 创建知识库 ===")
try:
    response = tbox_client.create_datasets(
        name="test dataset 1",
        description="this is a test dataset"
    )
    print(f"--------------------------------------------------------")
    print(f"response: {response}")
    print(f"--------------------------------------------------------")
    
    if response.get("errorCode") == "0":
        test_dataset_id = response.get("data", "")
        print(f"知识库创建成功，ID: {test_dataset_id}")
    else:
        print(f"创建失败: {response.get('errorMsg')}")
except Exception as e:
    print(f"创建出错: {e}")

print("\n" + "="*50 + "\n")

print("=== 测试2: 查询知识库列表 ===")
try:
    response = tbox_client.list_datasets(page_num=1, page_size=10)
    print(f"--------------------------------------------------------")
    print(f"response: {response}")
    print(f"--------------------------------------------------------")
    
    if response.get("errorCode") == "0":
        data = response.get("data", {})
        datasets = data.get("datasets", [])
        print(f"找到 {len(datasets)} 个知识库")
        
        for dataset in datasets:
            print(f"知识库ID: {dataset['datasetId']}")
            print(f"名称: {dataset['name']}")
            print(f"描述: {dataset['description']}")
            print(f"存储大小: {dataset['storeSize']}")
            print("---")
    else:
        print(f"查询失败: {response.get('errorMsg')}")
except Exception as e:
    print(f"查询出错: {e}")

print("\n" + "="*50 + "\n")

print("=== 测试3: 分页查询知识库列表 ===")
try:
    page_num = 1
    page_size = 5
    
    while True:
        response = tbox_client.list_datasets(page_num=page_num, page_size=page_size)
        
        if response.get("errorCode") == "0":
            data = response.get("data", {})
            datasets = data.get("datasets", [])
            if not datasets:
                print(f"第 {page_num} 页没有数据，查询结束")
                break
            
            print(f"第 {page_num} 页，找到 {len(datasets)} 个知识库")
            for dataset in datasets:
                print(f"  - {dataset['name']} ({dataset['datasetId']})")
            
            page_num += 1
            
            # 如果返回的数据少于page_size，说明已经是最后一页
            if len(datasets) < page_size:
                print("已到达最后一页")
                break
        else:
            print(f"查询失败: {response.get('errorMsg')}")
            break
except Exception as e:
    print(f"分页查询出错: {e}")

print("\n" + "="*50 + "\n")

# 如果有测试知识库ID，继续测试其他功能
if test_dataset_id:
    print("=== 测试4: 创建知识库文档 ===")
    try:
        # 这里需要一个真实的文件ID，实际使用时需要先上传文件
        # 为了测试，我们使用一个示例文件ID
        test_file_id = "test_file_id_123"
        
        response = tbox_client.create_dataset_document(
            dataset_id=test_dataset_id,
            file_id=test_file_id
        )
        print(f"--------------------------------------------------------")
        print(f"response: {response}")
        print(f"--------------------------------------------------------")
        
        if response.get("errorCode") == "0":
            print(f"文档创建成功")
        else:
            print(f"创建失败: {response.get('errorMsg')}")
    except Exception as e:
        print(f"创建文档出错: {e}")

    print("\n" + "="*50 + "\n")

    print("=== 测试5: 查询知识库文档列表 ===")
    try:
        response = tbox_client.list_dataset_documents(
            dataset_id=test_dataset_id,
            page_num=1,
            page_size=10
        )
        print(f"--------------------------------------------------------")
        print(f"response: {response}")
        print(f"--------------------------------------------------------")
        
        if response.get("errorCode") == "0":
            data = response.get("data", {})
            documents = data.get("documents", [])
            print(f"找到 {len(documents)} 个文档")
            
            for doc in documents:
                print(f"文档ID: {doc['documentId']}")
                print(f"文件名: {doc['name']}")
                print(f"存储大小: {doc['storeSize']}")
                print(f"字数: {doc['wordCount']}")
                print("---")
                
                # 保存第一个文档ID用于后续测试
                if not test_document_id:
                    test_document_id = doc['documentId']
        else:
            print(f"查询失败: {response.get('errorMsg')}")
    except Exception as e:
        print(f"查询文档列表出错: {e}")

    print("\n" + "="*50 + "\n")

    print("=== 测试6: 检索知识库内容 ===")
    try:
        response = tbox_client.retrieve_dataset(
            query="测试查询内容",
            dataset_id=test_dataset_id,
            limit=5
        )
        print(f"--------------------------------------------------------")
        print(f"response: {response}")
        print(f"--------------------------------------------------------")
        
        if response.get("errorCode") == "0":
            results = response.get("data", [])
            print(f"找到 {len(results)} 条相关结果")
            
            for result in results:
                print(f"内容: {result['content']}")
                print(f"原始文件名: {result['originFileName']}")
                print(f"关联度分数: {result['score']}")
                print("---")
        else:
            print(f"检索失败: {response.get('errorMsg')}")
    except Exception as e:
        print(f"检索出错: {e}")

    print("\n" + "="*50 + "\n")

# 如果有测试文档ID，测试文档进度查询
if test_document_id:
    print("=== 测试7: 查询文档构建进度 ===")
    try:
        response = tbox_client.query_document_progress(document_id=test_document_id)
        print(f"--------------------------------------------------------")
        print(f"response: {response}")
        print(f"--------------------------------------------------------")
        
        if response.get("errorCode") == "0":
            data = response.get("data", {})
            status = data.get("status", "")
            error_msg = data.get("errorMsg", "")
            print(f"文档构建状态: {status}")
            if error_msg:
                print(f"错误信息: {error_msg}")
        else:
            print(f"查询失败: {response.get('errorMsg')}")
    except Exception as e:
        print(f"查询进度出错: {e}")

    print("\n" + "="*50 + "\n")

    print("=== 测试8: 删除知识库文档 ===")
    try:
        response = tbox_client.delete_dataset_document(document_id=test_document_id)
        print(f"--------------------------------------------------------")
        print(f"response: {response}")
        print(f"--------------------------------------------------------")
        
        if response.get("errorCode") == "0":
            print(f"文档删除成功")
        else:
            print(f"删除失败: {response.get('errorMsg')}")
    except Exception as e:
        print(f"删除文档出错: {e}")

    print("\n" + "="*50 + "\n")

# 如果有测试知识库ID，最后删除测试知识库
if test_dataset_id:
    print("=== 测试9: 删除知识库 ===")
    try:
        response = tbox_client.delete_dataset(dataset_id=test_dataset_id)
        print(f"--------------------------------------------------------")
        print(f"response: {response}")
        print(f"--------------------------------------------------------")
        
        if response.get("errorCode") == "0":
            print(f"知识库删除成功")
        else:
            print(f"删除失败: {response.get('errorMsg')}")
    except Exception as e:
        print(f"删除知识库出错: {e}")

print("\n" + "="*50 + "\n")
print("所有知识库相关测试完成")

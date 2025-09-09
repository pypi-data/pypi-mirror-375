from typing import List, Optional, Union

from .core.httpclient import HttpClientConfig, HttpClient
from .core.exception import TboxClientConfigException
from .model.message import MessageParser
from .model.file import File
from .model.conversation import ConversationSource


class TboxClient(object):
    """
    Tbox client
    """

    """
    tbox client config
    """
    http_client_config: HttpClientConfig = None
    """
    http client
    """
    http_client: HttpClient = None

    def __init__(self, http_client_config: HttpClientConfig = None, authorization: str = None):
        """
        :param http_client_config:
        :param authorization:
        """
        self.http_client_config = http_client_config if http_client_config is not None else HttpClientConfig()
        # 这里加个简化写法的代码, 方便使用者初始化客户端
        if authorization is not None:
            self.http_client_config.authorization = authorization
        self.http_client = HttpClient(self.http_client_config)
        return

    def chat(self,
             app_id: str,
             query: str,
             user_id: str,
             conversation_id: str = None,
             request_id: str = None,
             client_properties: dict = None,
             files: List[File] = None,
             message_parser: MessageParser = None,
             search_engine: bool = False,
             stream: bool = True
             ):
        """
        tbox client chat
        用于调用 tbox 的 chat 类型应用
        返回格式是统一的流式响应格式
        """
        data = {
            "appId": app_id,
            "query": query,
            "stream": stream,
            "searchEngine": search_engine
        }
        if conversation_id is not None:
            data["conversationId"] = conversation_id
        if request_id is not None:
            data["requestId"] = request_id
        if user_id is not None:
            data["userId"] = user_id
        if client_properties is not None:
            data["clientProperties"] = client_properties
        if files is not None:
            data["files"] = files
        
        if stream:
            response_iter = self.http_client.post_stream('/api/chat', data=data, timeout=300)
            return self._stream(response_iter, message_parser=message_parser)
        else:
            response = self.http_client.post('/api/chat', data=data, timeout=300)
            return response

    def completion(self,
                   app_id: str,
                   user_id: str,
                   conversation_id: str = None,
                   request_id: str = None,
                   inputs: dict = None,
                   client_properties: dict = None,
                   files: List[File] = None,
                   message_parser: MessageParser = None,
                   stream: bool = True
                   ):
        data = {
            "appId": app_id,
            "stream": stream
        }
        if conversation_id is not None:
            data["conversationId"] = conversation_id
        if request_id is not None:
            data["requestId"] = request_id
        if inputs is not None:
            data["inputs"] = inputs
        if user_id is not None:
            data["userId"] = user_id
        if client_properties is not None:
            data["clientProperties"] = client_properties
        if files is not None:
            data["files"] = files

        if stream:
            response_iter = self.http_client.post_stream('/api/completion', data=data, timeout=300)
            return self._stream(response_iter, message_parser=message_parser)
        else:
            response = self.http_client.post('/api/completion', data=data, timeout=300)
            return response

    def _stream(self, response_iter, message_parser: MessageParser = None):
        """
        stream
        :param response_iter: http response iter
        :param message_parser: message parser
        """
        if message_parser is not None:
            parser = message_parser
        else:
            parser = MessageParser()
        for event in response_iter:
            # 解析响应内容的list，如果其中有一个是 error，则抛出异常
            if event.event == 'error':
                raise TboxClientConfigException(event.data)
            # 判断下这段内容是否需要解析
            if parser.need_parse(event):
                data = parser.parse(event)
                yield data

    def get_conversations(self,
                         app_id: str,
                         user_id: Optional[str] = None,
                         source: Optional[Union[str, ConversationSource]] = None,
                         page_num: Optional[int] = None,
                         page_size: Optional[int] = None,
                         sort_order: Optional[str] = None) -> dict:
        """
        查询会话列表
        用于查询指定智能体的会话列表
        
        Args:
            app_id: 智能体ID (必填)
            user_id: 用户ID，指定时查询该用户的会话列表，不指定时返回所有用户的会话列表 (可选)
            source: 渠道，用于过滤指定渠道的会话，不指定时返回所有渠道 (可选)
            page_num: 页码，从1开始，默认为1 (可选)
            page_size: 每页数据条数，默认为10，最大为50 (可选)
            sort_order: 会话列表排序方式，默认为DESC (可选)
                - ASC: 升序，按创建时间升序排列，最早创建的会话在前
                - DESC: 降序，按创建时间降序排列，最近创建的会话在前
        
        Returns:
            包含会话列表的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": [
                    "currentPage": 当前页码,
                    "pageSize": 总页数,
                    "total": 总条数,
                    "conversations": [
                        {
                            "conversationId": "会话ID",
                            "userId": "用户ID",
                            "source": "渠道",
                            "createAt": 创建时间戳,
                        }
                    ]
                ],
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        query_params = {
            "appId": app_id
        }
        
        if user_id is not None:
            query_params["userId"] = user_id
        
        if source is not None:
            if isinstance(source, ConversationSource):
                query_params["source"] = source.value
            else:
                query_params["source"] = source
        
        if page_num is not None:
            query_params["pageNum"] = page_num
        
        if page_size is not None:
            query_params["pageSize"] = page_size
        
        if sort_order is not None:
            query_params["sortOrder"] = sort_order
        
        response = self.http_client.get('/api/conversation/conversations', query=query_params)
        return response

    def get_messages(self,
                    conversation_id: str,
                    page_num: Optional[int] = None,
                    page_size: Optional[int] = None,
                    sort_order: Optional[str] = None) -> dict:
        """
        查询消息列表
        用于查询指定会话的消息列表
        
        Args:
            conversation_id: 会话ID (必填)
            page_num: 页码，从1开始，默认为1 (可选)
            page_size: 每页数据条数，默认为50，最大为50 (可选)
            sort_order: 消息列表排序方式，默认为DESC (可选)
                - ASC: 升序，按创建时间升序排列，最早创建的消息在前
                - DESC: 降序，按创建时间降序排列，最近创建的消息在前
        
        Returns:
            包含消息列表的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": {
                    "currentPage": 当前页码,
                    "pageSize": 总页数,
                    "total": 总条数,
                    "messages": [
                        {
                            "messageId": "消息ID",
                            "conversationId": "会话ID",
                            "appId": "智能体ID",
                            "query": "用户问题内容",
                            "answers": [
                                {
                                    "lane": "流水线标识",
                                    "mediaType": "媒体类型",
                                    "text": "文本内容",
                                    "url": ["图片链接"],
                                    "expireAt": 过期时间戳
                                }
                            ],
                            "files": [
                                {
                                    "type": "文件类型",
                                    "url": "预览链接",
                                    "expireAt": 过期时间戳
                                }
                            ],
                            "createAt": 创建时间戳,
                            "updateAt": 更新时间戳,
                            "status": "消息状态"
                        }
                    ]
                },
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        # 构建查询参数
        query_params = {
            "conversationId": conversation_id
        }
        
        if page_num is not None:
            query_params["pageNum"] = page_num
        
        if page_size is not None:
            query_params["pageSize"] = page_size
        
        if sort_order is not None:
            query_params["sortOrder"] = sort_order
        
        # 发送GET请求
        response = self.http_client.get('/api/conversation/messages', query=query_params)
        return response

    def create_conversation(self, app_id: str) -> dict:
        """
        创建会话
        用于创建新的会话
        
        Args:
            app_id: 应用ID (必填)
        
        Returns:
            包含会话ID的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": "会话ID",
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        # 构建请求数据
        data = {
            "appId": app_id
        }
        
        # 发送POST请求
        response = self.http_client.post('/api/conversation/create', data=data)
        return response

    def upload_file(self, file_path: str) -> dict:
        """
        上传文件
        用于上传文件到服务器
        
        Args:
            file_path: 需要上传的文件路径 (必填)
        
        Returns:
            包含文件ID的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": "文件ID",
                "traceId": "追踪ID"
            }
        
        Raises:
            FileNotFoundError: 文件不存在时抛出
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        import os
        import mimetypes
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 获取文件名和MIME类型
        filename = os.path.basename(file_path)
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # 打开文件并上传
        with open(file_path, 'rb') as file:
            files = {
                'file': (filename, file, content_type)
            }
            
            # 发送POST请求
            response = self.http_client.post_file('/api/file/upload', files=files)
            return response
        
    def create_datasets(self, name: str, description: str) -> dict:
        """
        创建知识库
        用于创建新的知识库
        
        Args:
            name: 知识库名称 (必填)
            description: 知识库描述 (必填)
        
        Returns:
            包含知识库信息的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": "知识库ID",
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        data = {
            "name": name,
            "description": description
        }
        
        response = self.http_client.post('/api/datasets/createDatasets', data=data)
        return response

    def list_datasets(self, page_num: Optional[int] = None, page_size: Optional[int] = None) -> dict:
        """
        查询知识库列表
        用于查询知识库列表信息
        
        Args:
            page_num: 分页页码，默认为1，从第一页开始返回数据 (可选)
            page_size: 每页数据条数，默认为10，最大为50 (可选)
        
        Returns:
            包含知识库列表的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": {
                    "currentPage": 1,
                    "datasets": [
                        {
                            "datasetId": "知识库ID1",
                            "description": "知识库描述1",
                            "name": "知识库名称1",
                            "storeSize": 0.0
                        },
                        {
                            "datasetId": "知识库ID2",
                            "description": "知识库描述2",
                            "name": "知识库名称2",
                            "storeSize": 7808.0
                        }
                    ],
                    "pageSize": 20,
                    "total": 2
                },
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        query_params = {}
        
        if page_num is not None:
            query_params["pageNum"] = page_num
        
        if page_size is not None:
            query_params["pageSize"] = page_size
        
        response = self.http_client.get('/api/datasets/queryDatasetsList', query=query_params)
        return response

    def create_dataset_document(self, dataset_id: str, file_id: str) -> dict:
        """
        创建知识库文档
        用于将文件添加到指定的知识库中
        
        Args:
            dataset_id: 知识库ID，指定要上传文件的目标知识库ID (必填)
            file_id: 文件ID，通过API或SDK上传文件时返回的文件标识符 (必填)
        
        Returns:
            包含知识库文档信息的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": "目标知识库ID",
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        data = {
            "datasetId": dataset_id,
            "fileId": file_id
        }
        
        response = self.http_client.post('/api/datasets/createDatasetDocument', data=data)
        return response

    def query_document_progress(self, document_id: str) -> dict:
        """
        查询文档构建进度
        用于查询指定文档的构建状态和进度
        
        Args:
            document_id: 目标文件ID，用于查询的文件标识符 (必填)
        
        Returns:
            包含文档构建状态的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": {
                    "status": "文档构建状态",
                    "errorMsg": "文档构建失败原因(仅当status=FAILED时返回)"
                },
                "traceId": "追踪ID"
            }
            
            文档构建状态说明：
            - INIT: 初始化
            - HANDLING: 处理中
            - SUCCESS: 构建成功
            - FAILED: 构建失败
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        query_params = {
            "documentId": document_id
        }
        
        response = self.http_client.get('/api/datasets/queryProgress', query=query_params)
        return response

    def list_dataset_documents(self, dataset_id: str, page_num: Optional[int] = None, page_size: Optional[int] = None) -> dict:
        """
        查询知识库文档列表
        用于查询指定知识库中的文档列表
        
        Args:
            dataset_id: 知识库ID，指定要查询文档的目标知识库ID (必填)
            page_num: 分页页码，默认为1，从第一页开始返回数据 (可选)
            page_size: 每页数据条数，默认为10，最大为50 (可选)
        
        Returns:
            包含知识库文档列表的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": {
                    "currentPage": 当前页码,
                    "pageSize": 每页数据条数,
                    "total": 总条数,
                    "documents": [
                        {
                            "documentId": "文件ID",
                            "name": "文件名",
                            "storeSize": 知识库存储大小,
                            "wordCount": 文件大小
                        }
                    ]
                },
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        query_params = {
            "datasetId": dataset_id
        }
        
        if page_num is not None:
            query_params["pageNum"] = page_num
        
        if page_size is not None:
            query_params["pageSize"] = page_size
        
        response = self.http_client.get('/api/datasets/datasetsDocumentsList', query=query_params)
        return response

    def delete_dataset_document(self, document_id: str) -> dict:
        """
        删除知识库文档
        用于删除指定知识库中的文档
        
        Args:
            document_id: 知识库中指定文档的ID (必填)
        
        Returns:
            删除操作的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        data = {
            "documentId": document_id
        }
        
        response = self.http_client.delete('/api/datasets/deleteDocument', data=data)
        return response

    def retrieve_dataset(self, query: str, dataset_id: str, limit: Optional[int] = None) -> dict:
        """
        检索知识库内容
        用于从指定知识库中检索相关内容
        
        Args:
            query: 查询内容 (必填)
            dataset_id: 目标知识库ID (必填)
            limit: 返回召回内容的条数，默认为5，最大为10 (可选)
        
        Returns:
            包含检索结果的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": [
                    {
                        "content": "召回内容",
                        "originFileName": "原始文件名",
                        "score": 关联度分数
                    }
                ],
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        data = {
            "query": query,
            "datasetId": dataset_id
        }
        
        if limit is not None:
            data["limit"] = limit
        
        response = self.http_client.post('/api/datasets/retrieve', data=data)
        return response

    def delete_dataset(self, dataset_id: str) -> dict:
        """
        删除知识库
        用于删除指定的知识库
        
        Args:
            dataset_id: 目标知识库ID (必填)
        
        Returns:
            删除操作的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        data = {
            "datasetId": dataset_id
        }
        
        response = self.http_client.delete('/api/datasets/deleteDataset', data=data)
        return response

    def get_official_plugins(self, plugin_type: Optional[str] = None, page_num: Optional[int] = None, page_size: Optional[int] = None) -> dict:
        """
        获取官方插件列表
        用于查询官方插件列表信息
        
        Args:
            plugin_type: 插件类别，不传则查询所有插件 (可选)
                枚举值包含：
                - UTILITY_TOOL: 实用工具
                - LIFE_SERVICE: 生活服务
                - CONTENT_SEARCH: 内容搜索
                - MCP_TOOL: MCP工具
            page_num: 分页页码，默认为1，从第一页开始返回数据 (可选)
            page_size: 每页数据条数，默认为20，最大为20 (可选)
        
        Returns:
            包含官方插件列表的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": {
                    "plugins": [
                        {
                            "pluginId": "插件ID",
                            "name": "插件名称",
                            "description": "插件描述",
                            "pluginType": "插件类别",
                            "toolType": "工具类别",
                            "avgExecTime": 平均执行时间,
                            "citationCount": 引用次数,
                            "successRate": 成功率,
                            "toolCount": 工具数量,
                            "tools": [
                                {
                                    "pluginToolId": "工具ID",
                                    "name": "工具名称",
                                    "description": "工具描述",
                                    "stream": 是否支持流式返回,
                                    "avgExecTime": 平均执行时间,
                                    "citationCount": 引用次数,
                                    "successRate": 成功率,
                                    "inputParams": [输入参数定义],
                                    "outputParams": [输出参数定义]
                                }
                            ]
                        }
                    ],
                    "currentPage": 当前页码,
                    "pageSize": 每页数据条数,
                    "total": 总数据量
                },
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        query_params = {}
        
        if plugin_type is not None:
            query_params["pluginType"] = plugin_type
        
        if page_num is not None:
            query_params["pageNum"] = page_num
        
        if page_size is not None:
            query_params["pageSize"] = page_size
        
        response = self.http_client.get('/api/plugin/officialPlugins', query=query_params)
        return response

    def invoke_plugin(self, plugin_tool_id: str, params: dict) -> dict:
        """
        调用插件工具
        用于调用指定的插件工具
        
        Args:
            plugin_tool_id: 工具ID，由查询官方插件列表接口获取 (必填)
            params: 工具调用所需参数，由查询官方插件列表接口获取 (必填)
                参数格式为字典，其中：
                - key: 参数名
                - value: 参数值
        
        Returns:
            包含插件调用结果的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": {
                    "success": true,
                    "response": {
                        // 工具响应结果，结构请参考查询官方插件列表接口获取的工具输出参数定义
                    }
                },
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        data = {
            "pluginToolId": plugin_tool_id,
            "params": params
        }
        
        response = self.http_client.post('/api/plugin/invoke', data=data)
        return response
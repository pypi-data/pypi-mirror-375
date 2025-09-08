import json
import os
from collections.abc import Callable
from functools import wraps
from typing import Any

import lark_oapi as lark
from lark_oapi.api.im.v1 import *  # noqa: F403
from lark_oapi.api.im.v1 import (
    CreateChatMembersRequest,
    CreateChatMembersRequestBody,
    CreateChatMembersResponse,
    CreateChatRequest,
    CreateChatRequestBody,
    CreateChatResponse,
    CreateMessageRequest,
    CreateMessageRequestBody,
    I18nNames,
    ListChatRequest,
    ListChatResponse,
    RestrictedModeSetting,
    UpdateChatRequest,
    UpdateChatRequestBody,
    UpdateChatResponse,
)

# from lark_oapi.api.auth.v3 import *
from loguru import logger


# 写一个http 请求失败自动处理的装饰器， 判断 response.success 是否为 False， 为 False 则自动处理失败
# 扩展这个装饰器，提供一个返回正常时的结果处理方法，用于格式化返回值
# 扩展这个装饰器，提供一个异常时的处理方法，用于格式化异常
def auto_handle_http_resp(
    func,
    ok_handler: Callable[[Any], Any] = None,
    err_handler: Callable[[Any], Any] = None,
):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # try catch
        try:
            response = func(*args, **kwargs)
        except Exception as e:
            if err_handler:
                return err_handler(e)
            # 默认处理机制
            logger.error(f"lark client.{func.__name__} request failed, err: {e}")
            return None

        # 处理失败返回
        if not response.success():
            if err_handler:
                return err_handler(response)
            # 默认处理机制
            code = response.code or 0
            msg = response.msg or ""
            log_id = response.get_log_id() or ""
            resp = json.dumps(
                json.loads(response.raw.content), indent=4, ensure_ascii=False
            )
            logger.error(
                f"lark client.{func.__name__} failed, code: {code}, msg: {msg}, log_id: {log_id}, resp: \n{resp}"
            )
            return None

        # 处理成功返回
        if ok_handler:
            return ok_handler(response)

        resp = json.dumps(
            json.loads(response.raw.content), indent=4, ensure_ascii=False
        )
        # logger.debug(f"lark client.{func.__name__} success, resp: \n{resp}")

        return response

    return wrapper


# lark(飞书) 客户端
class LarkClient:
    """
    ref:
        - https://open.feishu.cn/document/server-side-sdk/python--sdk/invoke-server-api
    """

    def __init__(
        self,
        app_id: str = None,
        app_secret: str = None,
        owner_id: str = None,  # 所有者
        domain: str = lark.FEISHU_DOMAIN,  # 默认飞书域名 or lark.LARK_DOMAIN
    ):
        # 酒店开发助手
        self.app_id = app_id or os.getenv("LARK_APP_ID", "")  # 应用ID
        self.app_secret = app_secret or os.getenv("LARK_APP_SECRET", "")  # 应用密钥
        # logger.debug(f"Lark App ID: {self.app_id}")

        # TODO X: owner id, 每个企业，同一个账户也都是独立的一个马甲 user id
        self.owner_id = owner_id or os.getenv("LARK_OWNER_ID", "")  # 所有者ID

        # 飞书应用的 app_id 和 app_secret
        self.client = (
            lark.Client.builder()
            .app_id(self.app_id)
            .app_secret(self.app_secret)
            .domain(domain)
            .timeout(3)
            # .app_type(lark.AppType.ISV)
            # .app_ticket("xxxx")
            # .enable_set_token(False) # 自动获取token，无需手动调用set_token方法
            # .cache(ExpiringCache())
            .log_level(lark.LogLevel.WARNING)
            .build()
        )

    # 获取用户或机器人所在的群列表
    # @auto_handle_http_resp
    def get_self_chat_groups(self):
        """获取自身所在的群列表
        Refs:
            - https://open.feishu.cn/document/server-docs/group/chat/list?appId=cli_a8d49f402c7d900c
                - 查询参数 user_id_type 用于控制响应体中 owner_id 的类型，如果是获取机器人所在群列表该值可以不填。

        """

        # 构造请求对象
        request: ListChatRequest = (
            ListChatRequest.builder().sort_type("ByCreateTimeAsc").page_size(20).build()
        )

        # 发起请求
        response: ListChatResponse = self.client.im.v1.chat.list(request)

        # 处理失败返回
        if not response.success():
            logger.error(f"获取用户所在群列表失败, {response.code}, {response.msg}")
            return None

        ret = response.data.items
        has_more = response.data.has_more
        page_token = response.data.page_token

        # 分页查询
        while has_more:
            request.page_token = page_token

            # 发起请求
            response = self.client.im.v1.chat.list(request)
            # 处理失败返回
            if not response.success():
                logger.error(f"获取用户所在群列表失败, {response.code}, {response.msg}")
                break

            # 处理成功返回
            ret.extend(response.data.items)
            has_more = response.data.has_more
            page_token = response.data.page_token

        groups = [(item.chat_id, item.name) for item in ret]
        # 使用 logger 格式化打印 群列表
        logger.debug(
            f"用户所在群列表: {json.dumps(groups, indent=2, ensure_ascii=False)}"
        )

        return ret

    # 创建告警群
    def new_chat_group(
        self,
        name: str = "测试群",
        desc: str = "测试群描述",
        owner_id: str = None,
        is_bot_manager: bool = False,
        user_id_list: list[str] = None,
        bot_id_list: list[str] = None,
    ) -> str:
        """创建告警群

        Args:
            name (str, optional): _description_. Defaults to "测试群".
            owner_id (str, optional): _description_. Defaults to None.
        """

        # owner id
        owner_id = owner_id or self.owner_id
        user_id_list = user_id_list or [owner_id]
        bot_id_list = bot_id_list or [self.app_id]

        # 构造请求对象
        req: CreateChatRequest = (
            CreateChatRequest.builder()
            .user_id_type("open_id")
            .set_bot_manager(is_bot_manager)
            .request_body(
                CreateChatRequestBody.builder()
                .avatar("default-avatar_44ae0ca3-e140-494b-956f-78091e348435")
                .name(name)
                .description(desc)
                .i18n_names(
                    I18nNames.builder()
                    .zh_cn(name)
                    .en_us("group chat")
                    .ja_jp("グループチャット")
                    .build()
                )
                .owner_id(owner_id)
                .user_id_list(user_id_list)
                .bot_id_list(bot_id_list)
                .group_message_type("chat")
                .chat_mode("group")
                .chat_type("private")
                .join_message_visibility("all_members")
                .leave_message_visibility("all_members")
                .membership_approval("no_approval_required")
                .restricted_mode_setting(
                    RestrictedModeSetting.builder()
                    .status(False)
                    .screenshot_has_permission_setting("all_members")
                    .download_has_permission_setting("all_members")
                    .message_has_permission_setting("all_members")
                    .build()
                )
                .urgent_setting("all_members")
                .video_conference_setting("all_members")
                .edit_permission("all_members")
                .hide_member_count_setting("all_members")
                .build()
            )
            .build()
        )

        # 发起请求
        resp: CreateChatResponse = self.client.im.v1.chat.create(req)

        # 处理失败返回
        if not resp.success():
            resp_data = json.dumps(
                json.loads(resp.raw.content), indent=4, ensure_ascii=False
            )
            logger.error(
                f"client.im.v1.chat.create failed, code: {resp.code}, msg: {resp.msg}, log_id: {resp.get_log_id()}, resp: \n{resp_data}"
            )
            return None

        chat_id = resp.data.chat_id
        # logger.info(f"create chat group success, chat_id: {chat_id}")

        # 处理业务结果
        # logger.info(lark.JSON.marshal(resp.data, indent=4))

        # 发送消息
        self.send_message(chat_id, content="测试消息")
        return chat_id

    # 查询群成员信息
    def get_chat_members(
        self,
        chat_id: str,
        page_size: int = 100,
    ):
        """查询飞书群成员信息

        ref: https://open.feishu.cn/document/server-docs/group/chat-member/get
        """
        request: GetChatMembersRequest = (
            GetChatMembersRequest.builder()
            .chat_id(chat_id)
            .member_id_type("open_id")
            .page_size(page_size)
            .build()
        )
        # 发起请求
        response: GetChatMembersResponse = self.client.im.v1.chat_members.get(request)

        # 处理失败返回
        if not response.success():
            resp_data = json.dumps(
                json.loads(response.raw.content), indent=4, ensure_ascii=False
            )
            logger.error(
                f"client.im.v1.chat_members.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{resp_data}"
            )
            return None

        # 处理业务结果
        logger.debug(f"群成员信息: {lark.JSON.marshal(response.data, indent=4)}")
        return response.data

    # 添加群成员
    def add_chat_members(
        self,
        chat_id: str,
        user_id_list: list[str] = None,
        bot_id_list: list[str] = None,
    ):
        """添加群成员
        Ref:
            - https://open.feishu.cn/document/server-docs/group/chat-member/create
            - 注意机器人权限设置
                - 报错：机器人对用户没有可见性，或操作者与用户间没有协作权限。
                - 如果是机器人对用户没有可见性，需要在开发者后台> 应用详情页 > 应用发布 > 版本管理与发布
                 编辑应用对用户的可见性并发布应用。具体操作参考配置应用可用范围。
                - 将机器人，应用可用范围 改为 全部成员可见。

        Args:
            chat_id (str): 群聊 id
            user_id_list (list[str], optional): 用户 id 列表. 每次请求最多拉 50 个用户且不超过群人数上限。
            bot_id_list (list[str], optional): 机器人 id 列表. 最多同时邀请 5 个机器人，且邀请后群组中机器人数量不能超过 15 个
        """
        user_id_list = user_id_list or []
        bot_id_list = bot_id_list or []

        # 校验参数
        if not user_id_list and not bot_id_list:
            logger.error(" 用户 id 列表和机器人 id 列表不能同时为空")
            return None

        # 合并 id list
        id_list = user_id_list + bot_id_list

        # 构造请求对象
        request: CreateChatMembersRequest = (
            CreateChatMembersRequest.builder()
            .chat_id(chat_id)
            .member_id_type("open_id")
            .succeed_type(
                0
            )  # 将参数中可用的 ID 全部拉入群聊，返回拉群成功的响应，并展示剩余不可用的 ID 及原因。
            .request_body(
                CreateChatMembersRequestBody.builder().id_list(id_list).build()
            )
            .build()
        )

        # 发起请求
        response: CreateChatMembersResponse = self.client.im.v1.chat_members.create(
            request
        )

        # 处理失败返回
        if not response.success():
            resp_data = json.dumps(
                json.loads(response.raw.content), indent=4, ensure_ascii=False
            )
            logger.error(
                f"添加群成员失败, code: {response.code}, msg: {response.msg}, resp: \n{resp_data}"
            )
            return None

        # 处理业务结果
        logger.debug(f"添加群成员成功: {lark.JSON.marshal(response.data, indent=4)}")
        return response.data

    # 更新群信息（群名称）
    def update_chat_info(
        self,
        chat_id: str,
        name: str,
        description: str = "运营告警群",
    ):
        """更新群信息（群名称）

        Ref:
            - https://open.feishu.cn/document/server-docs/group/chat/update-2

        Args:
            chat_id (str): 群聊 id
            name (str, optional): 群名称. Defaults to None.
        """

        # 构造请求对象
        request: UpdateChatRequest = (
            UpdateChatRequest.builder()
            .chat_id(chat_id)
            .user_id_type("open_id")
            .request_body(
                UpdateChatRequestBody.builder()
                # .avatar("default-avatar_44ae0ca3-e140-494b-956f-78091e348435")
                .name(name)
                .description(description)
                # .i18n_names(
                #     I18nNames.builder()
                #     .zh_cn("群聊")
                #     .en_us("group chat")
                #     .ja_jp("グループチャット")
                #     .build()
                # )
                # .add_member_permission("all_members")
                # .share_card_permission("allowed")
                # .at_all_permission("all_members")
                # .edit_permission("all_members")
                # .owner_id("4d7a3c6g")
                # .join_message_visibility("only_owner")
                # .leave_message_visibility("only_owner")
                # .membership_approval("no_approval_required")
                # .restricted_mode_setting(
                #     RestrictedModeSetting.builder()
                #     .status(False)
                #     .screenshot_has_permission_setting("all_members")
                #     .download_has_permission_setting("all_members")
                #     .message_has_permission_setting("all_members")
                #     .build()
                # )
                # .chat_type("private")
                # .group_message_type("chat")
                # .urgent_setting("all_members")
                # .video_conference_setting("all_members")
                # .hide_member_count_setting("all_members")
                .build()
            )
            .build()
        )

        # 发起请求
        response: UpdateChatResponse = self.client.im.v1.chat.update(request)

        # 处理失败返回
        if not response.success():
            resp_data = json.dumps(
                json.loads(response.raw.content), indent=4, ensure_ascii=False
            )
            logger.error(
                f"更新群信息失败, code: {response.code}, msg: {response.msg}, resp: \n{resp_data}"
            )
            return None

        # 处理业务结果
        # logger.debug(f"更新群信息成功: {lark.JSON.marshal(response, indent=4)}")
        return response

    # 发送消息
    def send_message(
        self,
        chat_id: str = "oc_ce179442842e3801af6145ed967590fa",
        content: str = "测试消息",
        at_user_ids: list[str] = None,
        at_all: bool = False,
        msg_type: str = "text",
    ):
        """发送消息

        Refs:
            - https://open.feishu.cn/document/server-docs/im-v1/message/create?appId=cli_a8d49f402c7d900c
                - 向同一用户发送消息的限频为 5 QPS、向同一群组发送消息的限频为群内机器人共享 5 QPS。
                - 接口频率限制: 1000 次/分钟、50 次/秒
        Args:
            chat_id (str): 群聊 id
            content (str): 消息内容

        """

        @auto_handle_http_resp
        def task():
            at_str = ""
            # @所有人
            if at_all:
                at_str = '<at user_id="all"></at>'

            # @指定用户
            if at_user_ids:
                for user_id in at_user_ids:
                    at_str += f' <at user_id="{user_id}"></at> '

            # 创建消息内容字典
            msg = {
                "text": f"{content}\n\n{at_str}".strip(),
            }
            # 将字典转换为 JSON 字符串
            text = json.dumps(msg)
            # logger.debug(f"发送消息: {msg}")

            # 构造请求对象
            request: CreateMessageRequest = (
                CreateMessageRequest.builder()
                .receive_id_type("chat_id")
                .request_body(
                    CreateMessageRequestBody.builder()
                    .receive_id(chat_id)
                    .msg_type(msg_type)
                    .content(text)
                    .build()
                )
                .build()
            )

            # 发起请求
            return self.client.im.v1.message.create(request)

        return task()

    # 发送到单个群组
    def send_one(
        self,
        content: str,
        chat_id: str,
        at_user_ids: list[str] = None,
        at_all: bool = False,
        msg_type: str = "text",
    ):
        if not chat_id:
            lark.logger.warn(f"send_one chat_id is empty, content: {content}")
            return

        self.send_message(
            content=content,
            chat_id=chat_id,
            at_user_ids=at_user_ids,
            at_all=at_all,
            msg_type=msg_type,
        )

    # 发送到多个群组
    def send_many(
        self,
        content: str,
        chat_ids: list[str],
        at_user_ids: list[str] = None,
        at_all: bool = False,
        msg_type: str = "text",
    ):
        if not chat_ids:
            lark.logger.warn(f"send_many chat_ids is empty, content: {content}")
            return

        for chat_id in chat_ids:
            self.send_message(
                content=content,
                chat_id=chat_id,
                at_user_ids=at_user_ids,
                at_all=at_all,
                msg_type=msg_type,
            )

    # 发送应用内加急消息
    def send_urgent_message(self, chat_id: str, content: str):
        """发送应用内加急消息
        Refs:
            - https://open.feishu.cn/document/server-docs/im-v1/buzz-messages/urgent_app?appId=cli_a8d49f402c7d900c

        Args:
            chat_id (str): 群聊 id
            content (str): 消息内容
        """

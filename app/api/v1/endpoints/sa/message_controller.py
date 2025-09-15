from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_db, get_current_active_user
from app.schemas.message import MessageCreate, MessageResponse, MessageUpdate
from app.services.message_service import MessageService
from app.services.conversation_service import ConversationService
from app.services.llm_configuration_service import LlmConfigurationService
# from app.config import settings
from app.core.llm import get_llm_response
from app.db.models.user import UserModel
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

router = APIRouter()

@router.post("/conversation/message", response_model=MessageResponse)
async def create_message(
    *,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
    message_in: MessageCreate,
    background_tasks: BackgroundTasks
):
    """创建新的消息"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to create message for conversation {message_in.conversation_id}. Question: {message_in.question[:50]}...")
    # 验证会话存在且属于当前用户
    conversation = await ConversationService.get(db=db, id=message_in.conversation_id)
    if not conversation:
        logger.warning(f"Conversation {message_in.conversation_id} not found for message creation by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to create message in unauthorized conversation {message_in.conversation_id} (owner: {conversation.user_id}).")
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 验证LLM配置是否存在且可用
    llm_config = await LlmConfigurationService.get(db=db, id=message_in.llm_id)
    if not llm_config or llm_config.status != 1:
        logger.warning(f"Invalid or unavailable LLM configuration {message_in.llm_id} for message creation by user {current_user.id}.")
        raise HTTPException(status_code=400, detail="Invalid LLM configuration")

    message_in.create_by = current_user.user_name
    
    # 获取历史消息作为上下文
    history_messages = await MessageService.get_by_conversation(
        db=db, conversation_id=message_in.conversation_id, limit=llm_config.max_chat_limit
    )
    logger.debug(f"Retrieved {len(history_messages)} history messages for conversation {message_in.conversation_id}.")
    
    # 异步获取LLM响应
    llm_response = await get_llm_response(
        question=message_in.question,
        history_messages=history_messages,
        llm_config=llm_config
    )
    logger.debug(f"LLM response received for conversation {message_in.conversation_id}. Content: {llm_response.get('content', '')[:50]}...")
    
    message_in.content = llm_response.get("content", "")
    message_in.reasoning_content = llm_response.get("reasoning_content")
    
    message = await MessageService.create(db=db, obj_in=message_in)
    logger.info(f"Message {message.id} created for conversation {message_in.conversation_id} by user {current_user.id}.")
    return message

@router.get("/conversation/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """获取特定会话的消息列表"""
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting messages for conversation {conversation_id}. Skip: {skip}, Limit: {limit}.")
    conversation = await ConversationService.get(db=db, id=conversation_id)
    if not conversation:
        logger.warning(f"Conversation {conversation_id} not found for message list request by user {current_user.id}.")
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to access messages in unauthorized conversation {conversation_id} (owner: {conversation.user_id}).")
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    messages = await MessageService.get_by_conversation(
        db=db, conversation_id=conversation_id, skip=skip, limit=limit
    )
    logger.info(f"Returned {len(messages)} messages for conversation {conversation_id} to user {current_user.id}.")
    return messages 
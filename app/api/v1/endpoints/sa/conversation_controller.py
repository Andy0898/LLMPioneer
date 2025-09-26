from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_current_active_user
from app.db.session import get_db
from app.schemas.conversation import (
    ConversationCreate, ConversationUpdate, ConversationResponse, ConversationList,
    SendMessageRequest, SendMessageResponse
)
from app.schemas.message import MessageCreate, MessageResponse
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.services.llm_configuration_service import LlmConfigurationService
from app.core.llm import get_llm_response
from app.db.models.user import UserModel
from pydantic import BaseModel
from app.core.logger.logging_config_helper import get_configured_logger # 导入日志

logger = get_configured_logger("pioneer_handler") # 获取Logger实例

router = APIRouter()

class ConversationCreateRequest(BaseModel):
    title: str = "新对话"
    llm_id: int

@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation_data: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    创建新会话
    """
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to create new conversation with title: {conversation_data.title}, LLM ID: {conversation_data.llm_id}.")
    # 1. 验证LLM配置是否存在且可用
    llm_config = await LlmConfigurationService.get(db=db, id=conversation_data.llm_id)
    if not llm_config or llm_config.status != 1:
        logger.warning(f"Invalid or unavailable LLM configuration {conversation_data.llm_id} for user {current_user.id}.")
        raise HTTPException(status_code=400, detail="Invalid LLM configuration")

    # 2. 获取大模型响应
    initial_prompt = f"你好，这是一个新的对话，主题是：{conversation_data.title}"
    llm_response = await get_llm_response(
        question=initial_prompt,
        history_messages=[],  # 新对话没有历史消息
        llm_config=llm_config
    )
    logger.debug(f"Initial LLM response for new conversation: {llm_response.get('content', '')[:50]}...")

    # 3. 创建会话记录
    conversation = await ConversationService.create(
        db=db,
        obj_in=ConversationCreate(
            title=conversation_data.title,
            user_id=current_user.id,
            create_by=current_user.user_name
        )
    )
    logger.info(f"Conversation {conversation.id} created for user {current_user.id}.")

    # 4. 创建消息记录
    await MessageService.create(
        db=db,
        obj_in=MessageCreate(
            conversation_id=conversation.id,
            llm_id=conversation_data.llm_id,
            question=initial_prompt,
            content=llm_response["content"],
            reasoning_content=llm_response.get("reasoning_content"),
            create_by=current_user.user_name
        )
    )
    logger.info(f"Initial message created for conversation {conversation.id}.")

    # 5. 返回创建的会话信息和大模型响应
    logger.info(f"New conversation {conversation.id} with initial response returned to user {current_user.id}.")
    return {
        **conversation.__dict__,
        "initial_response": llm_response
    }

@router.get("/list", response_model=ConversationList)
async def get_conversations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    获取用户的会话列表
    """
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting conversation list. Skip: {skip}, Limit: {limit}.")
    total = await ConversationService.get_total(db=db, user_id=current_user.id)
    conversations = await ConversationService.get_multi(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    logger.info(f"Returned {len(conversations)} conversations (total: {total}) to user {current_user.id}.")
    return {
        "total": total,
        "items": conversations
    }

@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    获取会话详情
    """
    logger.info(f"User {current_user.id} ({current_user.user_name}) requesting detail for conversation {conversation_id}.")
    conversation = await ConversationService.get(db=db, id=conversation_id)
    
    if not conversation:
        logger.warning(f"Conversation {conversation_id} not found for user {current_user.id}.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
        
    if conversation.user_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to access unauthorized conversation {conversation_id} (owner: {conversation.user_id}).")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    logger.info(f"Returned detail for conversation {conversation_id} to user {current_user.id}.")
    
    # 获取对话的消息列表
    messages = await MessageService.get_by_conversation(db=db, conversation_id=conversation_id, limit=50)
    message_responses = [MessageResponse.model_validate(msg) for msg in messages]
    
    # 返回包含消息列表的对话信息
    return ConversationResponse(
        **conversation.__dict__,
        messages=message_responses
    )

@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_data: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    更新会话信息
    """
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to update conversation {conversation_id} with data: {conversation_data.dict()}")
    conversation = await ConversationService.get(db=db, id=conversation_id)
    
    if not conversation:
        logger.warning(f"Conversation {conversation_id} not found for update by user {current_user.id}.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
        
    if conversation.user_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to update unauthorized conversation {conversation_id} (owner: {conversation.user_id}).")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    conversation_data.update_by = current_user.user_name
    updated_conversation = await ConversationService.update(
        db=db,
        db_obj=conversation,
        obj_in=conversation_data
    )
    logger.info(f"Conversation {conversation_id} updated by user {current_user.id}.")
    return updated_conversation

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    删除会话
    """
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to delete conversation {conversation_id}.")
    conversation = await ConversationService.get(db=db, id=conversation_id)
    
    if not conversation:
        logger.warning(f"Conversation {conversation_id} not found for deletion by user {current_user.id}.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
        
    if conversation.user_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to delete unauthorized conversation {conversation_id} (owner: {conversation.user_id}).")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # TODO: 实现删除功能
    # await ConversationService.delete(db=db, id=conversation_id)
    delete_success = await ConversationService.delete(db=db, id=conversation_id)
    if delete_success:
        logger.info(f"Conversation {conversation_id} and its messages successfully deleted by user {current_user.id}.")
        return {"message": "Conversation deleted successfully"}
    else:
        logger.error(f"Failed to delete conversation {conversation_id} for user {current_user.id}.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )

@router.post("/{conversation_id}/send-message", response_model=SendMessageResponse)
async def send_message_to_conversation(
    conversation_id: int,
    message_data: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    在已有对话中发送消息
    """
    logger.info(f"User {current_user.id} ({current_user.user_name}) sending message to conversation {conversation_id}. Question: {message_data.question[:50]}...")
    
    # 1. 验证对话存在且属于当前用户
    conversation = await ConversationService.get(db=db, id=conversation_id)
    if not conversation:
        logger.warning(f"Conversation {conversation_id} not found for message send by user {current_user.id}.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
        
    if conversation.user_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to send message to unauthorized conversation {conversation_id} (owner: {conversation.user_id}).")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # 2. 验证LLM配置是否存在且可用
    llm_config = await LlmConfigurationService.get(db=db, id=message_data.llm_id)
    if not llm_config or llm_config.status != 1:
        logger.warning(f"Invalid or unavailable LLM configuration {message_data.llm_id} for message send by user {current_user.id}.")
        raise HTTPException(status_code=400, detail="Invalid LLM configuration")
    
    # 3. 获取历史消息作为上下文
    history_messages = await MessageService.get_by_conversation(
        db=db, 
        conversation_id=conversation_id, 
        limit=getattr(llm_config, 'max_chat_limit', 10)
    )
    logger.debug(f"Retrieved {len(history_messages)} history messages for conversation {conversation_id}.")
    
    # 4. 获取大模型响应
    llm_response = await get_llm_response(
        question=message_data.question,
        history_messages=history_messages,
        llm_config=llm_config
    )
    logger.debug(f"LLM response received for conversation {conversation_id}. Content: {llm_response.get('content', '')[:50]}...")
    
    # 5. 创建消息记录
    message = await MessageService.create(
        db=db,
        obj_in=MessageCreate(
            conversation_id=conversation_id,
            llm_id=message_data.llm_id,
            question=message_data.question,
            content=llm_response.get("content", ""),
            reasoning_content=llm_response.get("reasoning_content"),
            create_by=current_user.user_name
        )
    )
    logger.info(f"Message {message.id} created for conversation {conversation_id} by user {current_user.id}.")
    
    # 6. 获取更新后的对话信息（包含消息列表）
    updated_messages = await MessageService.get_by_conversation(db=db, conversation_id=conversation_id, limit=20)
    message_responses = [MessageResponse.model_validate(msg) for msg in updated_messages]
    conversation_response = ConversationResponse(
        **conversation.__dict__,
        messages=message_responses
    )
    
    logger.info(f"Message sent successfully to conversation {conversation_id} by user {current_user.id}.")
    return SendMessageResponse(
        message=MessageResponse.model_validate(message),
        conversation=conversation_response
    )

@router.put("/message/{message_id}", response_model=MessageResponse)
async def update_message(
    message_id: int,
    updated_question: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    更新消息并重新生成响应（基于上下文）
    """
    logger.info(f"User {current_user.id} ({current_user.user_name}) updating message {message_id} with new question: {updated_question[:50]}...")
    
    # 1. 获取消息并验证权限
    message = await MessageService.get(db=db, id=message_id)
    if not message:
        logger.warning(f"Message {message_id} not found for update by user {current_user.id}.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # 2. 验证对话所有权
    conversation = await ConversationService.get(db=db, id=message.conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to update message {message_id} in unauthorized conversation {message.conversation_id}.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # 3. 获取LLM配置
    llm_config = await LlmConfigurationService.get(db=db, id=message.llm_id)
    if not llm_config or llm_config.status != 1:
        logger.warning(f"Invalid or unavailable LLM configuration {message.llm_id} for message update by user {current_user.id}.")
        raise HTTPException(status_code=400, detail="Invalid LLM configuration")
    
    # 4. 获取该消息之前的历史消息作为上下文
    history_messages = await MessageService.get_messages_before_time(
        db=db, 
        conversation_id=message.conversation_id, 
        before_time=message.create_time
    )
    logger.debug(f"Retrieved {len(history_messages)} history messages before message {message_id} for context.")
    
    # 5. 获取新的LLM响应
    llm_response = await get_llm_response(
        question=updated_question,
        history_messages=history_messages,
        llm_config=llm_config
    )
    logger.debug(f"LLM response received for updated message {message_id}. Content: {llm_response.get('content', '')[:50]}...")
    
    # 6. 更新消息
    from app.schemas.message import MessageUpdate
    updated_message = await MessageService.update(
        db=db,
        db_obj=message,
        obj_in=MessageUpdate(
            content=llm_response.get("content", ""),
            reasoning_content=llm_response.get("reasoning_content"),
            update_by=current_user.user_name
        )
    )
    
    # 同时更新问题（需要添加到MessageUpdate schema中）
    updated_message.question = updated_question
    await db.commit()
    await db.refresh(updated_message)
    
    logger.info(f"Message {message_id} updated successfully by user {current_user.id}.")
    return MessageResponse.model_validate(updated_message)

@router.delete("/message/{message_id}")
async def delete_message(
    message_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user)
):
    """
    删除消息
    """
    logger.info(f"User {current_user.id} ({current_user.user_name}) attempting to delete message {message_id}.")
    
    # 1. 获取消息并验证权限
    message = await MessageService.get(db=db, id=message_id)
    if not message:
        logger.warning(f"Message {message_id} not found for deletion by user {current_user.id}.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # 2. 验证对话所有权
    conversation = await ConversationService.get(db=db, id=message.conversation_id)
    if not conversation or conversation.user_id != current_user.id:
        logger.warning(f"User {current_user.id} attempted to delete message {message_id} in unauthorized conversation {message.conversation_id}.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # 3. 删除消息
    delete_success = await MessageService.delete(db=db, id=message_id)
    if delete_success:
        logger.info(f"Message {message_id} successfully deleted by user {current_user.id}.")
        return {"message": "Message deleted successfully"}
    else:
        logger.error(f"Failed to delete message {message_id} for user {current_user.id}.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete message"
        ) 
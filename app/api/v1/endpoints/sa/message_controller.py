from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.v1.deps import get_db, get_current_active_user
from app.schemas.message import MessageCreate, MessageResponse, MessageUpdate
from app.services.message_service import MessageService
from app.services.conversation_service import ConversationService
from app.services.llm_configuration_service import LlmConfigurationService
from app.config import settings
from app.core.llm import get_llm_response
from app.db.models.user import UserModel


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
    # 验证会话存在且属于当前用户
    conversation = await ConversationService.get(db=db, id=message_in.conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    # 验证LLM配置是否存在且可用
    llm_config = await LlmConfigurationService.get(db=db, id=message_in.llm_id)
    if not llm_config or llm_config.status != 1:
        raise HTTPException(status_code=400, detail="Invalid LLM configuration")

    message_in.create_by = current_user.user_name
    
    # 获取历史消息作为上下文
    history_messages = await MessageService.get_by_conversation(
        db=db, conversation_id=message_in.conversation_id, limit=llm_config.max_chat_limit
    )
    
    # 异步获取LLM响应
    llm_response = await get_llm_response(
        question=message_in.question,
        history_messages=history_messages,
        llm_config=llm_config
    )
    
    message_in.content = llm_response.get("content", "")
    message_in.reasoning_content = llm_response.get("reasoning_content")
    
    message = await MessageService.create(db=db, obj_in=message_in)
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
    conversation = await ConversationService.get(db=db, id=conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    messages = await MessageService.get_by_conversation(
        db=db, conversation_id=conversation_id, skip=skip, limit=limit
    )
    return messages 
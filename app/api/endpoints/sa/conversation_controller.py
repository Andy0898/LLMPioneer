from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.schemas.conversation import ConversationCreate, ConversationUpdate, ConversationResponse, ConversationList
from app.schemas.message import MessageCreate
from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService
from app.services.llm_configuration_service import LlmConfigurationService
from app.core.llm import get_llm_response
from app.db.models.user import UserModel
from pydantic import BaseModel

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
    # 1. 验证LLM配置是否存在且可用
    llm_config = await LlmConfigurationService.get(db=db, id=conversation_data.llm_id)
    if not llm_config or llm_config.status != 1:
        raise HTTPException(status_code=400, detail="Invalid LLM configuration")

    # 2. 获取大模型响应
    initial_prompt = f"你好，这是一个新的对话，主题是：{conversation_data.title}"
    llm_response = await get_llm_response(
        question=initial_prompt,
        history_messages=[],  # 新对话没有历史消息
        llm_config=llm_config
    )

    # 3. 创建会话记录
    conversation = await ConversationService.create(
        db=db,
        obj_in=ConversationCreate(
            title=conversation_data.title,
            user_id=current_user.id,
            create_by=current_user.user_name
        )
    )

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

    # 5. 返回创建的会话信息和大模型响应
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
    total = await ConversationService.get_total(db=db, user_id=current_user.id)
    conversations = await ConversationService.get_multi(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
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
    conversation = await ConversationService.get(db=db, id=conversation_id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
        
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
        
    return conversation

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
    conversation = await ConversationService.get(db=db, id=conversation_id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
        
    if conversation.user_id != current_user.id:
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
    conversation = await ConversationService.get(db=db, id=conversation_id)
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
        
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # TODO: 实现删除功能
    # await ConversationService.delete(db=db, id=conversation_id)
        
    return {"message": "Conversation deleted successfully"} 
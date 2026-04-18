from datetime import datetime
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from clients.minimax_client import (
    MiniMaxClient,
    MiniMaxResponseData,
    MiniMaxError,
)
from core.logger import get_logger
from core.settings import settings
from db.crud.generation_record import generation_record_crud
from db.crud.script_work import script_work_crud
from db.crud.script_chapter import script_chapter_crud
from db.models.generation_record import (
    GenerationRecordCreate,
    GenerationType,
    GenerationStatus,
)

logger = get_logger(__name__)


class ScriptGenerationService:
    OUTLINE_PROMPT_TEMPLATE = """你是一位专业的剧本大纲设计师。请根据以下要求，创作一个完整的剧本大纲。

作品标题：{title}
作品描述：{description}

请生成一个结构清晰、逻辑严谨的剧本大纲，包含以下内容：
1. 故事核心主题与立意
2. 主要故事线概述
3. 关键情节点分布
4. 故事结构（三幕结构或其他适合的结构）

请用清晰的markdown格式输出，确保内容专业、完整、具有可执行性。"""

    CHARACTERS_PROMPT_TEMPLATE = """你是一位专业的角色设计师。请根据以下作品信息和大纲，设计主要角色设定。

作品标题：{title}
作品描述：{description}

已确定的故事大纲：
{outline}

请为这个故事设计主要角色设定，每个角色需要包含：
1. 角色姓名
2. 年龄与外貌特征
3. 性格特点
4. 背景故事
5. 在故事中的定位和作用
6. 与其他角色的关系

请确保角色设计符合故事大纲的设定，角色之间有明确的互动关系和戏剧张力。用markdown格式输出。"""

    CHAPTER_PROMPT_TEMPLATE = """你是一位专业的剧本作家。请根据以下信息，创作第{chapter_number}集/场的详细内容。

作品标题：{title}
已确定的故事大纲：
{outline}

已确定的角色设定：
{characters}

第{chapter_number}集/场信息：
章节标题：{chapter_title}
章节大纲：{chapter_outline}

请根据以上信息，创作完整的剧本内容。要求：
1. 符合剧本格式（场景说明、人物对话、动作描述等）
2. 角色对话要符合其性格设定
3. 情节推进要自然流畅
4. 注意场景转换和节奏把控

请用专业的剧本格式输出。"""

    def __init__(
        self,
        minimax_client: Optional[MiniMaxClient] = None,
        db_session: Optional[AsyncSession] = None,
    ):
        self._minimax_client = minimax_client
        self._db_session = db_session
        self._owns_client = minimax_client is None

    def _get_client(self) -> MiniMaxClient:
        if self._minimax_client is None:
            self._minimax_client = MiniMaxClient()
            self._owns_client = True
        return self._minimax_client

    async def _create_generation_record(
        self,
        generation_type: GenerationType,
        script_work_id: int,
        project_id: int,
        user_id: int,
        prompt: str,
        script_chapter_id: Optional[int] = None,
    ) -> int:
        if self._db_session is None:
            logger.warning("数据库会话未提供，无法创建生成记录")
            return 0

        try:
            record_create = GenerationRecordCreate(
                generation_type=generation_type,
                script_work_id=script_work_id,
                script_chapter_id=script_chapter_id,
                prompt=prompt,
                metadata={
                    "generated_at": datetime.now().isoformat(),
                },
            )
            record = await generation_record_crud.create(
                self._db_session,
                record_create,
                user_id=user_id,
            )
            logger.info(f"创建生成记录成功: ID={record.id}, 类型={generation_type.value}")
            return record.id
        except Exception as e:
            logger.error(f"创建生成记录失败: {str(e)}", exc_info=True)
            return 0

    async def _update_generation_record(
        self,
        record_id: int,
        user_id: int,
        status: GenerationStatus,
        result: Optional[str] = None,
        error_message: Optional[str] = None,
        model_used: Optional[str] = None,
        tokens_used: Optional[int] = None,
    ) -> None:
        if self._db_session is None or record_id == 0:
            return

        try:
            await generation_record_crud.update_status(
                self._db_session,
                record_id=record_id,
                status=status.value,
                user_id=user_id,
                result=result,
                error_message=error_message,
                tokens_used=tokens_used,
            )
        except Exception as e:
            logger.error(f"更新生成记录失败: {str(e)}", exc_info=True)

    async def _call_minimax_api(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> tuple[Optional[MiniMaxResponseData], Optional[MiniMaxError], float]:
        client = self._get_client()
        return await client.chat(
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )

    async def generate_outline(
        self,
        script_work_id: int,
        user_id: int,
        custom_prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        if self._db_session is None:
            return {
                "success": False,
                "error_msg": "数据库会话未提供",
            }

        script_work = await script_work_crud.get_by_id(
            self._db_session,
            id=script_work_id,
            user_id=user_id,
        )
        if not script_work:
            return {
                "success": False,
                "error_msg": "脚本作品不存在或无权限访问",
            }

        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self.OUTLINE_PROMPT_TEMPLATE.format(
                title=script_work.title,
                description=script_work.description or "未提供描述",
            )

        record_id = await self._create_generation_record(
            generation_type=GenerationType.OUTLINE,
            script_work_id=script_work_id,
            project_id=script_work.project_id,
            user_id=user_id,
            prompt=prompt,
        )

        logger.info(f"开始生成大纲，作品ID: {script_work_id}")
        response_data, error, latency_ms = await self._call_minimax_api(prompt)

        if response_data and error is None:
            result = response_data.content
            model_used = response_data.model
            tokens_used = response_data.usage.total_tokens if response_data.usage else None

            await self._update_generation_record(
                record_id=record_id,
                user_id=user_id,
                status=GenerationStatus.COMPLETED,
                result=result,
                model_used=model_used,
                tokens_used=tokens_used,
            )

            logger.info(f"大纲生成成功，作品ID: {script_work_id}, 耗时: {latency_ms:.2f}ms")
            return {
                "success": True,
                "content": result,
                "model": model_used,
                "latency_ms": round(latency_ms, 2),
                "tokens_used": tokens_used,
            }
        else:
            error_msg = error.message if error else "未知错误"
            await self._update_generation_record(
                record_id=record_id,
                user_id=user_id,
                status=GenerationStatus.FAILED,
                error_message=error_msg,
            )
            logger.error(f"大纲生成失败，作品ID: {script_work_id}: {error_msg}")
            return {
                "success": False,
                "error_msg": error_msg,
                "latency_ms": round(latency_ms, 2),
            }

    async def generate_characters(
        self,
        script_work_id: int,
        user_id: int,
        custom_prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        if self._db_session is None:
            return {
                "success": False,
                "error_msg": "数据库会话未提供",
            }

        script_work = await script_work_crud.get_by_id(
            self._db_session,
            id=script_work_id,
            user_id=user_id,
        )
        if not script_work:
            return {
                "success": False,
                "error_msg": "脚本作品不存在或无权限访问",
            }

        current_outline = script_work.outline or "尚未确定大纲"

        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self.CHARACTERS_PROMPT_TEMPLATE.format(
                title=script_work.title,
                description=script_work.description or "未提供描述",
                outline=current_outline,
            )

        record_id = await self._create_generation_record(
            generation_type=GenerationType.CHARACTERS,
            script_work_id=script_work_id,
            project_id=script_work.project_id,
            user_id=user_id,
            prompt=prompt,
        )

        logger.info(f"开始生成人物设定，作品ID: {script_work_id}")
        response_data, error, latency_ms = await self._call_minimax_api(prompt)

        if response_data and error is None:
            result = response_data.content
            model_used = response_data.model
            tokens_used = response_data.usage.total_tokens if response_data.usage else None

            await self._update_generation_record(
                record_id=record_id,
                user_id=user_id,
                status=GenerationStatus.COMPLETED,
                result=result,
                model_used=model_used,
                tokens_used=tokens_used,
            )

            logger.info(f"人物设定生成成功，作品ID: {script_work_id}, 耗时: {latency_ms:.2f}ms")
            return {
                "success": True,
                "content": result,
                "model": model_used,
                "latency_ms": round(latency_ms, 2),
                "tokens_used": tokens_used,
            }
        else:
            error_msg = error.message if error else "未知错误"
            await self._update_generation_record(
                record_id=record_id,
                user_id=user_id,
                status=GenerationStatus.FAILED,
                error_message=error_msg,
            )
            logger.error(f"人物设定生成失败，作品ID: {script_work_id}: {error_msg}")
            return {
                "success": False,
                "error_msg": error_msg,
                "latency_ms": round(latency_ms, 2),
            }

    async def generate_chapter_content(
        self,
        script_work_id: int,
        chapter_id: int,
        user_id: int,
        custom_prompt: Optional[str] = None,
    ) -> dict[str, Any]:
        if self._db_session is None:
            return {
                "success": False,
                "error_msg": "数据库会话未提供",
            }

        script_work = await script_work_crud.get_by_id(
            self._db_session,
            id=script_work_id,
            user_id=user_id,
        )
        if not script_work:
            return {
                "success": False,
                "error_msg": "脚本作品不存在或无权限访问",
            }

        chapter = await script_chapter_crud.get_by_id(
            self._db_session,
            id=chapter_id,
            user_id=user_id,
        )
        if not chapter:
            return {
                "success": False,
                "error_msg": "章节不存在或无权限访问",
            }

        if chapter.script_work_id != script_work_id:
            return {
                "success": False,
                "error_msg": "章节不属于该作品",
            }

        current_outline = script_work.outline or "尚未确定大纲"
        current_characters = script_work.characters or "尚未确定角色设定"

        if custom_prompt:
            prompt = custom_prompt
        else:
            prompt = self.CHAPTER_PROMPT_TEMPLATE.format(
                title=script_work.title,
                outline=current_outline,
                characters=current_characters,
                chapter_number=chapter.chapter_number,
                chapter_title=chapter.title,
                chapter_outline=chapter.outline or "未提供章节大纲",
            )

        record_id = await self._create_generation_record(
            generation_type=GenerationType.CHAPTER,
            script_work_id=script_work_id,
            project_id=script_work.project_id,
            user_id=user_id,
            prompt=prompt,
            script_chapter_id=chapter_id,
        )

        logger.info(f"开始生成章节内容，作品ID: {script_work_id}, 章节ID: {chapter_id}")
        response_data, error, latency_ms = await self._call_minimax_api(prompt, max_tokens=8192)

        if response_data and error is None:
            result = response_data.content
            model_used = response_data.model
            tokens_used = response_data.usage.total_tokens if response_data.usage else None

            await self._update_generation_record(
                record_id=record_id,
                user_id=user_id,
                status=GenerationStatus.COMPLETED,
                result=result,
                model_used=model_used,
                tokens_used=tokens_used,
            )

            logger.info(f"章节内容生成成功，作品ID: {script_work_id}, 章节ID: {chapter_id}, 耗时: {latency_ms:.2f}ms")
            return {
                "success": True,
                "content": result,
                "model": model_used,
                "latency_ms": round(latency_ms, 2),
                "tokens_used": tokens_used,
            }
        else:
            error_msg = error.message if error else "未知错误"
            await self._update_generation_record(
                record_id=record_id,
                user_id=user_id,
                status=GenerationStatus.FAILED,
                error_message=error_msg,
            )
            logger.error(f"章节内容生成失败，作品ID: {script_work_id}, 章节ID: {chapter_id}: {error_msg}")
            return {
                "success": False,
                "error_msg": error_msg,
                "latency_ms": round(latency_ms, 2),
            }

    async def close(self) -> None:
        if self._owns_client and self._minimax_client is not None:
            await self._minimax_client.close()
            self._minimax_client = None

    async def __aenter__(self) -> "ScriptGenerationService":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

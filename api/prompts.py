from fastapi import APIRouter, HTTPException, Query

from core.logger import get_logger
from core.prompts import get_prompt_template, list_available_templates
from db.models.generation_record import GenerationType

logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["prompts"])

VALID_TYPES = {
    "outline": GenerationType.OUTLINE,
    "characters": GenerationType.CHARACTERS,
    "chapter_outline": GenerationType.CHAPTER_OUTLINE,
    "chapter_content": GenerationType.CHAPTER_CONTENT,
}


@router.get(
    "/prompts",
    summary="获取提示词模板",
    responses={
        200: {"description": "获取成功"},
        400: {"description": "无效的生成类型"},
    },
)
async def get_prompts(
    type: str = Query(..., description="生成类型：outline, characters, chapter_outline, chapter_content"),
) -> dict:
    logger.info(f"获取提示词模板请求，类型: {type}")

    if type not in VALID_TYPES:
        logger.warning(f"无效的生成类型: {type}")
        raise HTTPException(
            status_code=400,
            detail="无效的生成类型",
        )

    gen_type = VALID_TYPES[type]
    template = get_prompt_template(gen_type)

    available_templates = list_available_templates()
    description = "未知类型"
    for gt, desc in available_templates:
        if gt == gen_type:
            description = desc
            break

    return {
        "success": True,
        "type": type,
        "template": template,
        "description": description,
    }

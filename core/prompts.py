import re
from typing import Any

from db.models.generation_record import GenerationType


DEFAULT_PROMPT_TEMPLATES: dict[GenerationType, str] = {
    GenerationType.OUTLINE: """你是一位专业的短剧/网文创作编剧。请根据用户的需求，创作一个完整的故事大纲。

创作要求：
1. 故事类型：{genre:悬疑/甜宠/爽文/玄幻等，根据需求确定}
2. 目标时长/篇幅：{target_length:短剧通常10-100集，网文通常50-500章}
3. 核心卖点：{selling_point:例如"女主逆袭"、"穿越打脸"、"甜宠虐恋"等}

请按照以下结构输出大纲：
【故事简介】（100-200字概括整个故事）
【核心主题】（1-2句话点明故事主旨）
【主要冲突】（列出3-5个关键冲突点）
【故事结构】
- 开篇钩子（第1-3章/集）：如何吸引读者/观众
- 发展阶段（第4-50章/集）：主要情节推进
- 高潮阶段（第51-80章/集）：最紧张刺激的部分
- 结局阶段（第81-100章/集）：如何收尾
【关键转折点】（列出5-8个重要转折点）

请确保：
- 节奏紧凑，每章/集都有看点
- 人物动机清晰合理
- 冲突层层递进
- 符合目标受众的口味""",

    GenerationType.CHARACTERS: """你是一位专业的角色设定师。请基于以下故事大纲，设计主要角色的详细设定。

【故事大纲】
{outline}

请为每个主要角色提供以下信息：

【角色名称】
- 基本信息：年龄、性别、外貌特征、职业/身份
- 性格特点：3-5个核心性格词，并用具体事例说明
- 背景故事：成长经历、关键事件塑造的性格
- 核心欲望：角色最想要什么？
- 内心恐惧：角色最害怕什么？
- 人物弧线：故事开始时 vs 故事结束时的变化
- 标志性台词：1-2句能代表角色性格的台词
- 与其他角色的关系：简要说明与其他主要角色的互动

请设计至少3个主要角色：
1. 主角（男主角或女主角）
2. 重要配角（可能是恋人、朋友或对手）
3. 反派或关键对立角色

确保角色设定：
- 与大纲中的情节发展相契合
- 每个角色都有独特的声音和行为模式
- 角色之间的冲突和化学反应足够强烈
- 符合目标受众的审美期待""",

    GenerationType.CHAPTER_OUTLINE: """你是一位专业的分集编剧。请基于以下信息，为指定章节/集创作详细的分集大纲。

【整体故事大纲】
{outline}

【主要角色设定】
{characters}

【当前章节/集信息】
章节/集标题：{chapter_title}
章节/集序号：{chapter_number}
总章节/集数：{total_chapters}

请按照以下结构创作本章/集的详细大纲：

【本章/集核心目标】
- 本章/集要达成什么叙事目的？
- 对整体故事有什么推进作用？

【场景拆分】
场景1：[场景名称]
- 出场人物：
- 地点：
- 时间：
- 核心事件：
- 情感基调：
- 关键对话/动作：

场景2：[场景名称]
...（根据需要添加更多场景）

【本章/集亮点】
- 钩子：开篇如何吸引读者/观众继续看下去
- 高潮：本章/集最精彩的部分
- 悬念：结尾留下什么钩子让读者/观众期待下一章/集

【人物发展】
- 本章/集中哪些角色有重要表现？
- 揭示了角色的什么新特点？
- 角色关系有什么变化？

【与前后章节的衔接】
- 承接上一章/集的什么情节？
- 为下一章/集铺垫什么？

请确保：
- 节奏紧凑，每个场景都有明确的叙事目的
- 符合角色设定，人物行为和对话符合其性格
- 冲突足够强烈，有足够的戏剧张力
- 情感变化自然流畅""",

    GenerationType.CHAPTER_CONTENT: """你是一位专业的网文/短剧作家。请基于以下信息，创作完整的章节/集内容。

【整体故事大纲】
{outline}

【主要角色设定】
{characters}

【当前章节/集信息】
章节/集标题：{chapter_title}
章节/集序号：{chapter_number}
总章节/集数：{total_chapters}

【本章/集详细大纲】
{chapter_outline}

【写作风格要求】
- 类型：{genre:例如"甜宠"、"悬疑"、"爽文"、"玄幻"}
- 语气：{tone:例如"轻松幽默"、"紧张刺激"、"深情虐恋"}
- 目标受众：{audience:例如"女性向"、"男性向"、"全年龄"}
- 每章/集字数要求：{word_count:短剧通常300-800字/集，网文通常2000-5000字/章}

【写作指导】
1. 开篇钩子：前100字必须抓住读者/观众注意力
   - 可以用冲突、悬念、反转或强烈情感开场
   - 避免冗长的背景介绍

2. 对话描写：
   - 每个角色的对话要符合其性格和身份
   - 用动作、表情、环境描写衬托对话
   - 避免长篇大论的独白
   - 对话要有潜台词，不要把所有事情都明说

3. 场景描写：
   - 用感官细节（视觉、听觉、触觉）营造氛围
   - 场景切换要自然流畅
   - 环境描写要服务于情节和人物情绪

4. 节奏控制：
   - 张弛有度，紧张场景与舒缓场景交替
   - 短剧每集要有3-5个情绪转折点
   - 网文每章要有明确的起承转合

5. 情感渲染：
   - 通过人物的动作、表情、内心活动展现情感
   - 让读者/观众能够共情角色的喜怒哀乐
   - 关键情感场景要给足篇幅

6. 结尾钩子：
   - 每章/集结尾必须留下悬念或期待
   - 可以是冲突升级、新信息揭露、或重要抉择
   - 让读者/观众迫不及待想看下一章/集

【输出格式】
请直接输出正文内容，不需要标注场景序号。对话使用引号，内心活动可以使用括号或斜体。

注意：
- 严格按照大纲中的情节发展
- 保持角色性格的一致性
- 语言要生动形象，有画面感
- 符合目标受众的阅读/观看习惯
- 确保字数符合要求""",
}


def get_prompt_template(generation_type: GenerationType) -> str:
    """
    根据生成类型获取对应的提示词模板。
    
    未来扩展说明：
    - 当前从 DEFAULT_PROMPT_TEMPLATES 字典中获取默认模板
    - 未来可以从数据库加载自定义模板，优先级：用户自定义 > 项目默认 > 系统默认
    - 数据库表设计建议：
      - prompt_templates: id, generation_type, template_content, is_default, created_by, project_id
      - 支持按项目、按用户覆盖默认模板
    
    Args:
        generation_type: 生成类型枚举值
        
    Returns:
        对应的提示词模板字符串
        
    Raises:
        ValueError: 当 generation_type 没有对应的模板时
    """
    template = DEFAULT_PROMPT_TEMPLATES.get(generation_type)
    if template is None:
        raise ValueError(f"未找到生成类型 {generation_type} 对应的提示词模板")
    return template


def render_prompt(
    generation_type: GenerationType,
    context: dict[str, Any],
) -> str:
    """
    根据上下文渲染提示词模板，替换占位符。
    
    占位符格式说明：
    - 基础格式：{placeholder_name}，例如 {outline}、{characters}、{chapter_title} 等
    - 带默认值的格式：{placeholder_name:默认值说明}，例如 {genre:悬疑/甜宠/爽文/玄幻}
      - 如果 context 中提供了对应值，使用提供的值
      - 如果未提供，使用冒号后的默认值说明
      - 如果连默认值也没有，使用 [placeholder_name] 作为标记
    
    Args:
        generation_type: 生成类型枚举值
        context: 包含占位符对应值的字典
        
    Returns:
        渲染后的完整提示词
        
    Raises:
        ValueError: 当生成类型无效时
    """
    template = get_prompt_template(generation_type)
    
    def replace_placeholder(match: re.Match[str]) -> str:
        full_match = match.group(0)
        placeholder_name = match.group(1)
        default_value = match.group(2)
        
        if placeholder_name in context:
            value = context[placeholder_name]
            return str(value) if value is not None else ""
        
        if default_value:
            return default_value
        
        return f"[{placeholder_name}]"
    
    placeholder_pattern = r'\{([^}:]+)(?::([^}]+))?\}'
    result = re.sub(placeholder_pattern, replace_placeholder, template)
    
    return result


def list_available_templates() -> list[tuple[GenerationType, str]]:
    """
    列出所有可用的提示词模板类型及其简要说明。
    
    用于前端展示或调试目的。
    
    Returns:
        包含 (生成类型, 简要说明) 的列表
    """
    template_descriptions = {
        GenerationType.OUTLINE: "故事大纲生成 - 创建整体故事框架、结构和关键转折点",
        GenerationType.CHARACTERS: "人物设定生成 - 基于大纲设计主要角色的详细设定",
        GenerationType.CHAPTER_OUTLINE: "章节大纲生成 - 为指定章节创作详细的分集大纲",
        GenerationType.CHAPTER_CONTENT: "章节内容生成 - 基于章节大纲生成完整的正文内容",
    }
    
    return [
        (gen_type, template_descriptions.get(gen_type, "未知类型"))
        for gen_type in DEFAULT_PROMPT_TEMPLATES.keys()
    ]

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MiniMax API 长文本生成测试 - 使用 120s 超时
"""
import asyncio
import time
import httpx
from dotenv import load_dotenv
import os
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()


def mask_api_key(key):
    if not key:
        return "None"
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


async def test_long_generation_120s():
    """测试长文本生成 - 使用 120s 超时"""
    api_key = os.getenv("MINIMAX_API_KEY")
    base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1/text/chatcompletion_v2")
    default_model = os.getenv("MINIMAX_DEFAULT_MODEL", "MiniMax-M2.7")
    group_id = os.getenv("MINIMAX_GROUP_ID")

    timeout = 120.0

    print("=" * 70)
    print("MiniMax API 长文本生成测试 (120s 超时)")
    print("=" * 70)
    print(f"API Key: {mask_api_key(api_key)}")
    print(f"Base URL: {base_url}")
    print(f"Model: {default_model}")
    print(f"Timeout: {timeout}s")
    print(f"Group ID: {group_id or '未配置'}")
    print("=" * 70)

    if not api_key:
        print("[ERROR] MINIMAX_API_KEY 未配置")
        return False

    prompt = """你是一位专业的剧本大纲设计师。请根据以下要求，创作一个完整的剧本大纲。

作品标题：草根的故事
作品描述：一个程序员叫林老六，他是一个草根程序员，他生活中每天发生的故事

请生成一个结构清晰、逻辑严谨的剧本大纲，包含以下内容：
1. 故事核心主题与立意
2. 主要故事线概述
3. 关键情节点分布
4. 故事结构（三幕结构或其他适合的结构）

请用清晰的markdown格式输出，确保内容专业、完整、具有可执行性。"""

    payload = {
        "model": default_model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 4096
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    params = {}
    if group_id:
        params["GroupId"] = group_id

    print(f"\n[INFO] Prompt 长度: {len(prompt)} 字符")
    print(f"[INFO] Max Tokens: {payload['max_tokens']}")
    print(f"[INFO] 超时时间: {timeout}s")
    print("-" * 70)

    try:
        start_time = time.time()
        timeout_config = httpx.Timeout(timeout=timeout, connect=10.0)

        async with httpx.AsyncClient(timeout=timeout_config) as client:
            print(f"[{time.time() - start_time:.2f}s] 发送请求...")

            response = await client.post(
                base_url,
                json=payload,
                headers=headers,
                params=params,
            )

            elapsed = time.time() - start_time
            print(f"[{elapsed:.2f}s] 收到响应")
            print(f"[INFO] HTTP 状态码: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"\n[SUCCESS] 请求成功!")
                    print(f"[INFO] 响应 ID: {data.get('id')}")
                    print(f"[INFO] 响应模型: {data.get('model')}")

                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        print(f"\n[INFO] 生成内容长度: {len(content)} 字符")
                        print(f"\n--- 生成内容预览 (前800字符) ---\n")
                        print(content[:800])
                        if len(content) > 800:
                            print(f"\n... (还有 {len(content) - 800} 字符)")

                    usage = data.get("usage", {})
                    if usage:
                        print(f"\n[INFO] Token 使用:")
                        print(f"  - 总计: {usage.get('total_tokens', 0)}")
                        print(f"  - Prompt: {usage.get('prompt_tokens', 0)}")
                        print(f"  - Completion: {usage.get('completion_tokens', 0)}")

                    print("-" * 70)
                    print("[RESULT] 测试成功!")
                    print(f"[INFO] 总耗时: {elapsed:.2f}s")
                    print(f"\n[IMPORTANT] 结论: 120s 超时可以成功完成长文本生成!")
                    return True

                except Exception as e:
                    print(f"[ERROR] 解析响应失败: {e}")
                    print(f"[INFO] 原始响应: {response.text[:500]}")
                    return False
            else:
                print(f"\n[ERROR] 请求失败!")
                print(f"[INFO] 状态码: {response.status_code}")
                print(f"[INFO] 响应: {response.text[:1000]}")
                return False

    except httpx.TimeoutException as e:
        elapsed = time.time() - start_time
        print(f"\n[ERROR] 请求超时!")
        print(f"[INFO] 配置的超时时间: {timeout}s")
        print(f"[INFO] 实际耗时: {elapsed:.2f}s")
        print(f"[INFO] 错误: {e}")
        return False

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n[ERROR] 发生错误!")
        print(f"[INFO] 错误类型: {type(e).__name__}")
        print(f"[INFO] 错误信息: {e}")
        print(f"[INFO] 耗时: {elapsed:.2f}s")
        import traceback
        traceback.print_exc()
        return False


async def main():
    success = await test_long_generation_120s()
    if success:
        print("\n" + "=" * 70)
        print("[FINAL] 所有测试通过!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("[FINAL] 测试失败!")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

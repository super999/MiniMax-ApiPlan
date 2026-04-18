#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MiniMax API 最小测试程序
"""
import asyncio
import time
import httpx
from dotenv import load_dotenv
import os

load_dotenv()


def mask_api_key(key):
    if not key:
        return "None"
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


async def test_minimax_api():
    api_key = os.getenv("MINIMAX_API_KEY")
    base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1/text/chatcompletion_v2")
    default_model = os.getenv("MINIMAX_DEFAULT_MODEL", "MiniMax-M2.7")
    timeout = float(os.getenv("MINIMAX_TIMEOUT", "120.0"))
    group_id = os.getenv("MINIMAX_GROUP_ID")

    print("=" * 60)
    print("MiniMax API 测试程序")
    print("=" * 60)
    print(f"API Key: {mask_api_key(api_key)}")
    print(f"Base URL: {base_url}")
    print(f"Model: {default_model}")
    print(f"Timeout: {timeout}s")
    print(f"Group ID: {group_id or '未配置'}")
    print("=" * 60)

    if not api_key:
        print("错误: MINIMAX_API_KEY 未配置")
        return False

    payload = {
        "model": default_model,
        "messages": [
            {
                "role": "user",
                "content": "你好，请用一句话介绍你自己。"
            }
        ],
        "max_tokens": 100
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    params = {}
    if group_id:
        params["GroupId"] = group_id

    print(f"\n请求 URL: {base_url}")
    print(f"请求参数: {params}")
    print(f"请求模型: {default_model}")
    print(f"请求内容: {payload['messages'][0]['content']}")
    print(f"超时时间: {timeout}s")
    print("-" * 60)

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
            print(f"HTTP 状态码: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"\n响应成功!")
                    print(f"响应 ID: {data.get('id')}")
                    print(f"响应模型: {data.get('model')}")

                    choices = data.get("choices", [])
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        print(f"\nAI 回复: {content[:200]}{'...' if len(content) > 200 else ''}")

                    usage = data.get("usage", {})
                    if usage:
                        print(f"\nToken 使用:")
                        print(f"  - 总计: {usage.get('total_tokens', 0)}")
                        print(f"  - Prompt: {usage.get('prompt_tokens', 0)}")
                        print(f"  - Completion: {usage.get('completion_tokens', 0)}")

                    print("-" * 60)
                    print("测试结果: ✅ 成功!")
                    print(f"总耗时: {elapsed:.2f}s")
                    return True

                except Exception as e:
                    print(f"解析响应失败: {e}")
                    print(f"原始响应: {response.text[:500]}")
                    return False
            else:
                print(f"\n请求失败!")
                print(f"状态码: {response.status_code}")
                print(f"响应: {response.text[:1000]}")
                return False

    except httpx.TimeoutException as e:
        elapsed = time.time() - start_time
        print(f"\n❌ 请求超时!")
        print(f"配置的超时时间: {timeout}s")
        print(f"实际耗时: {elapsed:.2f}s")
        print(f"错误: {e}")
        print("-" * 60)
        print("建议:")
        print("1. 增加 MINIMAX_TIMEOUT 到 120s 或更高")
        print("2. 检查网络连接是否正常")
        print("3. 确认 API 地址是否正确")
        return False

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"\n❌ 发生错误!")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {e}")
        print(f"耗时: {elapsed:.2f}s")
        import traceback
        traceback.print_exc()
        return False


async def test_multiple_timeouts():
    """测试不同超时时间"""
    print("\n" + "=" * 60)
    print("测试不同超时时间")
    print("=" * 60)

    api_key = os.getenv("MINIMAX_API_KEY")
    if not api_key:
        print("错误: MINIMAX_API_KEY 未配置")
        return

    base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimaxi.com/v1/text/chatcompletion_v2")
    default_model = os.getenv("MINIMAX_DEFAULT_MODEL", "MiniMax-M2.7")
    group_id = os.getenv("MINIMAX_GROUP_ID")

    test_timeouts = [60, 120, 180]

    for timeout in test_timeouts:
        print(f"\n--- 测试超时时间: {timeout}s ---")

        payload = {
            "model": default_model,
            "messages": [
                {"role": "user", "content": "你好，请用一句话介绍你自己。"}
            ],
            "max_tokens": 50
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        params = {}
        if group_id:
            params["GroupId"] = group_id

        try:
            start_time = time.time()
            timeout_config = httpx.Timeout(timeout=timeout, connect=10.0)

            async with httpx.AsyncClient(timeout=timeout_config) as client:
                response = await client.post(
                    base_url,
                    json=payload,
                    headers=headers,
                    params=params,
                )

                elapsed = time.time() - start_time

                if response.status_code == 200:
                    print(f"✅ 成功! 耗时: {elapsed:.2f}s")
                    return
                else:
                    print(f"❌ 失败! 状态码: {response.status_code}")
                    print(f"响应: {response.text[:500]}")

        except httpx.TimeoutException:
            elapsed = time.time() - start_time
            print(f"⏰ 超时! 耗时: {elapsed:.2f}s")
        except Exception as e:
            elapsed = time.time() - start_time
            print(f"❌ 错误: {e}, 耗时: {elapsed:.2f}s")


async def main():
    success = await test_minimax_api()

    if not success:
        await test_multiple_timeouts()


if __name__ == "__main__":
    asyncio.run(main())

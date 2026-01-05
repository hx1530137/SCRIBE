import os
import asyncio
import sys
import json
from datetime import datetime
from volcenginesdkarkruntime import AsyncArk

# 直接在代码中指定输入和输出文件路径
INPUT_JSON_PATH = r"C:\3b-top4-res-api.json"  # 输入JSON文件路径
OUTPUT_JSON_PATH = r"3b-top4-res-api-score-result.json"  # 输出结果文件路径


async def worker(
        worker_id: int,
        client: AsyncArk,
        requests: "asyncio.Queue[dict]",

        lock: asyncio.Lock  # 用于确保文件写入安全
):
    print(f"Worker {worker_id} is starting.")
    while True:
        request = await requests.get()
        try:
            # 获取原始请求内容
            content = request["messages"][1]["content"]

            # 执行推理
            completion = await client.batch.chat.completions.create(**request)

            # 准备要保存的结果
            result_item = {
                "original_content": content,
                "inference_result": completion.model_dump(),
                "timestamp": datetime.now().isoformat()  # 添加时间戳
            }

            # 加锁进行文件操作，避免并发冲突
            async with lock:
                # 尝试读取现有结果
                existing_results = []
                try:
                    if os.path.exists(OUTPUT_JSON_PATH):
                        with open(OUTPUT_JSON_PATH, 'r', encoding='utf-8') as f:
                            existing_results = json.load(f)
                            # 确保是列表格式
                            if not isinstance(existing_results, list):
                                existing_results = [existing_results]
                except json.JSONDecodeError:
                    print(f"Warning: {OUTPUT_JSON_PATH} is corrupted, starting with new file", file=sys.stderr)
                    existing_results = []
                except Exception as e:
                    print(f"Warning: Error reading {OUTPUT_JSON_PATH}: {e}", file=sys.stderr)
                    existing_results = []

                # 添加新结果
                existing_results.append(result_item)

                # 写入更新后的结果
                with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
                    json.dump(existing_results, f, ensure_ascii=False, indent=2)

            print(f"Worker {worker_id} completed and saved 1 task")

        except Exception as e:
            error_msg = f"Worker {worker_id} error: {e}"
            print(error_msg, file=sys.stderr)

            # 出错时也保存错误信息
            error_item = {
                "original_content": content if 'content' in locals() else "Unknown",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

            # 加锁保存错误信息
            async with lock:
                existing_results = []
                try:
                    if os.path.exists(OUTPUT_JSON_PATH):
                        with open(OUTPUT_JSON_PATH, 'r', encoding='utf-8') as f:
                            existing_results = json.load(f)
                            if not isinstance(existing_results, list):
                                existing_results = [existing_results]
                except Exception:
                    existing_results = []

                existing_results.append(error_item)

                with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
                    json.dump(existing_results, f, ensure_ascii=False, indent=2)

        finally:
            requests.task_done()


async def main():
    start = datetime.now()

    # 初始化输出文件（如果不存在则创建空列表）
    if not os.path.exists(OUTPUT_JSON_PATH):
        with open(OUTPUT_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump([], f)

    # 读取JSON文件
    try:
        with open(INPUT_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 确保数据是列表形式
        if not isinstance(data, list):
            data = [data]

        # 提取content字段，统计有效任务数量
        task_num = len(data)
        print(f"Total tasks to process: {task_num}")

        # 设置最大并发数，可根据API限制调整
        max_concurrent_tasks = min(1000, task_num)  # 不超过1000并发

    except Exception as e:
        print(f"Error reading JSON file: {e}", file=sys.stderr)
        return

    requests = asyncio.Queue()
    file_lock = asyncio.Lock()  # 创建文件锁

    client = AsyncArk(
        api_key='54b80726-c7b0-44f1-b7e6-01f16f64aa7f',
        timeout=24 * 3600,
    )

    # 将所有content加入请求队列
    for item in data:
        # 确保item包含content字段
        if "content" in item and isinstance(item["content"], str):
            await requests.put({
                #deepseek-v3
                # "model": "ep-bi-20250907152332-xr5pw",

                # doubao
                "model": "ep-bi-20251023215317-6v6r9",

                "messages": [
                    {
                        "role": "system",
                        "content": "你是三国历史专家，擅长给模型在三国志相关的回答打分",
                    },
                    {"role": "user", "content": item["content"]},
                ],
            })
        else:
            print(f"Skipping invalid item: {item}", file=sys.stderr)
            task_num -= 1

    # 创建工作线程
    tasks = [
        asyncio.create_task(worker(i, client, requests, file_lock))
        for i in range(max_concurrent_tasks)
    ]

    # 等待所有请求完成
    await requests.join()

    # 停止工作线程
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

    # 关闭客户端
    await client.close()

    end = datetime.now()
    print(f"Total time: {end - start}, Completed tasks: {task_num}")
    print(f"All results saved to {OUTPUT_JSON_PATH}")


if __name__ == "__main__":
    asyncio.run(main())

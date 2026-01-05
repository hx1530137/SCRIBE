import json
import os
from typing import List, Dict, Any, Callable


def process_json_file(input_path: str, output_path: str,
                      input_field: str, transform_func: Callable[[str], str]):
    """处理单个JSON文件"""
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON文件应该包含一个数组")

    processed_data = []
    for idx, item in enumerate(data, 1):
        if input_field not in item:
            print(f"警告: 第{idx}条数据缺少'{input_field}'字段")
            continue

        # 创建新对象，保留原始数据但修改指定字段
        new_item = item.copy()
        # 应用转换函数到指定字段
        new_item['content'] = transform_func(item[input_field])
        # 添加id字段
        new_item['id'] = idx
        processed_data.append(new_item)

    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    print(f"处理完成: {input_path} -> {output_path}")
    print(f"总处理条数: {len(processed_data)}")

    return processed_data


def process_json_directory(input_dir: str, output_path: str,
                           input_field: str, transform_func: Callable[[str], str],
                           merge_output: bool = True):
    """处理目录中的所有JSON文件

    参数:
        input_dir: 输入目录路径
        output_path: 输出路径（文件或目录）
        input_field: 输入字段名
        transform_func: 转换函数
        merge_output: 是否合并输出为一个JSON文件
    """
    if not os.path.exists(input_dir):
        print(f"错误: 目录 {input_dir} 不存在")
        return

    json_files = [f for f in os.listdir(input_dir) if f.endswith('.json')]

    if not json_files:
        print(f"在目录 {input_dir} 中未找到JSON文件")
        return

    if merge_output:
        # 合并模式：所有数据合并到一个JSON文件
        all_processed_data = []
        global_id = 1

        for json_file in json_files:
            input_path = os.path.join(input_dir, json_file)
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                print(f"警告: 文件 {json_file} 不包含数组，跳过")
                continue

            for item in data:
                if input_field not in item:
                    print(f"警告: 文件 {json_file} 中缺少'{input_field}'字段的数据")
                    continue

                # 创建新对象，保留原始数据但修改指定字段
                new_item = item.copy()
                # 应用转换函数到指定字段
                new_item['content'] = transform_func(item[input_field])
                # 添加全局连续的id字段
                new_item['id'] = global_id
                global_id += 1
                all_processed_data.append(new_item)

        # 确保输出目录存在
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 如果输出路径是目录，则使用默认文件名
        if os.path.isdir(output_path):
            output_path = os.path.join(output_path, "merged_output.json")

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_processed_data, f, ensure_ascii=False, indent=2)

        print(f"合并处理完成: {input_dir} -> {output_path}")
        print(f"总处理文件数: {len(json_files)}")
        print(f"总处理条数: {len(all_processed_data)}")

    else:
        # 非合并模式：每个文件对应一个JSON文件
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        for json_file in json_files:
            input_path = os.path.join(input_dir, json_file)
            # 保持原文件名，但放在输出目录中
            output_file_path = os.path.join(output_path, json_file)
            process_json_file(input_path, output_file_path, input_field, transform_func)


# 自定义内容转换函数 - 根据需要修改这个函数
def custom_transform(content: str) -> str:
    """自定义内容转换函数

    参数:
        content: 原始内容

    返回:
        转换后的内容
    """
    # 示例1: 在内容前后添加特定文本
    # return f"前缀文本 {content} 后缀文本"

    # 示例2: 替换特定文本
    # return content.replace("旧文本", "新文本")

    # 示例3: 根据内容长度添加不同文本
    # if len(content) > 50:
    #     return f"长文本: {content}"
    # else:
    #     return f"短文本: {content}"

    # 示例4: 添加当前时间戳
    # import datetime
    # return f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {content}"

    # 返回原始内容（不做任何修改）
    # return content
    return f"""给模型的回答进行打分，参考标准答案标签，从五个角度进行打分，分别是准确性、精炼度、引用相关性、完整性、幻觉率，每一项满分10分。打分结果只需要返回纯json格式的内容，具体如下：'{' 准确性: 精炼度: 引用相关性: 完整性: 幻觉率: '}'。\n\n 提问、标准回答标签、模型回答内容如下：\n{content}"""
    # return f"""{content}"""


# 在代码中直接指定参数
if __name__ == "__main__":
    # 配置参数 - 根据需要修改这些值
    INPUT_PATH = r"C:\Users\hx\PycharmProjects\shouxieshuzi\RAG-top-k-result\8b-top5\8b-top5-ios-predict-res\3b-top4-res.json"
    OUTPUT_PATH = r"C:\Users\hx\PycharmProjects\shouxieshuzi\RAG-top-k-result\8b-top5\8b-top5-ios-predict-res\3b-top4-res-api.json" 
    INPUT_FIELD = "content"  # 输入JSON中的字段名（需要被转换的字段）
    MERGE_OUTPUT = True  # 当输入是文件夹时，是否合并为一个JSON文件（True=合并，False=每个文件对应一个）

    # 根据输入路径类型决定处理方式
    if os.path.isfile(INPUT_PATH):
        process_json_file(INPUT_PATH, OUTPUT_PATH, INPUT_FIELD, custom_transform)
    elif os.path.isdir(INPUT_PATH):
        process_json_directory(INPUT_PATH, OUTPUT_PATH, INPUT_FIELD, custom_transform, MERGE_OUTPUT)
    else:
        print(f"错误: 路径 '{INPUT_PATH}' 不存在")
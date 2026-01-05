import json
import numpy as np
import os
import csv  # 新增csv模块用于处理CSV文件


def calculate_scores_from_json(json_file_path):
    """计算JSON文件中content数据的5个指标平均分和总平均分"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        accuracy_scores = []
        conciseness_scores = []
        reference_relevance_scores = []
        completeness_scores = []
        hallucination_scores = []
        all_scores = []

        for item in data:
            try:
                content_str = item['inference_result']['choices'][0]['message']['content']
                score_data = json.loads(content_str)

                accuracy = score_data.get('准确性', 0)
                conciseness = score_data.get('精炼度', 0)
                reference_relevance = score_data.get('引用相关性', 0)
                completeness = score_data.get('完整性', 0)
                hallucination = score_data.get('幻觉率', 0)

                accuracy_scores.append(accuracy)
                conciseness_scores.append(conciseness)
                reference_relevance_scores.append(reference_relevance)
                completeness_scores.append(completeness)
                hallucination_scores.append(hallucination)
                all_scores.extend([accuracy, conciseness, reference_relevance, completeness, hallucination])

            except (KeyError, json.JSONDecodeError) as e:
                print(f"解析数据时出错: {e}")
                continue

        # 计算各指标平均分
        avg_accuracy = np.mean(accuracy_scores) if accuracy_scores else 0
        avg_conciseness = np.mean(conciseness_scores) if conciseness_scores else 0
        avg_reference_relevance = np.mean(reference_relevance_scores) if reference_relevance_scores else 0
        avg_completeness = np.mean(completeness_scores) if completeness_scores else 0
        avg_hallucination = np.mean(hallucination_scores) if hallucination_scores else 0
        total_avg = np.mean(all_scores) if all_scores else 0

        return {
            'accuracy_avg': avg_accuracy,
            'conciseness_avg': avg_conciseness,
            'reference_relevance_avg': avg_reference_relevance,
            'completeness_avg': avg_completeness,
            'hallucination_avg': avg_hallucination,
            'total_avg': total_avg,
            'total_records': len(accuracy_scores)
        }

    except FileNotFoundError:
        print(f"文件 {json_file_path} 未找到")
        return None
    except json.JSONDecodeError:
        print("JSON文件格式错误")
        return None


def process_json_folder(folder_path):
    """处理文件夹中所有JSON文件，汇总结果到CSV文件"""
    if not os.path.isdir(folder_path):
        print(f"错误：文件夹 {folder_path} 不存在")
        return

    # 存储所有文件的结果（用于写入CSV）
    all_file_results = []
    # 序号计数器
    file_index = 1

    # 遍历文件夹中的JSON文件
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.json'):
            json_file_path = os.path.join(folder_path, filename)
            print(f"\n正在处理文件 [{file_index}]：{json_file_path}")

            # 计算当前文件的评分
            scores_result = calculate_scores_from_json(json_file_path)

            if scores_result:
                # 构造当前文件的结果数据（按CSV列顺序）
                file_result = {
                    '序号': file_index,
                    '文件名称': filename,  # 仅保留文件名（不含路径）
                    '准确性平均分': round(scores_result['accuracy_avg'], 2),
                    '精炼度平均分': round(scores_result['conciseness_avg'], 2),
                    '引用相关性平均分': round(scores_result['reference_relevance_avg'], 2),
                    '完整性平均分': round(scores_result['completeness_avg'], 2),
                    '幻觉率平均分': round(scores_result['hallucination_avg'], 2),
                    '总平均分': round(scores_result['total_avg'], 2)
                }
                all_file_results.append(file_result)
                file_index += 1  # 只有成功处理的文件才递增序号

    # 生成CSV文件（保存到目标文件夹下，命名为“评分汇总.csv”）
    csv_file_path = os.path.join(folder_path, "评分汇总.csv")
    try:
        with open(csv_file_path, 'w', encoding='utf-8-sig', newline='') as csvfile:
            # 定义CSV列名（按要求的8个列）
            fieldnames = [
                '序号',
                '文件名称',
                '准确性平均分',
                '精炼度平均分',
                '引用相关性平均分',
                '完整性平均分',
                '幻觉率平均分',
                '总平均分'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # 写入表头
            writer.writeheader()
            # 写入所有文件的结果
            for result in all_file_results:
                writer.writerow(result)

        print(f"\n所有文件处理完成，结果已汇总保存至：{csv_file_path}")
        print(f"共成功处理 {len(all_file_results)} 个JSON文件")

    except IOError as e:
        print(f"写入CSV文件时出错：{e}")


# 使用示例
if __name__ == "__main__":
    # 替换为包含JSON文件的文件夹路径
    json_folder_path = r"C:"

    # 处理文件夹并生成汇总CSV
    process_json_folder(json_folder_path)
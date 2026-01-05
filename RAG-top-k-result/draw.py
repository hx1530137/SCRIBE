import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib import style

# Set style and color palette
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
plt.rcParams['axes.unicode_minus'] = False
style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Read data
df = pd.read_excel('accuracy_results.xlsx', sheet_name='准确率统计')

# Model mapping
model_mapping = {
    '4b': 'qwen3-embedding-4B',
    '8b': 'qwen3-embedding-8B',
    'bge-m3': 'bge-m3'
}

# Extract model name and topk values from file names
df['模型'] = df['文件名'].str.extract(r'([\w-]+)-top\d+')
df['topk'] = df['文件名'].str.extract(r'top(\d)').astype(int)

# Apply model mapping
df['Model Name'] = df['模型'].map(model_mapping)

# Create figure and subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# 1. Line chart - Show accuracy trends for different models across topk values
for model in df['Model Name'].unique():
    model_data = df[df['Model Name'] == model].sort_values('topk')
    ax1.plot(model_data['topk'], model_data['准确率(%)'],
             marker='o', linewidth=2.5, markersize=8, label=model)

ax1.set_xlabel('Top K', fontsize=12)
ax1.set_ylabel('Accuracy (%)', fontsize=12)
ax1.set_title('Accuracy Comparison Across Models by TopK', fontsize=14, fontweight='bold')
ax1.legend(loc='upper left', bbox_to_anchor=(1.02, 1), frameon=True, fancybox=True, shadow=True)
ax1.grid(True, alpha=0.3)
ax1.set_xticks(df['topk'].unique())

# 2. Grouped bar chart - Detailed comparison of accuracy across models and topk values
x = np.arange(len(df['topk'].unique()))
width = 0.25
models = df['Model Name'].unique()

for i, model in enumerate(models):
    model_data = df[df['Model Name'] == model].sort_values('topk')
    ax2.bar(x + i * width, model_data['准确率(%)'], width, label=model, alpha=0.8)

ax2.set_xlabel('Top K', fontsize=12)
ax2.set_ylabel('Accuracy (%)', fontsize=12)
ax2.set_title('Detailed Accuracy Comparison by Model and TopK', fontsize=14, fontweight='bold')
ax2.set_xticks(x + width)
ax2.set_xticklabels([f'top{k}' for k in sorted(df['topk'].unique())])
ax2.legend(loc='upper left', bbox_to_anchor=(1.02, 1), frameon=True, fancybox=True, shadow=True)
ax2.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.savefig('model_accuracy_comparison.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# 3. Heatmap - Display accuracy matrix
plt.figure(figsize=(10, 6))

# Prepare heatmap data
heatmap_data = df.pivot(index='Model Name', columns='topk', values='准确率(%)')
heatmap_data = heatmap_data.reindex(index=['qwen3-embedding-4B', 'qwen3-embedding-8B', 'bge-m3'])

sns.heatmap(heatmap_data, annot=True, cmap='YlOrRd', fmt='.1f',
            linewidths=0.5, cbar_kws={'label': 'Accuracy (%)'})
plt.title('Model Accuracy Heatmap', fontsize=14, fontweight='bold', pad=20)
plt.xlabel('Top K')
plt.ylabel('Model')

plt.tight_layout()
plt.savefig('model_accuracy_heatmap.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# 4. Area chart - Show accuracy changes with topk
plt.figure(figsize=(12, 6))

# Prepare area chart data
area_data = df.pivot(index='topk', columns='Model Name', values='准确率(%)')
area_data = area_data[['qwen3-embedding-4B', 'qwen3-embedding-8B', 'bge-m3']]

plt.stackplot(area_data.index, area_data.T, labels=area_data.columns, alpha=0.7)
plt.plot(area_data.index, area_data['qwen3-embedding-4B'], 'o-', linewidth=2, markersize=6)
plt.plot(area_data.index, area_data['qwen3-embedding-8B'], 'o-', linewidth=2, markersize=6)
plt.plot(area_data.index, area_data['bge-m3'], 'o-', linewidth=2, markersize=6)

plt.xlabel('Top K', fontsize=12)
plt.ylabel('Accuracy (%)', fontsize=12)
plt.title('Accuracy Trend by TopK', fontsize=14, fontweight='bold')
plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1), frameon=True, fancybox=True, shadow=True)
plt.grid(True, alpha=0.3)

plt.tight_layout(rect=[0, 0, 0.85, 1])
plt.savefig('model_accuracy_area.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# 5. Radar chart - Multi-dimensional view of model performance
plt.figure(figsize=(10, 8))
ax = plt.subplot(111, projection='polar')

# Prepare radar chart data
categories = [f'top{k}' for k in sorted(df['topk'].unique())]
N = len(categories)

# Calculate angles
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]  # Close the radar chart

# Plot radar chart for each model
for model in df['Model Name'].unique():
    model_data = df[df['Model Name'] == model].sort_values('topk')
    values = model_data['准确率(%)'].values.tolist()
    values += values[:1]  # Close the data

    ax.plot(angles, values, 'o-', linewidth=2, label=model, markersize=6)
    ax.fill(angles, values, alpha=0.1)

ax.set_xticks(angles[:-1])
ax.set_xticklabels(categories, fontsize=10)
ax.set_ylim(50, 100)
ax.set_title('Model Accuracy Radar Chart by TopK', size=14, fontweight='bold', pad=20)

# 将雷达图的图例放在图像内的右上角
ax.legend(loc='upper right', frameon=True, fancybox=True, shadow=True)

plt.tight_layout()
plt.savefig('model_accuracy_radar.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# Print performance summary
print("Model Performance Summary:")
summary = df.groupby('Model Name').agg({
    '准确率(%)': ['min', 'max', 'mean'],
    '总样本数': 'first'
}).round(2)
print(summary)
---
name: data-analyst-agent
description: Build AI agents that analyze datasets, create visualizations, and extract insights through autonomous code execution.
---

# Data Analyst Agent Skill

> Build AI agents that analyze datasets, create visualizations, and extract insights through autonomous code execution.

## Overview

Data Analyst Agents combine:
- **LLM reasoning** for understanding questions and planning analysis
- **Code execution** for data manipulation (pandas, numpy)
- **Visualization** for creating plots (matplotlib, seaborn, plotly)
- **Iterative refinement** through the agent loop

---

## Quick Start

### Setup
```python
from e2b_code_interpreter import Sandbox
from openai import OpenAI

# Create sandbox and upload data
sbx = Sandbox.create()
with open("data.csv", "r") as f:
    sbx.files.write("data.csv", f.read())

client = OpenAI()
```

### System Prompt
```python
system = """You are a senior data analyst and Python programmer.

Your task is to help users understand their data through:
1. Exploratory data analysis
2. Statistical summaries
3. Visualizations
4. Insights and recommendations

You must run all code using the `execute_code` tool.
The user has uploaded a dataset called `data.csv`.

When creating visualizations:
- Use matplotlib or seaborn
- Always include titles and labels
- Choose appropriate chart types for the data
- Use clear, professional styling

When providing insights:
- Be specific with numbers
- Identify patterns and anomalies
- Suggest actionable next steps
"""
```

### Run Agent
```python
from lib.coding_agent import coding_agent

messages = coding_agent(
    client=client,
    query="What is this data about? Give me a summary.",
    system=system,
    tools={"execute_code": lambda code: sbx.run_code(code).to_json()},
    tools_schemas=[execute_code_schema],
    max_steps=10,
    sbx=sbx
)
```

---

## Common Analysis Patterns

### Initial Data Exploration
```python
# Agent typically runs this first
"""
import pandas as pd

df = pd.read_csv('data.csv')
print("Shape:", df.shape)
print("\\nColumns:", df.columns.tolist())
print("\\nData types:")
print(df.dtypes)
print("\\nFirst 5 rows:")
print(df.head())
print("\\nBasic statistics:")
print(df.describe())
print("\\nMissing values:")
print(df.isnull().sum())
"""
```

### Aggregation Queries
```python
# "Aggregate by category"
"""
import pandas as pd

df = pd.read_csv('data.csv')
aggregated = df.groupby('category').agg({
    'value': ['count', 'sum', 'mean', 'std'],
    'date': ['min', 'max']
})
print(aggregated)
"""
```

### Time Series Analysis
```python
# "Show trends over time"
"""
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('data.csv')
df['date'] = pd.to_datetime(df['date'])
df = df.set_index('date')

# Resample to monthly
monthly = df.resample('M')['value'].sum()

plt.figure(figsize=(12, 6))
plt.plot(monthly.index, monthly.values, marker='o')
plt.title('Monthly Trend')
plt.xlabel('Date')
plt.ylabel('Value')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
"""
```

### Distribution Analysis
```python
# "Show distribution of values"
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data.csv')

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Histogram
axes[0].hist(df['value'], bins=30, edgecolor='black', alpha=0.7)
axes[0].set_title('Distribution of Values')
axes[0].set_xlabel('Value')
axes[0].set_ylabel('Frequency')

# Box plot
sns.boxplot(data=df, y='value', ax=axes[1])
axes[1].set_title('Value Box Plot')

plt.tight_layout()
plt.show()
"""
```

### Correlation Analysis
```python
# "What correlations exist?"
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('data.csv')
numeric_cols = df.select_dtypes(include=['number']).columns

correlation_matrix = df[numeric_cols].corr()

plt.figure(figsize=(10, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix')
plt.tight_layout()
plt.show()

print("Strong correlations (>0.7 or <-0.7):")
for i in range(len(correlation_matrix.columns)):
    for j in range(i+1, len(correlation_matrix.columns)):
        corr = correlation_matrix.iloc[i, j]
        if abs(corr) > 0.7:
            print(f"  {correlation_matrix.columns[i]} vs {correlation_matrix.columns[j]}: {corr:.2f}")
"""
```

---

## Visualization Library

### Bar Charts
```python
"""
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('data.csv')
counts = df['category'].value_counts()

plt.figure(figsize=(10, 6))
plt.bar(counts.index, counts.values, color='steelblue', edgecolor='black')
plt.title('Count by Category')
plt.xlabel('Category')
plt.ylabel('Count')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()
"""
```

### Pie Charts
```python
"""
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('data.csv')
distribution = df['category'].value_counts()

plt.figure(figsize=(8, 8))
plt.pie(distribution.values, labels=distribution.index, autopct='%1.1f%%',
        startangle=90, colors=plt.cm.Pastel1.colors)
plt.title('Distribution by Category')
plt.show()
"""
```

### Scatter Plots
```python
"""
import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('data.csv')

plt.figure(figsize=(10, 6))
plt.scatter(df['x'], df['y'], alpha=0.6, c=df['category'].astype('category').cat.codes,
            cmap='viridis')
plt.colorbar(label='Category')
plt.title('X vs Y by Category')
plt.xlabel('X Value')
plt.ylabel('Y Value')
plt.tight_layout()
plt.show()
"""
```

### Multi-Plot Dashboard
```python
"""
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

df = pd.read_csv('data.csv')

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Distribution
axes[0, 0].hist(df['value'], bins=30, edgecolor='black', alpha=0.7)
axes[0, 0].set_title('Value Distribution')

# Plot 2: Time series
df_sorted = df.sort_values('date')
axes[0, 1].plot(df_sorted['date'], df_sorted['value'])
axes[0, 1].set_title('Value Over Time')
axes[0, 1].tick_params(axis='x', rotation=45)

# Plot 3: Category breakdown
df.groupby('category')['value'].sum().plot(kind='bar', ax=axes[1, 0])
axes[1, 0].set_title('Value by Category')

# Plot 4: Correlation heatmap
numeric_df = df.select_dtypes(include=['number'])
sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', ax=axes[1, 1])
axes[1, 1].set_title('Correlations')

plt.tight_layout()
plt.show()
"""
```

---

## Advanced Patterns

### Handling Missing Data
```python
"""
import pandas as pd

df = pd.read_csv('data.csv')

# Report missing data
missing = df.isnull().sum()
missing_pct = (missing / len(df)) * 100

print("Missing Data Report:")
for col in df.columns:
    if missing[col] > 0:
        print(f"  {col}: {missing[col]} ({missing_pct[col]:.1f}%)")

# Options for handling:
# 1. Drop rows with missing values
df_clean = df.dropna()

# 2. Fill with mean/median/mode
df['numeric_col'] = df['numeric_col'].fillna(df['numeric_col'].median())
df['categorical_col'] = df['categorical_col'].fillna(df['categorical_col'].mode()[0])

# 3. Forward/backward fill for time series
df['value'] = df['value'].fillna(method='ffill')
"""
```

### Outlier Detection
```python
"""
import pandas as pd
import numpy as np

df = pd.read_csv('data.csv')

# IQR method
Q1 = df['value'].quantile(0.25)
Q3 = df['value'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = df[(df['value'] < lower_bound) | (df['value'] > upper_bound)]
print(f"Found {len(outliers)} outliers ({len(outliers)/len(df)*100:.1f}%)")
print(f"Lower bound: {lower_bound:.2f}, Upper bound: {upper_bound:.2f}")
"""
```

### Statistical Tests
```python
"""
import pandas as pd
from scipy import stats

df = pd.read_csv('data.csv')

# T-test between two groups
group_a = df[df['category'] == 'A']['value']
group_b = df[df['category'] == 'B']['value']

t_stat, p_value = stats.ttest_ind(group_a, group_b)
print(f"T-test: t={t_stat:.3f}, p={p_value:.4f}")
if p_value < 0.05:
    print("Significant difference between groups")
else:
    print("No significant difference between groups")
"""
```

---

## Gradio UI Integration

```python
from lib.ui import ui
from lib.coding_agent import coding_agent

# Create sandbox with data
sbx = Sandbox.create()
sbx.files.write("data.csv", data_content)

# Launch UI
ui(
    coding_agent,
    messages=[],
    client=client,
    system=system,
    tools_schemas=[execute_code_schema],
    tools={"execute_code": lambda code: sbx.run_code(code).to_json()},
    max_steps=10,
    sbx=sbx,
).launch(share=True, height=800)
```

---

## Example Queries

Good queries to ask a data analyst agent:

1. **Exploration**: "What is this data about? Give me a summary."
2. **Aggregation**: "Can you aggregate the data by [column]?"
3. **Trends**: "What trends do you see over time?"
4. **Comparison**: "Compare [group A] vs [group B]"
5. **Distribution**: "What's the distribution of [column]?"
6. **Correlation**: "What correlations exist in the data?"
7. **Anomalies**: "Are there any outliers or anomalies?"
8. **Top/Bottom**: "What are the top 10 [items] by [metric]?"
9. **Filtering**: "Show me only [condition] data"
10. **Export**: "Create a summary report"

---

## Dependencies

Standard data analysis stack:
```
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
scipy>=1.10
plotly>=5.14  # optional for interactive
```

These are typically pre-installed in E2B sandboxes.

---

## Integration with a CRM

For CRM analytics (adapt the system prompt to your domain):
```python
system = """You are a senior data analyst for a <your-business-type> CRM.

The data may contain:
- Leads (potential clients with contact info, source, stage)
- Projects (engagements with budgets, timelines, status)
- Invoices (payments, amounts, dates)
- Clients (companies, contacts)

Help the user understand:
- Sales pipeline health
- Revenue trends
- Conversion rates
- Client concentration
- Project profitability

Always provide actionable insights relevant to <your-business-type>.
"""
```

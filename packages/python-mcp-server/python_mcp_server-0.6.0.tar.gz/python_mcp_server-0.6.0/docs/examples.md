# Examples

Practical usage examples and common patterns for the Python MCP Server v0.6.0 with FastMCP integration and advanced session management.

## Basic Usage Examples

### Simple Code Execution
```python
import asyncio
from fastmcp.client import Client

async def basic_execution():
    async with Client("http://localhost:8000/mcp") as client:
        # Basic Python calculation
        result = await client.call_tool("run_python_code", {
            "code": """
x = 10
y = 20
result = x * y + 5
print(f"Result: {result}")
"""
        })
        print("Output:", result.data["stdout"])

asyncio.run(basic_execution())
```

### Data Analysis Workflow
```python
async def data_analysis_example():
    async with Client("http://localhost:8000/mcp") as client:
        # Install required packages
        await client.call_tool("install_dependencies", {
            "packages": ["pandas", "numpy", "matplotlib", "seaborn"]
        })
        
        # Create and analyze sample data
        await client.call_tool("run_python_code", {
            "code": """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Create sample dataset
np.random.seed(42)
data = {
    'temperature': np.random.normal(25, 5, 1000),
    'humidity': np.random.normal(60, 15, 1000),
    'pressure': np.random.normal(1013, 20, 1000),
    'wind_speed': np.random.exponential(10, 1000)
}
df = pd.DataFrame(data)

# Basic statistics
print("Dataset Overview:")
print(f"Shape: {df.shape}")
print("\\nSummary Statistics:")
print(df.describe())

# Create correlation matrix
correlation = df.corr()
print("\\nCorrelation Matrix:")
print(correlation)
"""
        })
        
        # Create visualizations
        await client.call_tool("run_python_code", {
            "code": """
# Create visualizations
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Temperature distribution
axes[0, 0].hist(df['temperature'], bins=30, alpha=0.7, color='red')
axes[0, 0].set_title('Temperature Distribution')
axes[0, 0].set_xlabel('Temperature (°C)')

# Scatter plot: Temperature vs Humidity
axes[0, 1].scatter(df['temperature'], df['humidity'], alpha=0.5)
axes[0, 1].set_title('Temperature vs Humidity')
axes[0, 1].set_xlabel('Temperature (°C)')
axes[0, 1].set_ylabel('Humidity (%)')

# Pressure over time (assuming sequential data)
axes[1, 0].plot(df['pressure'][:100])
axes[1, 0].set_title('Pressure Trend (First 100 points)')
axes[1, 0].set_xlabel('Time')
axes[1, 0].set_ylabel('Pressure (hPa)')

# Box plot of wind speed
axes[1, 1].boxplot(df['wind_speed'])
axes[1, 1].set_title('Wind Speed Distribution')
axes[1, 1].set_ylabel('Wind Speed (m/s)')

plt.tight_layout()
plt.savefig('outputs/weather_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("Analysis complete! Visualization saved as 'weather_analysis.png'")
"""
        })

asyncio.run(data_analysis_example())
```

## Machine Learning Example

### End-to-End ML Pipeline
```python
async def ml_pipeline_example():
    async with Client("http://localhost:8000/mcp") as client:
        # Create ML session
        await client.call_tool("create_session", {
            "session_id": "ml_pipeline",
            "description": "Complete machine learning pipeline"
        })
        await client.call_tool("switch_session", {"session_id": "ml_pipeline"})
        
        # Install ML packages
        await client.call_tool("install_dependencies", {
            "packages": [
                "scikit-learn", 
                "pandas", 
                "numpy", 
                "matplotlib",
                "seaborn",
                "joblib"
            ]
        })
        
        # Load and prepare data
        await client.call_tool("run_python_code", {
            "code": """
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

# Generate synthetic dataset
X, y = make_classification(
    n_samples=1000, 
    n_features=20, 
    n_informative=15, 
    n_redundant=5, 
    n_classes=3, 
    random_state=42
)

# Create DataFrame for easier handling
feature_names = [f'feature_{i}' for i in range(X.shape[1])]
df = pd.DataFrame(X, columns=feature_names)
df['target'] = y

print(f"Dataset shape: {df.shape}")
print(f"Target distribution:\\n{df['target'].value_counts()}")
"""
        })
        
        # Exploratory Data Analysis
        await client.call_tool("run_python_code", {
            "code": """
# EDA Visualizations
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Target distribution
axes[0, 0].bar(df['target'].value_counts().index, df['target'].value_counts().values)
axes[0, 0].set_title('Target Class Distribution')
axes[0, 0].set_xlabel('Class')
axes[0, 0].set_ylabel('Count')

# Feature correlation heatmap (top 10 features)
corr_matrix = df[feature_names[:10]].corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=axes[0, 1])
axes[0, 1].set_title('Feature Correlation (Top 10)')

# Feature importance by variance
feature_variance = df[feature_names].var().sort_values(ascending=False)
axes[1, 0].bar(range(len(feature_variance[:10])), feature_variance[:10].values)
axes[1, 0].set_title('Top 10 Features by Variance')
axes[1, 0].set_xlabel('Feature Rank')
axes[1, 0].set_ylabel('Variance')

# Box plot of first few features by class
df_melted = df[['feature_0', 'feature_1', 'feature_2', 'target']].melt(
    id_vars='target', var_name='feature', value_name='value'
)
sns.boxplot(data=df_melted, x='feature', y='value', hue='target', ax=axes[1, 1])
axes[1, 1].set_title('Feature Distribution by Class')

plt.tight_layout()
plt.savefig('outputs/eda_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

print("EDA complete!")
"""
        })
        
        # Model training and comparison
        await client.call_tool("run_python_code", {
            "code": """
# Prepare data for modeling
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Define models to compare
models = {
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000),
    'SVM': SVC(random_state=42, probability=True)
}

# Train and evaluate models
results = {}
for name, model in models.items():
    print(f"\\nTraining {name}...")
    
    # Use scaled data for LogReg and SVM, original for RandomForest
    if name == 'Random Forest':
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)
    else:
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        y_prob = model.predict_proba(X_test_scaled)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)
    
    results[name] = {
        'accuracy': accuracy,
        'precision': report['macro avg']['precision'],
        'recall': report['macro avg']['recall'],
        'f1': report['macro avg']['f1-score']
    }
    
    print(f"{name} Accuracy: {accuracy:.4f}")

# Compare results
results_df = pd.DataFrame(results).T
print("\\nModel Comparison:")
print(results_df.round(4))
"""
        })
        
        # Save best model and create final visualizations
        await client.call_tool("run_python_code", {
            "code": """
# Find best model
best_model_name = results_df['accuracy'].idxmax()
best_accuracy = results_df['accuracy'].max()

print(f"\\nBest Model: {best_model_name} (Accuracy: {best_accuracy:.4f})")

# Train best model and save
best_model = models[best_model_name]
if best_model_name == 'Random Forest':
    best_model.fit(X_train, y_train)
    y_pred_final = best_model.predict(X_test)
else:
    best_model.fit(X_train_scaled, y_train)
    y_pred_final = best_model.predict(X_test_scaled)

# Save model and scaler
joblib.dump(best_model, 'outputs/best_model.pkl')
joblib.dump(scaler, 'outputs/scaler.pkl')

# Create final visualization
fig, axes = plt.subplots(1, 2, figsize=(15, 6))

# Model comparison
axes[0].bar(results_df.index, results_df['accuracy'])
axes[0].set_title('Model Accuracy Comparison')
axes[0].set_ylabel('Accuracy')
axes[0].tick_params(axis='x', rotation=45)

# Confusion matrix for best model
cm = confusion_matrix(y_test, y_pred_final)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[1])
axes[1].set_title(f'Confusion Matrix - {best_model_name}')
axes[1].set_xlabel('Predicted')
axes[1].set_ylabel('Actual')

plt.tight_layout()
plt.savefig('outputs/ml_results.png', dpi=300, bbox_inches='tight')
plt.show()

print("\\nML Pipeline Complete!")
print(f"Best model ({best_model_name}) saved as 'best_model.pkl'")
print("Scaler saved as 'scaler.pkl'")
"""
        })

asyncio.run(ml_pipeline_example())
```

## Web Scraping and Data Collection

### Web Data Analysis
```python
async def web_scraping_example():
    async with Client("http://localhost:8000/mcp") as client:
        await client.call_tool("install_dependencies", {
            "packages": ["requests", "beautifulsoup4", "pandas", "matplotlib"]
        })
        
        await client.call_tool("run_python_code", {
            "code": """
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import time

# Example: Scrape weather data (replace with actual API/website)
# Note: Always respect robots.txt and rate limits

def scrape_example_data():
    # Simulating scraped data for demonstration
    import random
    import datetime as dt
    
    dates = [dt.date.today() - dt.timedelta(days=i) for i in range(30, 0, -1)]
    temperatures = [random.randint(15, 30) for _ in dates]
    
    return pd.DataFrame({
        'date': dates,
        'temperature': temperatures
    })

# Get data
df = scrape_example_data()
print(f"Collected {len(df)} data points")
print(df.head())

# Analyze trends
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date')

# Create visualization
plt.figure(figsize=(12, 6))
plt.plot(df['date'], df['temperature'], marker='o')
plt.title('Temperature Trend Over Time')
plt.xlabel('Date')
plt.ylabel('Temperature (°C)')
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/temperature_trend.png')
plt.show()

# Save data
df.to_csv('outputs/weather_data.csv', index=False)
print("Data saved to weather_data.csv")
"""
        })

asyncio.run(web_scraping_example())
```

## File Processing Examples

### CSV Data Processing
```python
async def csv_processing_example():
    async with Client("http://localhost:8000/mcp") as client:
        # Create sample CSV file
        await client.call_tool("write_file", {
            "path": "sample_sales.csv",
            "content": """date,product,quantity,price,customer
2024-01-01,Widget A,10,29.99,Customer 1
2024-01-02,Widget B,5,39.99,Customer 2
2024-01-03,Widget A,15,29.99,Customer 3
2024-01-04,Widget C,8,49.99,Customer 1
2024-01-05,Widget B,12,39.99,Customer 4
2024-01-06,Widget A,20,29.99,Customer 2
2024-01-07,Widget C,6,49.99,Customer 5"""
        })
        
        # Process the data
        await client.call_tool("run_python_code", {
            "code": """
import pandas as pd
import matplotlib.pyplot as plt

# Load and process data
df = pd.read_csv('sample_sales.csv')
df['date'] = pd.to_datetime(df['date'])
df['total'] = df['quantity'] * df['price']

print("Sales Data Overview:")
print(f"Shape: {df.shape}")
print(f"Date range: {df['date'].min()} to {df['date'].max()}")
print(f"Total sales: ${df['total'].sum():.2f}")

# Analysis by product
product_summary = df.groupby('product').agg({
    'quantity': 'sum',
    'total': 'sum',
    'customer': 'nunique'
}).round(2)
print("\\nProduct Summary:")
print(product_summary)

# Customer analysis
customer_summary = df.groupby('customer').agg({
    'total': 'sum',
    'quantity': 'sum'
}).round(2)
print("\\nTop Customers:")
print(customer_summary.sort_values('total', ascending=False))
"""
        })
        
        # Create visualizations
        await client.call_tool("run_python_code", {
            "code": """
# Create comprehensive sales dashboard
fig, axes = plt.subplots(2, 2, figsize=(15, 10))

# Sales by product
product_totals = df.groupby('product')['total'].sum()
axes[0, 0].pie(product_totals.values, labels=product_totals.index, autopct='%1.1f%%')
axes[0, 0].set_title('Sales Distribution by Product')

# Daily sales trend
daily_sales = df.groupby('date')['total'].sum()
axes[0, 1].plot(daily_sales.index, daily_sales.values, marker='o')
axes[0, 1].set_title('Daily Sales Trend')
axes[0, 1].set_xlabel('Date')
axes[0, 1].set_ylabel('Sales ($)')
axes[0, 1].tick_params(axis='x', rotation=45)

# Quantity by product
quantity_by_product = df.groupby('product')['quantity'].sum()
axes[1, 0].bar(quantity_by_product.index, quantity_by_product.values)
axes[1, 0].set_title('Total Quantity Sold by Product')
axes[1, 0].set_xlabel('Product')
axes[1, 0].set_ylabel('Quantity')

# Customer spending
customer_spending = df.groupby('customer')['total'].sum().sort_values(ascending=True)
axes[1, 1].barh(customer_spending.index, customer_spending.values)
axes[1, 1].set_title('Customer Spending')
axes[1, 1].set_xlabel('Total Spent ($)')

plt.tight_layout()
plt.savefig('outputs/sales_dashboard.png', dpi=300, bbox_inches='tight')
plt.show()

# Export processed data
df.to_csv('outputs/processed_sales.csv', index=False)
print("\\nDashboard saved as 'sales_dashboard.png'")
print("Processed data saved as 'processed_sales.csv'")
"""
        })

asyncio.run(csv_processing_example())
```

## Session-Based Workflows

### Parallel Data Processing
```python
async def parallel_processing_example():
    async with Client("http://localhost:8000/mcp") as client:
        # Create sessions for different data processing tasks
        tasks = [
            ("text_processing", "Natural language processing"),
            ("image_processing", "Image analysis and manipulation"),
            ("data_cleaning", "Data preprocessing and cleaning")
        ]
        
        # Set up sessions
        for session_id, description in tasks:
            await client.call_tool("create_session", {
                "session_id": session_id,
                "description": description
            })
        
        # Text processing session
        await client.call_tool("switch_session", {"session_id": "text_processing"})
        await client.call_tool("install_dependencies", {
            "packages": ["nltk", "wordcloud", "textblob"]
        })
        
        await client.call_tool("run_python_code", {
            "code": """
import nltk
from wordcloud import WordCloud
from textblob import TextBlob
import matplotlib.pyplot as plt

# Sample text data
text = '''
Machine learning is a method of data analysis that automates analytical model building.
It is a branch of artificial intelligence based on the idea that systems can learn from data,
identify patterns and make decisions with minimal human intervention.
'''

# Download required NLTK data
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

# Text analysis
blob = TextBlob(text)
sentiment = blob.sentiment

print("Text Analysis Results:")
print(f"Sentiment: Polarity={sentiment.polarity:.2f}, Subjectivity={sentiment.subjectivity:.2f}")
print(f"Word count: {len(blob.words)}")

# Create word cloud
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)

plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.title('Text Word Cloud')
plt.savefig('outputs/text_wordcloud.png', bbox_inches='tight')
plt.show()

print("Text processing complete!")
"""
        })
        
        # Image processing session (simulation)
        await client.call_tool("switch_session", {"session_id": "image_processing"})
        await client.call_tool("install_dependencies", {
            "packages": ["pillow", "numpy", "matplotlib"]
        })
        
        await client.call_tool("run_python_code", {
            "code": """
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import matplotlib.pyplot as plt

# Create a sample image
img = Image.new('RGB', (400, 300), color='lightblue')
draw = ImageDraw.Draw(img)

# Add some shapes
draw.rectangle([50, 50, 150, 150], fill='red', outline='black')
draw.ellipse([200, 50, 300, 150], fill='green', outline='black')
draw.polygon([(100, 200), (150, 250), (50, 250)], fill='yellow', outline='black')

# Apply filters
blurred = img.filter(ImageFilter.BLUR)
edges = img.filter(ImageFilter.FIND_EDGES)

# Create visualization
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

axes[0].imshow(img)
axes[0].set_title('Original')
axes[0].axis('off')

axes[1].imshow(blurred)
axes[1].set_title('Blurred')
axes[1].axis('off')

axes[2].imshow(edges)
axes[2].set_title('Edge Detection')
axes[2].axis('off')

plt.tight_layout()
plt.savefig('outputs/image_processing.png', dpi=300, bbox_inches='tight')
plt.show()

# Save processed images
img.save('outputs/original_image.png')
blurred.save('outputs/blurred_image.png')

print("Image processing complete!")
"""
        })
        
        # Check session status
        sessions = await client.call_tool("list_sessions")
        print(f"Active sessions: {list(sessions.data['sessions'].keys())}")

asyncio.run(parallel_processing_example())
```

These examples demonstrate the versatility and power of the Python Interpreter MCP Server for various data science, machine learning, and automation tasks.
# NCES School Courses for the Exchange of Data (SCED) Codes Matching Tool
A Python package for matching K-12 course names and descriptions to standardized NCES School Courses for the Exchange of Data (SCED) codes.

## Installation

Install the package using pip:

```bash
pip install sced-matcher
```

## Usage

### Basic Usage

```python
from sced_matcher import SCEDMatcher

# Initialize the matcher with your OpenAI API key
matcher = SCEDMatcher(api_key="your-openai-api-key")
# Or set OPENAI_API_KEY environment variable and use:
# matcher = SCEDMatcher()

# Get SCED code for a single course
sced_code = matcher.get_sced_match("Advanced Algebra")
print(sced_code)  # Returns SCED code

# Get detailed information
code, name, description = matcher.get_sced_match("Advanced Algebra", return_details=True)
print(f"Code: {code}, Name: {name}, Description: {description}")
```

### Processing DataFrames

```python
import pandas as pd

# Create or load your DataFrame
df = pd.DataFrame({
    'Course_Name': ['Advanced Algebra', 'Biology I', 'World History'],
    'Course_Description': ['Advanced algebra concepts', 'Introduction to biology', 'World history survey']
})

# Process the DataFrame
result_df = matcher.process_dataframe(df)
print(result_df)  # DataFrame with added SCED_Code column
```

### Processing CSV Files

```python
# Process a CSV file directly
result_df = matcher.process_csv_file('input.csv', 'output_with_sced.csv')
```

## Requirements

- Python 3.8+
- OpenAI API key
- Required packages: `openai`, `pandas`, `python-dotenv`

## Environment Setup

Create a `.env` file in your project root:

```
OPENAI_API_KEY=your-openai-api-key-here
```

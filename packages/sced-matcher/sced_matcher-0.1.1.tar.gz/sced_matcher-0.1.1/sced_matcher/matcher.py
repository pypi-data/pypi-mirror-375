from openai import OpenAI
import time
import pandas as pd
import os
import re
from dotenv import load_dotenv

load_dotenv()


class SCEDMatcher:
    def __init__(self, api_key=None):
        """Initialize SCED Matcher with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        self.client = OpenAI(api_key=self.api_key)
    
    def get_sced_match(self, course_input, return_details=False):
        """
        Get SCED code match for a single course.
        
        Args:
            course_input (str): Course name or description
            return_details (bool): If True, returns (code, name, description) tuple
            
        Returns:
            str or tuple: SCED code or (code, name, description) if return_details=True
        """
        thread = self.client.beta.threads.create()

        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=course_input.strip().replace('/', '') + '. Search carefully. If there is no exact match, find the closest match. Always provide a matching SCED code, even if unsure.'
        )

        my_updated_assistant = self.client.beta.assistants.update(
          "asst_PbpkEKciHCmAJS4Yf4uKAUV5",
            tool_resources={
            "code_interpreter": {
              "file_ids": ["file-kino7A5APplnta6Alp1x8xx7"]
            }
          }, model="gpt-4o"
        )

        run = self.client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id='asst_PbpkEKciHCmAJS4Yf4uKAUV5',
        )

        while True:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=thread.id, 
                                                               run_id=run.id)
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                print("Run failed:", run_status.last_error)
                return None
            time.sleep(2)
            
        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        answer = messages.data[0].content[0].text.value.split("|")
        sced_code_clean = re.sub('[^0-9]','', answer[0])
        
        if len(str(sced_code_clean)) < 5:
            sced_code = '0' + str(sced_code_clean)
        else:
            sced_code = sced_code_clean
        
        if return_details:
            course_name = answer[1].strip() if len(answer) > 1 else "N/A"
            course_description = answer[2].strip() if len(answer) > 2 else "N/A"
            return sced_code, course_name, course_description
        
        return sced_code

    def process_dataframe(self, df, course_name_col=None, course_desc_col=None):
        """
        Process a pandas DataFrame to add SCED codes.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            course_name_col (str): Column name for course names (default: first column)
            course_desc_col (str): Column name for course descriptions (default: second column if available)
            
        Returns:
            pd.DataFrame: DataFrame with added SCED_Code column
        """
        df = df.copy()
        
        if df.shape[1] < 1:
            raise ValueError("DataFrame must have at least 1 column.")
        
        # Handle single column case
        if df.shape[1] == 1:
            course_name_col = course_name_col or df.columns[0]
            course_desc_col = None
            print(f"Processing {len(df)} courses with single column (name/description only)...")
        else:
            course_name_col = course_name_col or df.columns[0]
            course_desc_col = course_desc_col or df.columns[1]
            print(f"Processing {len(df)} courses with name and description columns...")
        
        sced_codes = []
        
        for index, row in df.iterrows():
            course_name = str(row[course_name_col])
            
            if course_desc_col and course_desc_col in df.columns:
                course_desc = str(row[course_desc_col])
                course_input = f"{course_name}: {course_desc}"
                display_name = course_name
            else:
                # Single column - use the content as both name and description
                course_input = course_name
                display_name = course_name[:50] + "..." if len(course_name) > 50 else course_name
            
            print(f"Processing course {index + 1}/{len(df)}: {display_name}")
            
            sced_code = self.get_sced_match(course_input)
            sced_codes.append(sced_code if sced_code else "N/A")
        
        df['SCED_Code'] = sced_codes
        return df

    def process_csv_file(self, input_file_path, output_file_path=None):
        """
        Process a CSV file to add SCED codes.
        
        Args:
            input_file_path (str): Path to input CSV file
            output_file_path (str): Path for output CSV file (optional)
            
        Returns:
            pd.DataFrame: Processed DataFrame with SCED codes
        """
        if not os.path.exists(input_file_path):
            raise FileNotFoundError(f"Input file '{input_file_path}' not found.")
        
        df = pd.read_csv(input_file_path)
        result_df = self.process_dataframe(df)
        
        if output_file_path:
            result_df.to_csv(output_file_path, index=False)
            print(f"Results saved to: {output_file_path}")
        
        return result_df
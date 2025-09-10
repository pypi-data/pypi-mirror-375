from google import genai
from google.genai import types
import httpx
import time
import pandas as pd
import os
import re
from dotenv import load_dotenv
import requests
from io import BytesIO

load_dotenv()
gemini_key = os.getenv("GEMINI_API_KEY")


def get_sced_match(course_input, client, return_details=False):
        doc_url="https://nbviewer.org/github/LeosonH/sced-matcher-cli/blob/main/data/sced_v12.pdf"
        doc_data=httpx.get(doc_url).content
        prompt = f"""Please find the most appropriate 5-digit SCED code for this course: "{course_input.strip().replace('/', '')}"
            Format your answer with only the SCED Code, SCED Course Name, and SCED Course Description, separated by a '|'."""
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Part.from_bytes(
                    data=doc_data,
                    mime_type='application/pdf',
                    ),
                    prompt])

            result = response.text.split('|')
            sced_code = result[0].strip()
            sced_course_name = result[1].strip()
            sced_course_description = result[2].strip()
            
            if return_details:
                return sced_code, sced_course_name, sced_course_description
            
            return sced_code
        
    except Exception as e:
        print(f"Error getting SCED match: {str(e)}")
        return None

def process_csv_file(input_file_path, output_file_path):
    if not os.path.exists(input_file_path):
        print(f"Error: Input file '{input_file_path}' not found.")
        return
    
    try:
        df = pd.read_csv(input_file_path)
        
        if df.shape[1] < 2:
            print("Error: CSV file must have at least 2 columns (course name and description).")
            return
        
        course_name_col = df.columns[0]
        course_desc_col = df.columns[1]
        
        print(f"Processing {len(df)} courses...")
        
        client = genai.Client(api_key=gemini_key)
        sced_codes = []
        
        for index, row in df.iterrows():
            course_name = str(row[course_name_col])
            course_desc = str(row[course_desc_col])
            course_input = f"{course_name}: {course_desc}"
            
            print(f"Processing course {index + 1}/{len(df)}: {course_name}")
            
            sced_code = get_sced_match(course_input, client)
            sced_codes.append(sced_code if sced_code else "N/A")
        
        df['SCED_Code'] = sced_codes
        df.to_csv(output_file_path, index=False)
        print(f"Results saved to: {output_file_path}")
        
    except Exception as e:
        print(f"Error processing CSV file: {str(e)}")
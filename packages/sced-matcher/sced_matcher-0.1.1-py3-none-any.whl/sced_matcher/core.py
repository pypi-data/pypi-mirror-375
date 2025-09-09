from openai import OpenAI
import time
import pandas as pd
import os
import re
from dotenv import load_dotenv

load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")


def get_sced_match(course_input, client, return_details=False):
    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=course_input.strip().replace('/', '') + '. If there is no exact match, find the closest match. Always provide a match, even if unsure.'
    )

    my_updated_assistant = client.beta.assistants.update(
      "asst_PbpkEKciHCmAJS4Yf4uKAUV5",
        tool_resources={
        "code_interpreter": {
          "file_ids": ["file-kino7A5APplnta6Alp1x8xx7"]
        }
      }, model="gpt-4o"
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id='asst_PbpkEKciHCmAJS4Yf4uKAUV5',
    )

    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id, 
                                                       run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            print("Run failed:", run_status.last_error)
            return None
        time.sleep(2)
        
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    answer = messages.data[0].content[0].text.value.split("|")
    sced_code_clean = re.sub('[^0-9]','', answer[0])
    
    if int(sced_code_clean) < 10000:
        sced_code = '0' + str(sced_code_clean)
    else:
        sced_code = sced_code_clean
    
    if return_details:
        course_name = answer[1].strip() if len(answer) > 1 else "N/A"
        course_description = answer[2].strip() if len(answer) > 2 else "N/A"
        return sced_code, course_name, course_description
    
    return sced_code

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
        
        client = OpenAI(api_key=openai_key)
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
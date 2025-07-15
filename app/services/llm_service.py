import os
# import time
import pandas as pd
from dotenv import load_dotenv
import logging
# import traceback
import pdfplumber

from app.schema.workout_schema import WorkoutProgram

from google import genai

load_dotenv()
class LLMService:
    def __init__(self):
        self.llm = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = os.getenv("GEMINI_MODEL")
    
    def generate_week_prompt(self, week_number: int) -> str:
        """Generate a prompt to extract the workout program for a specific week in JSON format."""
        return f"""
                Analyze the workout program and extract the exercises for Week {week_number}. Return the output as a JSON object with no additional text or comments. Ensure the JSON is valid. If there are any quotes within any field, replace them with asterisks. Do not include any escaped characters in the output.
                For each exercise, include the following attributes:
                - Exercise Name: If the exercise name has any superset related information, like A1, B2 etc, do not include it in the exercise name, but mention it in the notes.
                - Sets: A list of objects where each object includes:
                - Set Number: Number representing the sequence of the set (e.g., 1, 2, 3, etc.)
                - Reps: Object with 'isRange', 'value', 'min', and 'max' (use empty values if not mentioned). If the reps are non-numeric (e.g., MR, MR10, or hyphen separated like 12-15), convert them to numeric values (e.g., MR = 10, MR10 = 10, 12-15 = min: 12 max:15) and mention the original format in the notes. Rep ranges may have been converted to dates by excel (for eg, 3-4 may be interpretted by excel as 04/03/YYYY). Ensure you correct this to a range, (dd/mm/yyyy maps to a range of min(dd,mm), max(dd,mm)).
                - Weight: Object with 'value' and 'unit' (use empty values if not mentioned; if a range is provided, use the lower limit as 'value' and note the range in 'Notes')
                - Rest Time: Object with 'value' and 'unit' (use empty values if not mentioned)
                - Notes: Include warmups or additional notes; if a weight range exists, mention it here. If the program specifies the total number of sets in text (e.g., *3 sets*), create individual entries for each set. If reps are converted from non-numeric values, mention the original format here. Leave blank if not mentioned. Do not count the weeks by the number of days, follow the number of weeks in the program. Do not ignore any workouts, if a workout is repeated, include it in the output.
                Ensure that:
                1. If sets are written in text (e.g., *3 sets*), interpret this and generate separate numbered entries for each set with identical details unless specified otherwise.
                2. If sets are explicitly listed with varying details, preserve these details in the output.
                3. Warmup sets may be written in text (e.g., *3 sets*), ensure they are included in the notes.                   
                """.strip()

    def make_llm_call(self, prompt: str, workout_file_path: str, is_duration_call: bool = False) -> str:
        """Make a call to the LLM."""
        try:
            # Read file and convert to string representation
            if workout_file_path.endswith(('.xlsx', '.xls')):
                # Read all sheets from the Excel file
                excel_data = pd.read_excel(workout_file_path, sheet_name=None)
                workout_program = ""
                for sheet_name, df in excel_data.items():
                    workout_program += f"Sheet: {sheet_name}\n"
                    workout_program += df.to_markdown(index=False) + "\n\n"
            elif workout_file_path.endswith('.pdf'):
                # Use pdfplumber to extract tables and text
                workout_program = ""
                with pdfplumber.open(workout_file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        workout_program += f"--- Page {i+1} ---\n\n"
                        # Extract text
                        text = page.extract_text()
                        if text:
                            workout_program += text + "\n\n"
                        
                        # Extract tables and convert to markdown
                        tables = page.extract_tables()
                        for table in tables:
                            df = pd.DataFrame(table[1:], columns=table[0])
                            workout_program += df.to_markdown(index=False) + "\n\n"
            else:
                # For text files
                with open(workout_file_path, "r") as file:
                    workout_program = file.read()
                    
            contents = [prompt, workout_program]
            model = self.model
            config = {
                "response_mime_type": "application/json",
                "response_schema": WorkoutProgram if not is_duration_call else int,
            }

            response = self.llm.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            
            if response.candidates and response.candidates[0].finish_reason.name == "MAX_TOKENS":
                _ = response.usage_metadata.total_token_count
            return response.text
        except Exception as e:
            logging.error(f"Error making LLM call: {e}")
            return None
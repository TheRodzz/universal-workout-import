import logging
import traceback
import os
import pandas as pd
from typing import Any
from app.services.lyfta_api_service import APIClient
from app.services.exercise_matcher import ExerciseMatcher
from app.services.llm_service import LLMService
from app.services.workout_program_mapper import WorkoutProgramMapper
from app.constants import EXERCISE_DB_PATH
from concurrent.futures import ThreadPoolExecutor
import json
class WorkoutProgramParser:
    def __init__(self, input_file_path, tmp_dir_path):
        self.excel_file_path = input_file_path
        self.dir_path=tmp_dir_path
        self.csv_file_path = os.path.join(tmp_dir_path,'output.csv')
        self.llm_service = LLMService()

    def excel_to_single_minimal_csv(self) -> None:
        """Convert all sheets from an Excel file into a single CSV file."""
        try:
            # Validate input file path
            if not self.excel_file_path or not isinstance(self.excel_file_path, str):
                raise ValueError("Invalid Excel file path")

            # Read all sheets from the Excel file
            all_sheets = pd.read_excel(self.excel_file_path, sheet_name=None)

            # List to hold all DataFrames
            all_dataframes = []

            # Iterate over each sheet
            for sheet_name, df in all_sheets.items():
                # Strip whitespace from headers and data
                df.columns = [str(col).strip() for col in df.columns]
                df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

                # Drop any completely empty rows or columns
                df.dropna(how='all', inplace=True)
                df.dropna(axis=1, how='all', inplace=True)

                # Add a column to identify the sheet name
                df['SheetName'] = sheet_name

                # Append the DataFrame to the list
                all_dataframes.append(df)

            # Concatenate all DataFrames into a single DataFrame
            combined_df = pd.concat(all_dataframes, ignore_index=True)

            # Save the combined DataFrame to a single CSV file
            combined_df.to_csv(self.csv_file_path, index=False, sep=',', encoding='utf-8', compression='infer')

            logging.info(f"All sheets combined and saved as {self.csv_file_path}")
        except FileNotFoundError as e:
            logging.error(f"Excel file not found: {e}")
            logging.error(traceback.format_exc())
            raise
        except pd.errors.EmptyDataError as e:
            logging.error(f"Excel file is empty: {e}")
            logging.error(traceback.format_exc())
            raise
        except Exception as e:
            logging.error(f"Error converting Excel to CSV: {e}")
            logging.error(traceback.format_exc())
            raise

    def process_week(self, week_number: int, cookie: str, exercise_matcher: Any) -> None:
        """Process a single week and save the output as a JSON file."""
        try:
            #     api_client.create_workout_in_co
            output_file_path = os.path.join(self.dir_path, f'result-jn-{week_number}.json')

            # week_prompt = self.llm_service.generate_week_prompt(week_number)
            # response = self.llm_service.send_file_to_openai(self.csv_file_path, week_prompt)
            # with open(output_file_path, "w") as json_file:
            #     json_file.write(response)
            workout_processor = WorkoutProgramMapper(exercise_matcher)
            structured_workouts = workout_processor.read_workout_json(output_file_path)
        
            api_client = APIClient()
            # Create a collection for the week
            collection_name = f"Week {week_number}"
            collection_id, user_id = api_client.create_collection(collection_name, cookie)

            # Send workouts to the API, associating them with the created collection

            formatted_workouts = self.format_workout_data(structured_workouts)
            
            # Create the final payload
            with open('out', 'w', encoding='utf-8') as f:
                json.dump(structured_workouts, f, ensure_ascii=False, indent=2)

            for workout in formatted_workouts:
                api_client.create_workout_in_collection(workout, collection_id, user_id, collection_name, cookie)

            logging.info(f'Processed Week {week_number}')
        except Exception as e:
            logging.error(f"Error processing week {week_number}: {e}")
            logging.error(traceback.format_exc())
            raise

    def parallel_process(self, num_weeks: int, cookie: str) -> None:
        """Process multiple weeks in parallel using ThreadPoolExecutor."""
        exercise_matcher = ExerciseMatcher(EXERCISE_DB_PATH)
        try:
            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(self.process_week, i, cookie, exercise_matcher) 
                    for i in range(1, num_weeks + 1)
                ]
                for future in futures:
                    future.result()  # Wait for all tasks to complete
        except Exception as e:
            logging.error(f"Error in parallel processing: {e}")
            logging.error(traceback.format_exc())
            raise

    @staticmethod
    def format_workout_data(input_data):
        formatted_workouts = []
        
        for workout in input_data:
            workout_data = workout['workout']
            formatted_exercises = []
            
            for exercise in workout_data['exercises']:
                formatted_sets = []
                
                for set_item in exercise['sets']:
                    formatted_sets.append({
                        "set_type_id": 0,
                        "reps": set_item['reps'],
                        "weight": set_item['weight'],
                        "rir": "",
                        "duration": "",
                        "distance": ""
                    })
                
                formatted_exercises.append({
                    "exercise_superset_id": 0,
                    "exercise_id": exercise['exercise_id'],  # Replace with actual exercise ID if available
                    "exercise_note": exercise['exercise_note'],
                    "exercise_rest_time": 0,
                    "workout_id": 0,
                    "date_updated": "2025-01-24 13:47:20",  # Update as needed
                    "exercise_type": exercise['exercise_type'],  # Update as needed
                    "date_created": "2025-01-24 13:47:20",  # Update as needed
                    "exercise_image": exercise['exercise_image'],  # Add image URL if available
                    "exercise_name": exercise['exercise_name'],
                    "sets": formatted_sets
                })
            
            formatted_workouts.append({
                "id": workout_data['id'],  # Replace with actual workout ID if available
                "title": workout_data['title'],
                "description": workout_data['description'],
                "note": workout_data['note'],
                "color": workout_data['color'],
                "picture": workout_data['picture'],
                "user_id": workout_data['user_id'],  # Replace with actual user ID
                "create_date": workout_data['create_date'],  # Update as needed
                "update_date": workout_data['update_date'],  # Update as needed
                "exercises": formatted_exercises
            })
        
        return formatted_workouts

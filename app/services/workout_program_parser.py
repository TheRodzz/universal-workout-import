import logging
import traceback
import os
from typing import Any
from app.services.lyfta_api_service import APIClient
from app.services.exercise_matcher import ExerciseMatcher
from app.services.llm_service import LLMService
from app.services.workout_program_mapper import WorkoutProgramMapper
from app.constants import EXERCISE_DB_PATH
from concurrent.futures import ThreadPoolExecutor
class WorkoutProgramParser:
    def __init__(self, input_file_path, tmp_dir_path):
        self.excel_file_path = input_file_path
        self.dir_path=tmp_dir_path
        self.csv_file_path = os.path.join(tmp_dir_path,'output.csv')
        self.llm_service = LLMService()

    def process_week(self, week_number: int, cookie: str, exercise_matcher: Any) -> None:
        """Process a single week and save the output as a JSON file."""
        try:
            output_file_path = os.path.join(self.dir_path, f'result-{week_number}.json')

            # week_prompt = self.llm_service.generate_week_prompt(week_number)
            # response = self.llm_service.send_file_to_openai(self.csv_file_path, week_prompt)
            # with open(output_file_path, "w") as json_file:
            #     json_file.write(response)
            workout_processor = WorkoutProgramMapper(exercise_matcher)
            structured_workouts = workout_processor.read_workout_json(output_file_path)
        
            api_client = APIClient()
            # Create a collection for the week
            collection_name = f"Week {week_number}"
            collection_id, user_id = api_client.create_collection(collection_name, week_number, cookie)

            # Send workouts to the API, associating them with the created collection

            formatted_workouts = self.format_workout_data(structured_workouts)
            
            # Create the final payload

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
                    "excercise_name": exercise['excercise_name'],
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

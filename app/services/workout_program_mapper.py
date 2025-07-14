from typing import List, Dict, Any
from datetime import datetime
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.exercise_matcher import ExerciseMatcher

class WorkoutProgramMapper:
    def __init__(self, exercise_matcher: "ExerciseMatcher"):
        self.exercise_matcher = exercise_matcher

    def process_day(self, week: str, day_name: str, exercises: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            # logging.critical(f" exercises : {exercises}")
            matched_exercises = self.exercise_matcher.match_exercises(exercises)
            time_now = datetime.now().isoformat()
            return {
                "workout": {
                    "id": None,
                    "title": f'{week}-{day_name}',
                    "description": "",
                    "note": "",
                    "color": "#1A118F",
                    "picture": "",
                    "user_id": None,
                    "create_date": time_now,
                    "update_date": time_now,
                    "exercises": matched_exercises
                }
            }
        except Exception as e:
            logging.error(
                f"Error processing day '{week}-{day_name}' with exercises: {exercises}. Exception: {str(e)}",
                exc_info=True
            )
            raise

    def read_workout_json(self, file_path: str) -> List[Dict[str, Any]]:
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)

            structured_workouts = []
            with ThreadPoolExecutor() as executor:
                futures = []
                for week in data["weeks"]:
                    for day in week["days"]:
                        
                        logging.critical(f"week: {week['week']}")
                        # for day_name, exercises in day.items():
                        if day["exercises"] == "":
                            continue
                        futures.append(
                            executor.submit(self.process_day, week['week'], day['day'], day["exercises"])
                        )

                for future in as_completed(futures):
                    try:
                        structured_workouts.append(future.result())
                    except Exception as e:
                        logging.error(f"Error in processing a workout day from the thread pool: {e}", exc_info=True)
                        raise
            return structured_workouts
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}", exc_info=True)
            raise
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON format in file: {file_path}", exc_info=True)
            raise
        except Exception as e:
            logging.error(f"Unexpected error while reading workout JSON: {e}", exc_info=True)
            raise


import os
import json
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss
from uuid import uuid4
from fuzzywuzzy import process
import re
from app.constants import exercise_dict

class ExerciseMatcher:
    _faiss_index = None  # Class-level variable to cache the FAISS index

    def __init__(self, exercise_db_path: str):
        """
        Initialize the ExerciseMatcher with the path to the exercise database.

        :param exercise_db_path: Path to the JSON file containing exercise data.
        """
        logging.info(f"Initializing ExerciseMatcher with database path: {exercise_db_path}")
        if not os.path.exists(exercise_db_path):
            logging.error(f"Exercise database file not found at path: {exercise_db_path}")
            raise FileNotFoundError(f"Exercise database file not found at path: {exercise_db_path}")
        
        self.exercises = self._load_json_file(exercise_db_path)
        self._validate_exercises(self.exercises)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        if ExerciseMatcher._faiss_index is None:
            ExerciseMatcher._faiss_index = self._build_faiss_index()
        self.index = ExerciseMatcher._faiss_index
        
    def _load_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Load and return the exercise data from a JSON file.

        :param file_path: Path to the JSON file.
        :return: List of exercise dictionaries.
        """
        logging.info(f"Loading JSON file from path: {file_path}")
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON file: {e}")
            raise ValueError(f"Invalid JSON file format: {file_path}")
        except Exception as e:
            logging.error(f"Unexpected error loading JSON file: {e}")
            raise
        
    def _validate_exercises(self, exercises: List[Dict[str, Any]]):
        """
        Validate the exercise data to ensure it has the required fields.

        :param exercises: List of exercise dictionaries.
        """
        logging.info("Validating exercise data...")
        required_keys = {"id", "name"}
        for exercise in exercises:
            if not required_keys.issubset(exercise.keys()):
                logging.error(f"Exercise missing required keys: {exercise}")
                raise ValueError(f"Exercise missing required keys: {exercise}")
        logging.info("Exercise data validated successfully.")
            
    def _preprocess(self, text: str) -> str:
        """
        Preprocess the input text by converting it to lowercase and removing special characters.

        :param text: Input text to preprocess.
        :return: Preprocessed text.
        """
        text = text.lower()
        text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
        return text.strip()

    def _build_faiss_index(self) -> faiss.IndexFlatIP:
        """
        Build and return a FAISS index for the exercise names.

        :return: FAISS index.
        """
        logging.info("Building FAISS index...")
        try:
            exercise_names = [self._preprocess(exercise['name']) for exercise in self.exercises]
            embeddings = self.model.encode(exercise_names)
            index = faiss.IndexFlatIP(embeddings.shape[1])
            index.add(embeddings)
            logging.info("FAISS index built successfully.")
            return index
        except Exception as e:
            logging.error(f"Error building FAISS index: {e}")
            raise

    def find_most_similar(self, input_name: str, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Find the most similar exercises to the input name using semantic search.

        :param input_name: Name of the exercise to match.
        :param top_n: Number of top matches to return.
        :return: List of dictionaries containing matched exercises and their similarity scores.
        """
        try:
            input_embedding = self.model.encode([self._preprocess(input_name)])
            input_embedding = input_embedding.astype('float32')
            distances, indices = self.index.search(input_embedding, top_n)
            results = []
            for i in range(top_n):
                result = {
                    "name": self.exercises[indices[0][i]]['name'],
                    "similarity_score": float(distances[0][i]),
                    "details": self.exercises[indices[0][i]]
                }
                results.append(result)
            return results
        except Exception as e:
            logging.error(f"Error finding most similar exercises for exercise: {input_name} {e}")
            raise

    def match_exercises(self, workout_exercises: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Match workout exercises to the exercises in the database.

        :param workout_exercises: List of workout exercises to match.
        :return: List of matched exercises with additional details.
        """
        logging.info("Matching workout exercises...")
        matched_exercises = []
        for exercise in workout_exercises:
            # logging.critical(f"exercise: {exercise['Exercise Name']}")
            try:
                primary_name = self._normalize(self._extract_primary_name(exercise["Exercise Name"]))
                
                # Step 1: Fuzzy match with exercise_dict for un-common names
                closest_value, matched_key, fuzzy_match_score = self.find_closest_match(primary_name, exercise_dict)
                
                # Step 2: Use semantic search to find the most similar exercises
                if fuzzy_match_score >= 95:
                    matches = self.find_most_similar(closest_value, top_n=1)
                else:
                    matches = self.find_most_similar(primary_name, top_n=1)
                direct_match = matches[0]['details']
                if direct_match:
                    exercise_note = f"(Orignal Name: {exercise['Exercise Name']}). Notes: {exercise['Notes']}" if exercise.get("Notes") else f"Orignal Name: {exercise['Exercise Name']}"
                    matched_exercises.append({
                        "exercise_id": direct_match["id"],
                        "exercise_name": direct_match["name"],
                        "exercise_image": direct_match.get("image_name", ""),
                        "exercise_type": direct_match["exercise_type"],
                        "exercise_uuid": str(uuid4()),
                        "exercise_note": exercise_note,
                        "sets": [
                            {
                                "weight": str(set_info["Weight"]["value"]) if set_info["Weight"]["value"] else "",
                                "reps": f"{set_info['Reps']['min']}" if set_info['Reps'].get("isRange") else str(set_info['Reps']['value'])
                            }
                            for set_info in exercise.get("Sets", [])
                        ]
                    })
                # logging.critical(f"Matched Exercise: {matched_exercises[:3]}")
            except Exception as e:
                logging.error(f"Error matching exercise: {e}")
                continue
        logging.info(f"Matched {len(matched_exercises)} exercises.")
        return matched_exercises

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalize the input text by converting it to lowercase and stripping whitespace.

        :param text: Input text to normalize.
        :return: Normalized text.
        """
        return text.lower().strip()

    @staticmethod
    def _extract_primary_name(name: str) -> str:
        """
        Extract the primary name by removing text in brackets or parentheses.

        :param name: Input name to clean.
        :return: Cleaned name.
        """
        return re.sub(r"\[.*?\]|\(.*?\)", "", name, flags=re.IGNORECASE).strip()

    @staticmethod
    def find_closest_match(input_string, dictionary):
        """
        Find the closest match for the input string in the dictionary using fuzzy matching.

        :param input_string: Input string to match.
        :param dictionary: Dictionary to search for matches.
        :return: Closest match, matched key, and fuzzy match score.
        """
        match, score = process.extractOne(input_string, dictionary.keys())
        return dictionary[match], match, score

import logging
from typing import Dict, Any
import requests
from ratelimit import limits, sleep_and_retry
from datetime import datetime


class APIClient:
    BASE_URL = "https://my.lyfta.app/api"
    MAX_CALLS = 10
    PERIOD = 1  # in seconds

    def __init__(self):
        self.logging = logging.getLogger(__name__)

    @sleep_and_retry
    @limits(calls=MAX_CALLS, period=PERIOD)
    def send_request(self, endpoint: str, method: str, data: Dict[str, Any], cookie: str) -> requests.Response:
        try:
            url = f"{self.BASE_URL}/{endpoint}"
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "Cookie": cookie,
                "Host": "my.lyfta.app",
                "Origin": "https://my.lyfta.app",
                "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0",
            }

            # Choose the HTTP method
            if method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method.upper() == "GET":
                response = requests.get(url, headers=headers)
            else:
                raise ValueError("Unsupported HTTP method")

            # Raise HTTP errors, if any
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            self.logging.error(
                f"HTTP error while accessing {url}: {e}, Status Code: {e.response.status_code if e.response else 'N/A'}, Response: {e.response.text if e.response else 'N/A'}",
                exc_info=True
            )
            raise
        except requests.RequestException as e:
            self.logging.error(f"Request failed for {url}: {e}", exc_info=True)
            raise
        except Exception as e:
            self.logging.error(f"Unexpected error in send_request: {e}", exc_info=True)
            raise

    def create_collection(self, collection_name: str, cookie: str) -> str:
        """Create a new collection and return its ID."""
        endpoint = "saveCollection"
        current_time = datetime.now().isoformat()
        data = {
            "collection": {
                "title": collection_name,
                "description": "",
                "image": "",
                "date_created": current_time,
                "date_updated": current_time,
            }
        }
        try:
            response = self.send_request(endpoint, "POST", data, cookie)
            collection_id = response.json().get("data", {}).get("id")  # Extract collection ID from response
            user_id = response.json().get("data", {}).get("user_id")  # Extract user ID from response
            if not collection_id:
                raise ValueError("Failed to retrieve collection ID from API response")

            self.logging.info(f"Created collection '{collection_name}' with ID {collection_id}")
            return collection_id, user_id
        except Exception as e:
            self.logging.error(f"Error creating collection '{collection_name}': {e}", exc_info=True)
            raise

    def create_workout_in_collection(self, workout: Dict[str, Any], collection_id: str, user_id: str, collection_name: str, cookie: str) -> str:
        """Create a new workout inside a collection and return its ID."""
        endpoint = "workout/SaveTemplate"
        payload1 = {
            "workout": {
                "id": None,
                "collectionId": collection_id,
                "workoutType": None,
                "userId": None,
                "workoutName": None,
                "description": "",
                "exertion": 0,
                "privacy": None,
                "isCompleted": False,
                "workoutDuration": None,
                "createDate": None,
                "updateDate": None,
                "isTemplate": "0",
                "exercises": [],
                "isExpanded": False,
                "workoutPerformDate": None,
                "createWorkoutAndSaveTemplate": None,
                "user": None,
                "colorCode": "",
                "workoutNote": "",
                "workoutPicture": "",
                "lastPerformedDate": "",
                "downloadcount": "",
                "viewcount": "",
                "finishScreenStats": None,
                "totalVolume": 0,
                "collectionName": collection_name,
                "create_date": datetime.now().isoformat(),
                "update_date": datetime.now().isoformat(),
                "title": workout["title"]
            }
        }
        try:
            response = self.send_request(endpoint, "POST", payload1, cookie)
            workout_id = response.json().get("data", {}).get("id")  # Extract ID from response
            if not workout_id:
                raise ValueError("Failed to retrieve workout ID from API response")

            self.logging.info(f"Created workout '{workout['title']}' with ID {workout_id}")
            workout["id"] = workout_id
            workout["user_id"] = user_id
            payload2 = {
                "workout": workout
            }

            self.send_request(endpoint, "POST", payload2, cookie)
            return workout_id
        except Exception as e:
            self.logging.error(f"Error creating workout '{workout['title']}' in collection '{collection_name}': {e}", exc_info=True)
            raise

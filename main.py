from app.services.llm_service import LLMService
from app.constants import WORKOUT_DURATION_PROMPT
import logging
import concurrent.futures
import time
import argparse
from app.services.workout_program_parser import WorkoutProgramParser

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

llm_service = LLMService()
parser = argparse.ArgumentParser()
parser.add_argument("--file-path", required=True, help="Path to input workout file")
parser.add_argument("--lyfta-cookie", required=True, help="Cookie for your lyfta account")

args = parser.parse_args()
FILE_NAME = args.file_path


logging.info(f"File name: {FILE_NAME}")
# duration=12
duration = llm_service.make_llm_call(WORKOUT_DURATION_PROMPT, FILE_NAME, is_duration_call=True)
logging.info(f"Workout duration: {duration} weeks")

with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    start_times = {}
    future_to_week = {}
    for i in range(1, abs(int(duration)) + 1):
        prompt = llm_service.generate_week_prompt(i)
        future = executor.submit(llm_service.make_llm_call, prompt, FILE_NAME)
        start_times[future] = time.time()
        future_to_week[future] = i

    for future in concurrent.futures.as_completed(future_to_week):
        i = future_to_week[future]
        start_time = start_times[future]
        try:
            result = future.result()
            end_time = time.time()
            time_taken = end_time - start_time
            logging.info(f"Week {i} processed in {time_taken:.2f} seconds.")

            with open(f"result-{i}.json", "w") as f:
                f.write(result)
        except Exception as exc:
            logging.error(f'Week {i} generated an exception: {exc}') 
            
workout_parser = WorkoutProgramParser(FILE_NAME, ".")
workout_parser.parallel_process(abs(int(duration)), args.lyfta_cookie)
from app.services.llm_service import LLMService
from app.constants import WORKOUT_DURATION_PROMPT
import logging
import concurrent.futures
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

llm_service = LLMService()

FILE_NAME = "/home/vidhu/Documents/workout-import-refactor/jn.xlsx"

logging.info(f"File name: {FILE_NAME}")
duration = llm_service.make_llm_call(WORKOUT_DURATION_PROMPT, FILE_NAME, is_duration_call=True)
logging.info(f"Workout duration: {duration} weeks")
# TODO rep ranges like 3-4 are being interpreted as 04/03/2022 by excel, need to handle this
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    start_times = {}
    future_to_week = {}
    for i in range(1, int(duration) + 1):
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

            with open(f"result-jn-{i}.json", "w") as f:
                f.write(result)
        except Exception as exc:
            logging.error(f'Week {i} generated an exception: {exc}') 
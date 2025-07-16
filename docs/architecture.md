# Architecture

## How It Works

1.  **Input:** The script takes a workout program file and your Lyfta authentication cookie as input.
2.  **Determine Workout Duration:** It first calls an LLM to determine the total duration of the workout program in weeks.
3.  **Parse and Structure:** For each week, it uses the LLM to parse the workout details and structure them into a JSON format.
4.  **Map Data:** The structured JSON data is then mapped to a format that can be used by the Lyfta API.
5.  **Upload to Lyfta:** The script then communicates with the Lyfta API to:
    -   Create a new "collection" for each week of the program.
    -   Create the individual workouts and add them to the corresponding weekly collection.

## Project Structure

```
.
├── app/
│   ├── services/
│   │   ├── llm_service.py              # Handles interaction with the LLM.
│   │   ├── lyfta_api_service.py        # Manages communication with the Lyfta API.
│   │   ├── workout_program_parser.py   # Orchestrates the parsing and importing process.
│   │   ├── exercise_matcher.py         # Matches exercises.
│   │   └── workout_program_mapper.py   # Maps the LLM output to a structured format.
│   ├── schema/
│   │   └── workout_schema.py           # Pydantic models for workout data.
│   └── constants.py                    # Project constants.
├── main.py                             # The main entry point of the application.
├── Dockerfile                          # Docker configuration for containerization.
├── exercise_web.json                   # Lyfta specific exercises
└── requirements.txt                    # Python dependencies.
``` 
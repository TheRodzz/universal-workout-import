# Universal Workout Import

Universal Workout Import is a Python-based tool for importing, parsing, and mapping workout programs from various formats (Excel, PDF, JSON) into a structured format suitable for integration with the Lyfta app API. It leverages LLMs for intelligent parsing and exercise matching.

## Features
- **LLM-powered Parsing:** Uses Google Gemini (via `google-genai`) to extract and structure workout data from Excel/PDF files.
- **Exercise Matching:** Matches exercises using semantic search (Sentence Transformers + FAISS) and fuzzy matching.
- **Schema Validation:** Pydantic models for robust data validation and transformation.
- **Lyfta API Integration:** Automates creation of workout collections and workouts in Lyfta via its API.
- **Parallel Processing:** Efficiently processes multiple weeks/days using thread pools.

## Directory Structure
```
app/
  constants.py           # Exercise name mappings and config
  schema/
    workout_schema.py    # Pydantic models for workout data
  services/
    exercise_matcher.py  # Semantic/fuzzy exercise matching
    llm_service.py       # LLM prompt and response handling
    lyfta_api_service.py # Lyfta API client
    workout_program_mapper.py # Maps parsed workouts to Lyfta format
    workout_program_parser.py # Orchestrates parsing and API upload
main.py                  # Entry point for running the workflow
requirements.txt         # Python dependencies
```

## Setup
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Environment variables:**
   - Create a `.env` file with:
     - `GEMINI_API_KEY` (Google Gemini API key)
     - `GEMINI_MODEL` (Model name, e.g. `gemini-pro`)
     - `LYFTA_COOKIE` (Lyfta session cookie for API access)
3. **Prepare input files:**
   - Place your workout Excel/PDF file in the project root.
   - Ensure `exercises_web.json` contains your exercise database.

## Usage
Run the main workflow:
```bash
python main.py
```
- The script will parse the input file, extract workout data, match exercises, and upload to Lyfta.
- Output JSON files for each week will be generated (e.g., `result-jn-1.json`).

## Customization
- **Exercise Mapping:** Edit `app/constants.py` to adjust exercise name normalization.
- **Schema:** Modify `app/schema/workout_schema.py` for custom workout data structures.
- **API Integration:** Update `app/services/lyfta_api_service.py` for different endpoints or payloads.

## Troubleshooting
- Ensure all required environment variables are set.
- Check `requirements.txt` for missing packages.
- Review log output for errors (logging level is set to CRITICAL by default).

## Docker Usage

You can run Universal Workout Import in a Docker container using the provided `Dockerfile`.

### Build the Docker image
```bash
docker build -t universal-workout-import .
```

### Prepare environment variables
Create a `.env` file in the project root with the following variables:
```
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-pro
LYFTA_COOKIE=your_lyfta_cookie
```

### Run the container
Mount your input files and `.env` file, and pass required arguments:
```bash
docker run --rm \
  -v $(pwd):/app \
  --env-file .env \
  universal-workout-import \
  --excel-file jn.xlsx \
  --lyfta-cookie "$LYFTA_COOKIE"
```
Replace `jn.xlsx` with your input file name as needed.

## License
MIT

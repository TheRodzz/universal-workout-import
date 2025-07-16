# Usage

## Running the Script

To run the script, you need to provide the path to your workout file and your Lyfta cookie.

```bash
python main.py --file-path /path/to/your/workout_program.pdf --lyfta-cookie "your_lyfta_cookie_here"
```

### Arguments

-   `--file-path`: (Required) The path to the workout program file you want to import.
-   `--lyfta-cookie`: (Required) Your authentication cookie for your Lyfta account.

## Docker Usage

**Important:** Place your workout file in the root of this project directory before building the Docker image. This ensures the file is included in the Docker build context and accessible to the container.

### Build the Docker Image

```bash
docker build -t workout-import .
```

### Run the Docker Container

```bash
docker run \
  -e GEMINI_API_KEY=<YOUR_GEMINI_API_KEY> \
  -e GEMINI_MODEL=<MODEL_NAME> \
  workout-import \
  --file-path "/app/<INPUT-FILE-NAME>" \
  --lyfta-cookie "<YOUR_LYFTA_COOKIE>"
```

- Replace `<YOUR_GEMINI_API_KEY>` with your Gemini API key.
- Replace `<MODEL_NAME>` with the desired Gemini model name.
- Replace `<INPUT-FILE-NAME>` with the name of your workout file (e.g., `workout_program.pdf`).
- Replace `<YOUR_LYFTA_COOKIE>` with your Lyfta authentication cookie. 
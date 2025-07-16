# Universal Workout Import

A tool to parse workout programs from various file formats, structure them using Gemini API, and import them into the Lyfta workout tracker.

## Architecture

![Excel Import Workflow](docs/excel-import-workflow.drawio.png)

**Note:**
- The diagram above shows OpenAI as the LLM provider, but the current implementation uses the **Gemini Free API** instead, making the tool completely free to use.
- To ensure free usage, the app processes **one week at a time** instead of parallel processing multiple weeks parallely.

## Features

- **File Parsing:** Parses workout programs from file formats like PDF and excel.
- **AI-Powered Structuring:** Utilizes a Large Language Model (LLM) to understand and structure the workout data from the input file.
- **Exercise Matching:** Matches exercises from the source file to a predefined database of exercises for consistency.
- **Lyfta Integration:** Seamlessly uploads the structured workout program to your Lyfta account.
- **Parallel Processing:** Processes multiple weeks of a workout program in parallel for faster execution. 

## Known Issues

See [known_issues](docs/known_issues.md) for current limitations and workarounds.

## TODO

See [TODO.md](TODO.md) for upcoming features and ways to contribute.

## License

This project is licensed under a **Custom Non-Commercial License**.  
You are free to use, modify, and distribute this code for **personal, educational, or non-commercial purposes only**.

**Commercial use is prohibited without prior written consent.**  
For commercial licensing inquiries, please contact: vidhuarora84@gmail.com

See [LICENSE](LICENSE) for details.

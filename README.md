# LLM-based Automation Agent

A FastAPI-based automation agent that uses LLM to parse and execute various tasks.

## Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/llm-automation-agent.git
cd llm-automation-agent
```

2. Build the Docker image:
```bash
docker build -t your-username/llm-automation-agent .
```

3. Run the container:
```bash
docker run -e AIPROXY_TOKEN=your-token -p 8000:8000 your-username/llm-automation-agent
```

## API Endpoints

- POST `/run?task=...`: Execute a task
- GET `/read?path=...`: Read file contents
- GET `/filter-csv?path=...&column=...&value=...`: Filter CSV files

## Example Usage

```bash
# Execute a task
curl -X POST "http://localhost:8000/run?task=count weekdays in dates.txt"

# Read a file
curl "http://localhost:8000/read?path=/data/output.txt"
```

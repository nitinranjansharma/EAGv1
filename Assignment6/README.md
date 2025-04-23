# Assignment 6

This project extends the previous assignment and implements a cognitive system with 4 distinct layers: Perception, Memory, Decision-Making, and Action. This architecture is inspired by cognitive science and provides a structured approach to processing information and making decisions.

## Architecture Overview

The system is built around four layers:

1. **Perception Layer**: Handles LLM interactions and perception of the environment
2. **Memory Layer**: Stores and retrieves information
3. **Decision-Making Layer**: Analyzes information and makes decisions
4. **Action Layer**: Executes actions based on decisions

### How It Works

1. The user submits a query
2. The **Perception Layer** processes the query using an LLM (Gemini)
3. The **Memory Layer** provides context from previous interactions
4. The **Decision-Making Layer** analyzes the LLM response and makes a decision
5. The **Action Layer** executes the decision (e.g., calling a function)
6. The result is stored in memory and the cycle continues until a final answer is reached

## Files

- `main.py`: Orchestrates all cognitive layers
- `perception.py`: Handles LLM interactions
- `memory.py`: Manages storing and retrieving information
- `decision_making.py`: Analyzes information and makes decisions
- `action.py`: Executes actions based on decisions
- `server.py`: Provides tools for the action layer to use

## Requirements

- Python 3.8+
- MCP (Model Control Protocol)
- Google Gemini API
- Pydantic
- Other dependencies listed in requirements.txt

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage

Run the main script:

```bash
python main.py
```

This will initialize the cognitive system and process the example query.

## Example

The system can handle complex queries like:

```
Create a new Microsoft presentation and figure out what is the capital of India and write it in morse code? Format the answer as Question and Answer in the same rectangle box
```

The system will:
1. Open PowerPoint
2. Create a new presentation
3. Draw a rectangle
4. Greet in preferred language
5. Convert it to morse code
6. Write the question and answer in the rectangle in preferred language

## Architecture Details

### Perception Layer

The Perception Layer is responsible for:
- Interacting with the LLM (Gemini)
- Processing user queries
- Generating structured responses

### Memory Layer

The Memory Layer is responsible for:
- Storing information about past interactions
- Retrieving relevant information for current decisions
- Managing the importance and categorization of memories

### Decision-Making Layer

The Decision-Making Layer is responsible for:
- Analyzing LLM responses
- Making decisions about what actions to take
- Considering alternatives based on memory
- Evaluating the outcomes of decisions

### Action Layer

The Action Layer is responsible for:
- Executing decisions (e.g., calling functions)
- Interacting with external systems
- Handling errors and exceptions
- Measuring performance

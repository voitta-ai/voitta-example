# Voitta Example

This is an example project that demonstrates how to use the Voitta library to create a FastAPI application that routes API calls to different endpoints.

## Features

- FastAPI application that uses Voitta for routing API calls
- Example endpoints for getting available tools and calling functions
- Environment variable configuration

## Installation

1. Clone the repository:

```bash
git clone https://github.com/debedb/voitta-example.git
cd voitta-example
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

Copy the `.env.example` file to `.env` and update the values as needed.

## Usage

Run the application:

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload
```

The API will be available at http://localhost:8000.

### API Endpoints

- `GET /`: Welcome message
- `GET /tools`: Get all available tools
- `POST /call-function`: Call a function through the Voitta router
- `GET /prompt`: Get the prompt for all tools

## Requirements

- Python 3.8+
- Voitta library
- FastAPI
- Uvicorn
- python-dotenv

## License

MIT

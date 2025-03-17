# Voitta Example

This is an example project that demonstrates how to use the Voitta library to create a FastAPI application that routes API calls to different endpoints.

## Features

- FastAPI application that uses Voitta for routing API calls
- Example endpoints for getting available tools and calling functions
- Environment variable configuration
- Sample filesystem server for demonstration

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

Copy the `.env.example` file to `.env` and update the values as needed:

```bash
cp .env.example .env
# Edit .env to add your OpenAI API key
```

## Running the Filesystem Server

The project includes a sample filesystem server that provides file access functionality. This server needs to be running for the Voitta example to work properly.

### Manual Start

To start the filesystem server manually:

```bash
cd SERVERS/FILESYSTEM
python main.py
```

The server will run on port 50000 by default (configurable in .env).

## Running the Voitta Example

After starting the filesystem server, you can run the Voitta example:

```bash
python voitta_example.py
```

## VS Code Integration

This project includes VS Code launch configurations for easy debugging:

1. Open the project in VS Code
2. Go to the Run and Debug panel (Ctrl+Shift+D or Cmd+Shift+D)
3. Select one of the following launch configurations:
   - **Filesystem Server**: Runs only the filesystem server
   - **Voitta Example**: Runs only the Voitta example
   - **Voitta + Filesystem Server**: Runs both the filesystem server and Voitta example

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `FILESYSTEM_SERVER_PORT`: Port for the filesystem server (default: 50000)

### Voitta Configuration

The `voitta.yaml` file contains the configuration for the Voitta router, including the URL for the filesystem server.

## Requirements

- Python 3.8+
- Voitta library
- FastAPI
- Uvicorn
- python-dotenv
- OpenAI Python client

## License

MIT

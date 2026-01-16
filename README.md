# Flask Script Runner Dashboard

A modern Flask web application that provides an intuitive dashboard interface for executing and managing Python scripts. This application transforms command-line Python script execution into a user-friendly web experience, featuring real-time output visualization, script source code viewing, and comprehensive error handling. Perfect for developers, system administrators, and teams who need a centralized platform to run, monitor, and validate Python scripts without direct server access.

## Features

- Web dashboard for running Python scripts
- Execute `hello_world.py` and `verify_hello_world.py` scripts
- View script source code
- Real-time script output display
- Error handling and validation
- Responsive UI with Tailwind CSS

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Development Server

Run the Flask development server:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Deployment

For production deployment, use a WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## API Endpoints

- `GET /` - Main dashboard page
- `POST /run/<script_name>` - Run a Python script
  - `<script_name>`: `hello_world` or `verify_hello_world`
- `GET /view/<script_name>` - View script source code
- `GET /health` - Health check endpoint

## Scripts

### hello_world.py
A simple script that outputs "Hello from Kortex" with a timestamp.

### verify_hello_world.py
A verification script that tests the hello_world.py script to ensure it's working correctly.

## Configuration

The application uses the following configuration:
- Secret key: `dev-secret-key-change-in-production` (change for production)
- Script timeout: 30 seconds
- Workspace directory: Automatically detected

## Error Handling

The application includes comprehensive error handling:
- 404 errors for unknown endpoints
- 500 errors for internal server issues
- Script execution timeout handling
- Invalid script name validation

## Templates

The application uses Jinja2 templates located in the `templates/` directory:
- `base.html` - Base template with common layout
- `index.html` - Main dashboard page
- `404.html` - Not found error page
- `500.html` - Internal server error page

All templates use Tailwind CSS for styling via CDN.
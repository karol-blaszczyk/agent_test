#!/usr/bin/env python3
"""
Flask application for running and managing Python scripts.
Provides web interface for executing hello_world.py and verify_hello_world.py
"""

import os
import subprocess
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Get the current working directory
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

@app.route('/run/<script_name>', methods=['POST'])
def run_script(script_name):
    """
    Run a Python script and return the output.
    
    Args:
        script_name: Name of the script to run (hello_world or verify_hello_world)
    
    Returns:
        JSON response with output or error
    """
    try:
        # Validate script name
        if script_name not in ['hello_world', 'verify_hello_world']:
            return jsonify({'error': f'Unknown script: {script_name}'}), 400
        
        # Construct script path
        script_file = f'{script_name}.py'
        script_path = os.path.join(WORKSPACE_DIR, script_file)
        
        # Check if script exists
        if not os.path.exists(script_path):
            return jsonify({'error': f'Script not found: {script_file}'}), 404
        
        # Run the script
        result = subprocess.run(
            ['python', script_file],
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Prepare output
        output = []
        if result.stdout:
            output.append(result.stdout)
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        
        # Check return code
        if result.returncode != 0:
            output.append(f"Script exited with code: {result.returncode}")
            return jsonify({
                'error': f'Script failed with exit code {result.returncode}',
                'output': '\n'.join(output)
            }), 500
        
        return jsonify({
            'success': True,
            'output': '\n'.join(output) if output else 'Script completed successfully'
        })
        
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Script execution timed out after 30 seconds'}), 500
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/view/<script_name>')
def view_script(script_name):
    """
    Return the source code of a script.
    
    Args:
        script_name: Name of the script to view
    
    Returns:
        Plain text source code
    """
    try:
        # Validate script name
        if script_name not in ['hello_world', 'verify_hello_world']:
            return f'Unknown script: {script_name}', 404
        
        # Construct script path
        script_file = f'{script_name}.py'
        script_path = os.path.join(WORKSPACE_DIR, script_file)
        
        # Check if script exists
        if not os.path.exists(script_path):
            return f'Script not found: {script_file}', 404
        
        # Read and return the script content
        with open(script_path, 'r') as f:
            content = f.read()
        
        return content, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        return f'Error reading script: {str(e)}', 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'workspace': WORKSPACE_DIR
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Endpoint not found'}), 404
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Development server configuration
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )
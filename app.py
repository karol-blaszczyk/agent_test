#!/usr/bin/env python3
"""
Flask application for running and managing Python scripts.
Provides web interface for executing hello_world.py and verify_hello_world.py
"""

import os
import subprocess
import json
import glob
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Initialize Flask app
app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'

# Get the current working directory
WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

# Set the correct template folder path
template_folder = os.path.join(WORKSPACE_DIR, 'templates')
app.template_folder = template_folder

@app.route('/')
def index():
    """Render the main dashboard page."""
    return render_template('index.html')

@app.route('/hello')
def hello():
    """Render the hello world page."""
    return render_template('hello.html')

@app.route('/scripts')
def scripts():
    """Render the scripts listing page."""
    try:
        # Find all Python scripts in the workspace
        scripts = []
        pattern = os.path.join(WORKSPACE_DIR, '*.py')
        
        for script_path in glob.glob(pattern):
            script_name = os.path.basename(script_path)
            
            # Skip certain files that shouldn't be listed as runnable scripts
            if script_name.startswith('test_') or script_name == 'app.py':
                continue
                
            try:
                # Get file stats
                stat = os.stat(script_path)
                file_size = stat.st_size
                modified_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                
                # Read first few lines to get description
                description = ""
                with open(script_path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        if i >= 10:  # Read first 10 lines max
                            break
                        if line.strip().startswith('"""') or line.strip().startswith("'''"):
                            # Found docstring start
                            docstring_lines = []
                            quote_type = line.strip()[:3]
                            line = line.strip()[3:]
                            if line.endswith(quote_type):
                                # Single line docstring
                                description = line[:-3].strip()
                            else:
                                # Multi-line docstring
                                docstring_lines.append(line)
                                for doc_line in f:
                                    if doc_line.strip().endswith(quote_type):
                                        docstring_lines.append(doc_line.strip()[:-3])
                                        break
                                    docstring_lines.append(doc_line.rstrip())
                                description = ' '.join(docstring_lines).strip()
                            break
                
                scripts.append({
                    'name': script_name.replace('.py', ''),
                    'file_name': script_name,
                    'description': description or f'Python script: {script_name}',
                    'file_size': file_size,
                    'modified_at': modified_time,
                    'path': script_path
                })
                
            except Exception as e:
                # If we can't read a file, skip it but log the error
                app.logger.warning(f"Could not read script {script_name}: {e}")
                continue
        
        # Sort scripts by name
        scripts.sort(key=lambda x: x['name'])
        
        return render_template('scripts.html', scripts=scripts)
        
    except Exception as e:
        return render_template('scripts.html', scripts=[], error=f'Failed to list scripts: {str(e)}')

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

@app.route('/api/scripts')
def api_get_scripts():
    """
    API endpoint to get list of available scripts.
    
    Returns:
        JSON response with list of available scripts and their metadata
    """
    try:
        # Find all Python scripts in the workspace
        scripts = []
        pattern = os.path.join(WORKSPACE_DIR, '*.py')
        
        for script_path in glob.glob(pattern):
            script_name = os.path.basename(script_path)
            
            # Skip certain files that shouldn't be listed as runnable scripts
            if script_name.startswith('test_') or script_name == 'app.py':
                continue
                
            try:
                # Get file stats
                stat = os.stat(script_path)
                file_size = stat.st_size
                modified_time = datetime.fromtimestamp(stat.st_mtime).isoformat()
                
                # Read first few lines to get description
                description = ""
                with open(script_path, 'r', encoding='utf-8') as f:
                    for i, line in enumerate(f):
                        if i >= 10:  # Read first 10 lines max
                            break
                        if line.strip().startswith('"""') or line.strip().startswith("'''"):
                            # Found docstring start
                            docstring_lines = []
                            quote_type = line.strip()[:3]
                            line = line.strip()[3:]
                            if line.endswith(quote_type):
                                # Single line docstring
                                description = line[:-3].strip()
                            else:
                                # Multi-line docstring
                                docstring_lines.append(line)
                                for doc_line in f:
                                    if doc_line.strip().endswith(quote_type):
                                        docstring_lines.append(doc_line.strip()[:-3])
                                        break
                                    docstring_lines.append(doc_line.rstrip())
                                description = ' '.join(docstring_lines).strip()
                            break
                
                scripts.append({
                    'name': script_name.replace('.py', ''),
                    'file_name': script_name,
                    'description': description or f'Python script: {script_name}',
                    'file_size': file_size,
                    'modified_at': modified_time,
                    'path': script_path
                })
                
            except Exception as e:
                # If we can't read a file, skip it but log the error
                app.logger.warning(f"Could not read script {script_name}: {e}")
                continue
        
        # Sort scripts by name
        scripts.sort(key=lambda x: x['name'])
        
        return jsonify({
            'scripts': scripts,
            'count': len(scripts),
            'workspace': WORKSPACE_DIR
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to list scripts: {str(e)}'}), 500

@app.route('/api/scripts/<name>/run', methods=['POST'])
def api_run_script(name):
    """
    API endpoint to run a Python script.
    
    Args:
        name: Name of the script to run (without .py extension)
    
    Returns:
        JSON response with execution results
    """
    try:
        # Construct script path
        script_file = f'{name}.py'
        script_path = os.path.join(WORKSPACE_DIR, script_file)
        
        # Check if script exists
        if not os.path.exists(script_path):
            return jsonify({'error': f'Script not found: {script_file}'}), 404
        
        # Check if it's a Python script
        if not script_path.endswith('.py'):
            return jsonify({'error': 'Only Python scripts are supported'}), 400
        
        # Skip certain files that shouldn't be run
        if name.startswith('test_') or name == 'app':
            return jsonify({'error': 'This script cannot be executed via API'}), 400
        
        # Run the script
        result = subprocess.run(
            ['python', script_file],
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )
        
        # Prepare response
        execution_result = {
            'script_name': name,
            'status': 'success' if result.returncode == 0 else 'error',
            'return_code': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'executed_at': datetime.now().isoformat()
        }
        
        # Add error message if script failed
        if result.returncode != 0:
            execution_result['error_message'] = f'Script exited with code {result.returncode}'
        
        return jsonify(execution_result)
        
    except subprocess.TimeoutExpired:
        return jsonify({
            'error': 'Script execution timed out after 30 seconds',
            'script_name': name,
            'status': 'timeout'
        }), 500
    except Exception as e:
        return jsonify({
            'error': f'Internal server error: {str(e)}',
            'script_name': name,
            'status': 'error'
        }), 500

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
        port=5021,  # Changed to avoid port conflicts
        debug=True,
        threaded=True
    )
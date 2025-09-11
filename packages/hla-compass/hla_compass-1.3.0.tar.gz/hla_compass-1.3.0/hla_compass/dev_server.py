"""
Hot-reload development server for HLA-Compass modules

Provides automatic reloading, real-time logging, and interactive testing UI.
"""

import os
import sys
import json
import time
import threading
import subprocess
import importlib
import traceback
from pathlib import Path
from typing import Any, Dict, Optional, Callable
from datetime import datetime
import asyncio
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from aiohttp import web
import aiohttp_cors

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.syntax import Syntax
from rich.text import Text

from .testing import ModuleTester
from .module import Module

console = Console()
logger = logging.getLogger(__name__)


class ModuleReloader(FileSystemEventHandler):
    """Watches for file changes and triggers module reload"""
    
    def __init__(self, callback: Callable, paths: list[str], extensions: list[str] = None):
        self.callback = callback
        self.paths = paths
        self.extensions = extensions or ['.py', '.tsx', '.jsx', '.ts', '.js']
        self.last_reload = 0
        self.reload_delay = 1.0  # Debounce delay in seconds
        
    def on_modified(self, event):
        if event.is_directory:
            return
            
        # Check if file has a watched extension
        file_path = Path(event.src_path)
        if file_path.suffix not in self.extensions:
            return
            
        # Skip __pycache__ and other generated files
        if '__pycache__' in str(file_path) or '.pyc' in str(file_path):
            return
            
        # Debounce rapid changes
        current_time = time.time()
        if current_time - self.last_reload < self.reload_delay:
            return
            
        self.last_reload = current_time
        console.print(f"[yellow]⚡ File changed: {file_path.name}[/yellow]")
        self.callback(str(file_path))


class ModuleDevServer:
    """Development server with hot-reload and testing UI"""
    
    def __init__(self, module_dir: str = ".", port: int = 8080):
        self.module_dir = Path(module_dir).resolve()
        self.port = port
        self.backend_dir = self.module_dir / "backend"
        self.frontend_dir = self.module_dir / "frontend"
        self.manifest_path = self.module_dir / "manifest.json"
        
        # Module state
        self.module = None
        self.module_error = None
        self.reload_count = 0
        self.test_results = []
        
        # Load manifest
        self.manifest = self._load_manifest()
        self.module_name = self.manifest.get("name", "unknown")
        self.module_type = self.manifest.get("type", "no-ui")
        
        # File watcher
        self.observer = Observer()
        self.reloader = ModuleReloader(
            callback=self._reload_module,
            paths=[str(self.backend_dir)]
        )
        
        # Web server
        self.app = web.Application()
        self._setup_routes()
        
        # Frontend process (for UI modules)
        self.frontend_process = None
        
    def _load_manifest(self) -> dict:
        """Load module manifest"""
        if not self.manifest_path.exists():
            console.print("[red]Error: manifest.json not found[/red]")
            return {}
            
        try:
            with open(self.manifest_path) as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red]Error loading manifest: {e}[/red]")
            return {}
    
    def _reload_module(self, changed_file: str = None):
        """Reload the module after file changes"""
        self.reload_count += 1
        console.print(f"[blue]🔄 Reloading module (#{self.reload_count})...[/blue]")
        
        try:
            # Clear any cached imports
            module_file = self.backend_dir / "main.py"
            if not module_file.exists():
                raise FileNotFoundError(f"Module file not found: {module_file}")
            
            # Remove from sys.modules to force reload
            module_name = "main"
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Add backend dir to path if not already there
            if str(self.backend_dir) not in sys.path:
                sys.path.insert(0, str(self.backend_dir))
            
            # Import the module
            spec = importlib.util.spec_from_file_location("main", module_file)
            module = importlib.util.module_from_spec(spec)
            sys.modules["main"] = module
            spec.loader.exec_module(module)
            
            # Find the module class (inherits from Module)
            module_class = None
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and 
                    issubclass(obj, Module) and 
                    obj != Module):
                    module_class = obj
                    break
            
            if not module_class:
                raise ValueError("No Module subclass found in main.py")
            
            # Instantiate the module
            self.module = module_class()
            self.module_error = None
            
            console.print(f"[green]✓ Module reloaded successfully[/green]")
            
        except Exception as e:
            self.module_error = {
                "type": type(e).__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }
            console.print(f"[red]✗ Reload failed: {e}[/red]")
            
            # Show helpful error messages
            self._show_error_help(e)
    
    def _show_error_help(self, error: Exception):
        """Display helpful error messages with suggestions"""
        error_type = type(error).__name__
        error_msg = str(error)
        
        suggestions = {
            "ModuleNotFoundError": "💡 Try: pip install -r backend/requirements.txt",
            "SyntaxError": "💡 Check for missing colons, brackets, or indentation",
            "ImportError": "💡 Check if the module is installed or the import path is correct",
            "AttributeError": "💡 Check if you're calling the right method or attribute",
            "TypeError": "💡 Check function arguments and types",
            "NameError": "💡 Check for typos in variable or function names"
        }
        
        if error_type in suggestions:
            console.print(f"[yellow]{suggestions[error_type]}[/yellow]")
    
    def _setup_routes(self):
        """Setup web server routes"""
        cors = aiohttp_cors.setup(self.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
                allow_methods="*"
            )
        })
        
        # API routes
        self.app.router.add_get("/api/status", self.handle_status)
        self.app.router.add_post("/api/execute", self.handle_execute)
        self.app.router.add_get("/api/manifest", self.handle_manifest)
        self.app.router.add_get("/api/logs", self.handle_logs)
        self.app.router.add_get("/", self.handle_index)
        
        # Enable CORS for all routes
        for route in list(self.app.router.routes()):
            cors.add(route)
    
    async def handle_index(self, request):
        """Serve the development UI"""
        html = self._generate_dev_ui()
        return web.Response(text=html, content_type="text/html")
    
    async def handle_status(self, request):
        """Get module status"""
        return web.json_response({
            "module_name": self.module_name,
            "module_type": self.module_type,
            "loaded": self.module is not None,
            "error": self.module_error,
            "reload_count": self.reload_count,
            "backend_dir": str(self.backend_dir),
            "frontend_dir": str(self.frontend_dir) if self.module_type == "with-ui" else None
        })
    
    async def handle_execute(self, request):
        """Execute the module with test data"""
        if not self.module:
            return web.json_response({
                "status": "error",
                "error": self.module_error or {"message": "Module not loaded"}
            }, status=500)
        
        try:
            # Get input data from request
            data = await request.json()
            input_data = data.get("input", {})
            
            # Create mock context
            context = {
                "job_id": f"dev-test-{datetime.now().isoformat()}",
                "user_id": "dev-user",
                "organization_id": "dev-org",
                "timestamp": datetime.now().isoformat()
            }
            
            # Execute module
            result = self.module.execute(input_data, context)
            
            # Store test result
            self.test_results.append({
                "timestamp": datetime.now().isoformat(),
                "input": input_data,
                "output": result,
                "success": result.get("status") == "success"
            })
            
            return web.json_response(result)
            
        except Exception as e:
            error_response = {
                "status": "error",
                "error": {
                    "type": type(e).__name__,
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
            }
            return web.json_response(error_response, status=500)
    
    async def handle_manifest(self, request):
        """Get module manifest"""
        return web.json_response(self.manifest)
    
    async def handle_logs(self, request):
        """Get recent test results"""
        return web.json_response({
            "results": self.test_results[-10:],  # Last 10 results
            "total": len(self.test_results)
        })
    
    def _generate_dev_ui(self) -> str:
        """Generate the development UI HTML"""
        return '''<!DOCTYPE html>
<html>
<head>
    <title>HLA-Compass Dev Server</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: white;
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #333;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status { 
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }
        .status.loaded { background: #10b981; color: white; }
        .status.error { background: #ef4444; color: white; }
        .status.loading { background: #f59e0b; color: white; }
        
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
        
        .panel {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        h2 { 
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
        }
        
        textarea {
            width: 100%;
            min-height: 200px;
            padding: 12px;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 13px;
            resize: vertical;
        }
        
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 500;
            cursor: pointer;
            margin-top: 10px;
            transition: all 0.2s;
        }
        
        button:hover {
            background: #5a67d8;
            transform: translateY(-1px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        button:active { transform: translateY(0); }
        
        .output {
            background: #f7fafc;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 12px;
            margin-top: 10px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .output.success { border-color: #10b981; background: #f0fdf4; }
        .output.error { border-color: #ef4444; background: #fef2f2; }
        
        .info-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f3f4f6;
        }
        
        .info-label { color: #6b7280; font-size: 14px; }
        .info-value { 
            color: #333;
            font-weight: 500;
            font-size: 14px;
            font-family: 'Monaco', 'Menlo', monospace;
        }
        
        .logs {
            margin-top: 15px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .log-entry {
            padding: 8px;
            margin-bottom: 5px;
            background: #f9fafb;
            border-radius: 6px;
            font-size: 13px;
            font-family: 'Monaco', 'Menlo', monospace;
        }
        
        .log-entry.success { background: #f0fdf4; }
        .log-entry.error { background: #fef2f2; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>
                🧬 HLA-Compass Dev Server
                <span id="status" class="status loading">Loading...</span>
            </h1>
            <p style="color: #6b7280; margin-top: 10px;">
                Hot-reload development environment for module testing
            </p>
        </div>
        
        <div class="grid">
            <div class="panel">
                <h2>📝 Input</h2>
                <textarea id="input" placeholder='{"param1": "value1", "param2": "value2"}'>{}</textarea>
                <button onclick="executeModule()">🚀 Execute Module</button>
                <button onclick="loadExample()" style="background: #6b7280; margin-left: 10px;">📄 Load Example</button>
            </div>
            
            <div class="panel">
                <h2>📊 Output</h2>
                <div id="output" class="output">Ready to execute...</div>
            </div>
            
            <div class="panel">
                <h2>ℹ️ Module Info</h2>
                <div class="info-item">
                    <span class="info-label">Name:</span>
                    <span class="info-value" id="module-name">-</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Type:</span>
                    <span class="info-value" id="module-type">-</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Reloads:</span>
                    <span class="info-value" id="reload-count">0</span>
                </div>
                <div class="info-item">
                    <span class="info-label">Backend:</span>
                    <span class="info-value" id="backend-dir">-</span>
                </div>
            </div>
            
            <div class="panel">
                <h2>📜 Recent Executions</h2>
                <div id="logs" class="logs">
                    <div class="log-entry">No executions yet...</div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        let moduleStatus = {};
        let exampleInput = {};
        
        // Load status on page load
        window.onload = async () => {
            await updateStatus();
            await loadManifest();
            setInterval(updateStatus, 2000); // Poll for changes
        };
        
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                moduleStatus = await response.json();
                
                const statusEl = document.getElementById('status');
                if (moduleStatus.error) {
                    statusEl.className = 'status error';
                    statusEl.textContent = 'Error';
                } else if (moduleStatus.loaded) {
                    statusEl.className = 'status loaded';
                    statusEl.textContent = 'Ready';
                } else {
                    statusEl.className = 'status loading';
                    statusEl.textContent = 'Loading...';
                }
                
                document.getElementById('module-name').textContent = moduleStatus.module_name;
                document.getElementById('module-type').textContent = moduleStatus.module_type;
                document.getElementById('reload-count').textContent = moduleStatus.reload_count;
                document.getElementById('backend-dir').textContent = 
                    moduleStatus.backend_dir?.split('/').slice(-2).join('/') || '-';
                    
            } catch (e) {
                console.error('Failed to update status:', e);
            }
        }
        
        async function loadManifest() {
            try {
                const response = await fetch('/api/manifest');
                const manifest = await response.json();
                
                // Create example input from manifest
                if (manifest.inputs) {
                    exampleInput = {};
                    for (const [key, schema] of Object.entries(manifest.inputs)) {
                        if (schema.type === 'string') {
                            exampleInput[key] = schema.default || 'example_value';
                        } else if (schema.type === 'number' || schema.type === 'integer') {
                            exampleInput[key] = schema.default || 10;
                        } else if (schema.type === 'boolean') {
                            exampleInput[key] = schema.default || false;
                        } else if (schema.type === 'array') {
                            exampleInput[key] = schema.default || [];
                        } else if (schema.type === 'object') {
                            exampleInput[key] = schema.default || {};
                        }
                    }
                    document.getElementById('input').value = JSON.stringify(exampleInput, null, 2);
                }
            } catch (e) {
                console.error('Failed to load manifest:', e);
            }
        }
        
        function loadExample() {
            document.getElementById('input').value = JSON.stringify(exampleInput, null, 2);
        }
        
        async function executeModule() {
            const inputEl = document.getElementById('input');
            const outputEl = document.getElementById('output');
            
            try {
                const input = JSON.parse(inputEl.value);
                
                outputEl.textContent = 'Executing...';
                outputEl.className = 'output';
                
                const response = await fetch('/api/execute', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({input})
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    outputEl.className = 'output success';
                } else {
                    outputEl.className = 'output error';
                }
                
                outputEl.textContent = JSON.stringify(result, null, 2);
                
                // Update logs
                await updateLogs();
                
            } catch (e) {
                outputEl.className = 'output error';
                outputEl.textContent = 'Error: ' + e.message;
            }
        }
        
        async function updateLogs() {
            try {
                const response = await fetch('/api/logs');
                const data = await response.json();
                
                const logsEl = document.getElementById('logs');
                if (data.results.length === 0) {
                    logsEl.innerHTML = '<div class="log-entry">No executions yet...</div>';
                } else {
                    logsEl.innerHTML = data.results.reverse().map(r => {
                        const cls = r.success ? 'success' : 'error';
                        const time = new Date(r.timestamp).toLocaleTimeString();
                        return `<div class="log-entry ${cls}">${time} - ${r.success ? '✓' : '✗'} ${JSON.stringify(r.input).slice(0, 50)}...</div>`;
                    }).join('');
                }
            } catch (e) {
                console.error('Failed to update logs:', e);
            }
        }
    </script>
</body>
</html>'''
    
    def start_frontend_dev(self):
        """Start frontend development server for UI modules"""
        if self.module_type != "with-ui":
            return
            
        if not self.frontend_dir.exists():
            console.print("[yellow]No frontend directory found[/yellow]")
            return
            
        package_json = self.frontend_dir / "package.json"
        if not package_json.exists():
            console.print("[yellow]No package.json found in frontend[/yellow]")
            return
            
        try:
            # Install dependencies if node_modules doesn't exist
            node_modules = self.frontend_dir / "node_modules"
            if not node_modules.exists():
                console.print("[blue]Installing frontend dependencies...[/blue]")
                subprocess.run(
                    ["npm", "install"],
                    cwd=self.frontend_dir,
                    check=True,
                    capture_output=True
                )
            
            # Start webpack dev server
            console.print("[blue]Starting frontend dev server on port 3000...[/blue]")
            self.frontend_process = subprocess.Popen(
                ["npm", "run", "dev"],
                cwd=self.frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
        except Exception as e:
            console.print(f"[yellow]Could not start frontend server: {e}[/yellow]")
    
    async def start(self):
        """Start the development server"""
        console.print(Panel.fit(
            f"[bold green]🚀 Starting HLA-Compass Dev Server[/bold green]\n\n"
            f"Module: [cyan]{self.module_name}[/cyan]\n"
            f"Type: [cyan]{self.module_type}[/cyan]\n"
            f"Port: [cyan]http://localhost:{self.port}[/cyan]\n\n"
            f"[yellow]Watching for changes...[/yellow]\n"
            f"Press [bold]Ctrl+C[/bold] to stop",
            title="Dev Server",
            border_style="green"
        ))
        
        # Initial module load
        self._reload_module()
        
        # Start file watcher
        self.observer.schedule(self.reloader, str(self.backend_dir), recursive=True)
        self.observer.start()
        
        # Start frontend dev server if UI module
        if self.module_type == "with-ui":
            self.start_frontend_dev()
        
        # Start web server
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self.port)
        
        try:
            await site.start()
            console.print(f"\n[green]✓ Dev server running at http://localhost:{self.port}[/green]")
            console.print("[dim]Open in browser for interactive testing UI[/dim]\n")
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            console.print("\n[yellow]Shutting down...[/yellow]")
        finally:
            self.observer.stop()
            self.observer.join()
            
            if self.frontend_process:
                self.frontend_process.terminate()
                
            await runner.cleanup()


def run_dev_server(module_dir: str = ".", port: int = 8080):
    """Entry point for dev server"""
    server = ModuleDevServer(module_dir, port)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        console.print("\n[green]Dev server stopped[/green]")
    except Exception as e:
        console.print(f"[red]Server error: {e}[/red]")
        raise
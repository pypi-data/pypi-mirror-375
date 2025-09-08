#!/usr/bin/env python3
"""
Advanced CLI for AI Coder with MCP server integration
Provides a Gemini-like conversational coding experience
"""

import os
import sys
import json
import asyncio
import readline
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Import local modules
sys.path.append(os.path.dirname(__file__))
from tools.ollama import OllamaClient
from tools.files import FileTools  
from tools.shell import ShellTool
from utils.logger import HistoryLogger

class AiCoderCLI:
    def __init__(self, workspace_dir: str = None):
        self.workspace_dir = workspace_dir or os.getcwd()
        self.history_dir = os.path.join(self.workspace_dir, '.codeas-history')
        self.backup_dir = os.path.join(self.workspace_dir, '.codeas_backups')
        
        # Initialize components
        self.logger = HistoryLogger(self.history_dir)
        self.ollama = OllamaClient(logger=self.logger)
        self.files = FileTools(root=self.workspace_dir, backup_dir='.codeas_backups', logger=self.logger)
        self.shell = ShellTool(logger=self.logger)
        
        # Session state
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.context_files: List[str] = []
        self.conversation_history: List[Dict] = []
        
        # Setup readline for command history
        self._setup_readline()
        
    def _setup_readline(self):
        """Setup readline for better CLI experience"""
        try:
            history_file = os.path.join(self.history_dir, 'cli_history.txt')
            if os.path.exists(history_file):
                readline.read_history_file(history_file)
            readline.set_history_length(1000)
            
            # Set up tab completion
            readline.set_completer(self._completer)
            readline.parse_and_bind('tab: complete')
        except ImportError:
            pass  # readline not available on Windows
    
    def _completer(self, text, state):
        """Tab completion for commands"""
        commands = [
            'help', 'exit', 'quit', 'clear', 'context', 'files', 'run', 
            'read', 'write', 'edit', 'create', 'delete', 'analyze', 
            'explain', 'fix', 'optimize', 'test', 'review', 'workspace'
        ]
        
        matches = [cmd for cmd in commands if cmd.startswith(text)]
        if state < len(matches):
            return matches[state]
        return None
    
    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*70)
        print("🚀 AI CODER - Advanced Coding Assistant")
        print("="*70)
        print(f"📁 Workspace: {self.workspace_dir}")
        print(f"🔧 Session: {self.session_id}")
        print(f"🤖 Model: DeepSeek R1 8B (via Ollama)")
        print("\n💡 Commands:")
        print("  help          - Show all commands")
        print("  context       - Manage workspace context")
        print("  analyze       - Analyze codebase")
        print("  <question>    - Ask AI anything about your code")
        print("  exit/quit     - Exit the application")
        print("\n" + "="*70 + "\n")
    
    async def scan_workspace(self, progress_callback=None):
        """Scan workspace and build context"""
        print("🔍 Scanning workspace...")
        
        context = {
            'files': [],
            'structure': {},
            'languages': set(),
            'frameworks': set()
        }
        
        # Get file list
        try:
            result = await self.files.list_dir({'dir': '.'})
            context['files'] = result
            
            # Analyze file types and structure
            for item in result:
                if item['type'] == 'file':
                    ext = Path(item['name']).suffix.lower()
                    if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']:
                        context['languages'].add(ext[1:])
                    
                    # Detect frameworks
                    if item['name'] in ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod']:
                        context['frameworks'].add(item['name'])
                        
        except Exception as e:
            print(f"❌ Error scanning workspace: {e}")
        
        return context
    
    async def read_project_files(self, extensions: List[str] = None) -> Dict[str, str]:
        """Read important project files for context"""
        if extensions is None:
            extensions = ['.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml']
        
        files_content = {}
        
        try:
            # Get all files in workspace
            result = await self.files.list_dir({'dir': '.'})
            
            for item in result:
                if item['type'] == 'file':
                    file_path = item['name']
                    ext = Path(file_path).suffix.lower()
                    
                    if ext in extensions and not file_path.startswith('.'):
                        try:
                            content_result = await self.files.read_file({'path': file_path})
                            files_content[file_path] = content_result['data']
                        except Exception as e:
                            print(f"⚠️  Could not read {file_path}: {e}")
                            
        except Exception as e:
            print(f"❌ Error reading project files: {e}")
        
        return files_content
    
    async def analyze_codebase(self):
        """Analyze the entire codebase"""
        print("🔍 Analyzing codebase...")
        
        # Read project files
        files_content = await self.read_project_files()
        
        if not files_content:
            print("❌ No files found to analyze")
            return
        
        # Create analysis prompt
        files_info = "\n".join([f"=== {path} ===\n{content[:500]}..." 
                               if len(content) > 500 else f"=== {path} ===\n{content}"
                               for path, content in files_content.items()])
        
        prompt = f"""Analyze this codebase and provide a comprehensive overview:

{files_info}

Please provide:
1. Project structure and architecture
2. Main technologies and frameworks used
3. Key components and their purposes
4. Code quality assessment
5. Potential improvements or issues
6. Dependencies and configuration files
"""
        
        await self._ask_ai(prompt, system_prompt="You are an expert code analyst. Provide detailed, actionable insights about codebases.")
    
    async def _ask_ai(self, user_prompt: str, system_prompt: str = None, include_context: bool = True):
        """Ask AI with proper context and streaming response"""
        
        # Build context if requested
        context_info = ""
        if include_context and self.context_files:
            context_info = "\n=== WORKSPACE CONTEXT ===\n"
            for file_path in self.context_files[:5]:  # Limit to 5 files
                try:
                    result = await self.files.read_file({'path': file_path})
                    content = result['data']
                    context_info += f"\n--- {file_path} ---\n{content[:1000]}\n"
                except Exception as e:
                    context_info += f"\n--- {file_path} (Error: {e}) ---\n"
        
        # Prepare the full prompt
        full_prompt = f"{context_info}\n=== USER QUERY ===\n{user_prompt}"
        
        # Default system prompt
        if not system_prompt:
            system_prompt = """You are an expert AI coding assistant. You help developers with:
- Code analysis and review
- Bug fixing and optimization
- Explaining complex code
- Writing new features
- Best practices and patterns
- Architecture decisions

Always provide practical, actionable advice with code examples when relevant."""
        
        # Prepare request
        request_data = {
            'prompt': full_prompt,
            'system': system_prompt,
            'model': 'deepseek-r1:8b'
        }
        
        print("\n🤖 AI Response:")
        print("-" * 50)
        
        # Stream response
        try:
            def progress_handler(payload):
                message = payload.get('message', '')
                if message and not message.startswith('<think>') and not message.startswith('</think>'):
                    print(message, end='', flush=True)
            
            result = await self.ollama.chat(request_data, progress_cb=progress_handler)
            print("\n" + "-" * 50)
            
            # Save to conversation history
            self.conversation_history.append({
                'timestamp': datetime.now().isoformat(),
                'user': user_prompt,
                'assistant': result.get('content', ''),
                'context_files': self.context_files.copy()
            })
            
        except Exception as e:
            print(f"\n❌ Error getting AI response: {e}")
    
    def _parse_command(self, user_input: str) -> tuple[str, str]:
        """Parse user input into command and arguments"""
        parts = user_input.strip().split(' ', 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        return command, args
    
    async def handle_context_command(self, args: str):
        """Handle context management commands"""
        if not args:
            print(f"\n📁 Current context files ({len(self.context_files)}):")
            for i, file_path in enumerate(self.context_files, 1):
                print(f"  {i}. {file_path}")
            return
        
        parts = args.split(' ', 1)
        action = parts[0].lower()
        
        if action == 'add':
            if len(parts) > 1:
                file_path = parts[1]
                if file_path not in self.context_files:
                    # Verify file exists
                    try:
                        await self.files.read_file({'path': file_path})
                        self.context_files.append(file_path)
                        print(f"✅ Added {file_path} to context")
                    except Exception as e:
                        print(f"❌ Could not add {file_path}: {e}")
                else:
                    print(f"⚠️  {file_path} already in context")
            else:
                print("❌ Usage: context add <file_path>")
        
        elif action == 'remove':
            if len(parts) > 1:
                file_path = parts[1]
                if file_path in self.context_files:
                    self.context_files.remove(file_path)
                    print(f"✅ Removed {file_path} from context")
                else:
                    print(f"⚠️  {file_path} not in context")
            else:
                print("❌ Usage: context remove <file_path>")
        
        elif action == 'clear':
            self.context_files.clear()
            print("✅ Cleared all context files")
        
        elif action == 'auto':
            # Auto-add important files
            await self._auto_add_context()
        
        else:
            print("❌ Usage: context [add|remove|clear|auto] [file_path]")
    
    async def _auto_add_context(self):
        """Automatically add important files to context"""
        important_files = [
            'README.md', 'main.py', '__init__.py', 'setup.py', 'requirements.txt',
            'package.json', 'tsconfig.json', 'Dockerfile', '.gitignore'
        ]
        
        added = 0
        for file_name in important_files:
            try:
                await self.files.read_file({'path': file_name})
                if file_name not in self.context_files:
                    self.context_files.append(file_name)
                    added += 1
            except:
                continue
        
        print(f"✅ Auto-added {added} important files to context")
    
    async def handle_files_command(self, args: str):
        """Handle file operations"""
        if not args:
            # List files in current directory
            try:
                result = await self.files.list_dir({'dir': '.'})
                print("\n📁 Files in current directory:")
                for item in result:
                    icon = "📁" if item['type'] == 'dir' else "📄"
                    print(f"  {icon} {item['name']}")
            except Exception as e:
                print(f"❌ Error listing files: {e}")
            return
        
        parts = args.split(' ', 1)
        action = parts[0].lower()
        
        if action == 'read' and len(parts) > 1:
            file_path = parts[1]
            try:
                result = await self.files.read_file({'path': file_path})
                print(f"\n📄 Content of {file_path}:")
                print("-" * 50)
                print(result['data'])
                print("-" * 50)
            except Exception as e:
                print(f"❌ Error reading {file_path}: {e}")
        
        elif action == 'create' and len(parts) > 1:
            file_path = parts[1]
            print(f"Creating {file_path}...")
            print("Enter content (Ctrl+D to finish):")
            content_lines = []
            try:
                while True:
                    line = input()
                    content_lines.append(line)
            except EOFError:
                pass
            
            content = '\n'.join(content_lines)
            try:
                await self.files.write_file({'path': file_path, 'data': content})
                print(f"✅ Created {file_path}")
            except Exception as e:
                print(f"❌ Error creating {file_path}: {e}")
        
        else:
            print("❌ Usage: files [read|create] <file_path>")
    
    async def handle_run_command(self, args: str):
        """Handle shell command execution"""
        if not args:
            print("❌ Usage: run <command>")
            return
        
        print(f"🔧 Running: {args}")
        try:
            def progress_handler(payload):
                if 'output' in payload:
                    print(payload['output'], end='')
            
            result = await self.shell.run_cmd(
                {'cmd': args, 'cwd': self.workspace_dir}, 
                progress_cb=progress_handler
            )
            
            if result.get('ok'):
                print(f"\n✅ Command completed (exit code: {result.get('code', 0)})")
            else:
                print(f"\n❌ Command failed (exit code: {result.get('code', 1)})")
                
        except Exception as e:
            print(f"❌ Error running command: {e}")
    
    def show_help(self):
        """Show help information"""
        help_text = """
🤖 AI CODER - Command Reference

BASIC COMMANDS:
  help                 - Show this help
  exit, quit           - Exit the application
  clear               - Clear the screen

CONTEXT MANAGEMENT:
  context              - Show current context files
  context add <file>   - Add file to context
  context remove <file>- Remove file from context
  context clear        - Clear all context
  context auto         - Auto-add important files

FILE OPERATIONS:
  files                - List files in current directory
  files read <file>    - Read and display file content
  files create <file>  - Create a new file interactively

ANALYSIS:
  analyze              - Analyze entire codebase
  workspace            - Show workspace information

SHELL COMMANDS:
  run <command>        - Execute shell command

AI INTERACTION:
  Just type your question or request naturally!
  Examples:
    - "Explain this function in main.py"
    - "Find bugs in my code"
    - "How can I optimize this algorithm?"
    - "Write a test for the User class"
    - "Refactor this code to use async/await"

The AI has access to your workspace context and can help with:
- Code review and analysis
- Bug fixing and debugging
- Writing new features
- Optimization suggestions
- Testing and documentation
- Architecture decisions
"""
        print(help_text)
    
    async def run(self):
        """Main CLI loop"""
        self.print_banner()
        
        # Auto-add context on startup
        await self._auto_add_context()
        
        while True:
            try:
                # Get user input
                user_input = input("\n🔧 ai-coder> ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                command, args = self._parse_command(user_input)
                
                # Handle commands
                if command in ['exit', 'quit']:
                    print("👋 Goodbye!")
                    break
                
                elif command == 'help':
                    self.show_help()
                
                elif command == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.print_banner()
                
                elif command == 'context':
                    await self.handle_context_command(args)
                
                elif command == 'files':
                    await self.handle_files_command(args)
                
                elif command == 'run':
                    await self.handle_run_command(args)
                
                elif command == 'analyze':
                    await self.analyze_codebase()
                
                elif command == 'workspace':
                    context = await self.scan_workspace()
                    print(f"\n📊 Workspace Information:")
                    print(f"  Directory: {self.workspace_dir}")
                    print(f"  Files: {len(context['files'])}")
                    print(f"  Languages: {', '.join(context['languages']) if context['languages'] else 'None detected'}")
                    print(f"  Context files: {len(self.context_files)}")
                
                else:
                    # Treat as AI query
                    await self._ask_ai(user_input)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
        
        # Save history
        try:
            history_file = os.path.join(self.history_dir, 'cli_history.txt')
            readline.write_history_file(history_file)
        except:
            pass

def main():
    """Entry point for the CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Coder - Advanced Coding Assistant")
    parser.add_argument('--workspace', '-w', default=os.getcwd(), 
                       help='Workspace directory (default: current directory)')
    
    args = parser.parse_args()
    
    cli = AiCoderCLI(workspace_dir=args.workspace)
    asyncio.run(cli.run())

if __name__ == '__main__':
    main()

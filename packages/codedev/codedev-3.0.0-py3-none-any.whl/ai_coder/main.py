#!/usr/bin/env python3
"""
CodeDev - AI Coding Assistant
Simple, interactive coding assistant with AI
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path

class CodeDev:
    def __init__(self):
        self.workspace = os.getcwd()
        self.running = False
        
    def print_banner(self):
        """Print welcome banner"""
        print("\n" + "="*60)
        print("🚀 CodeDev - AI Coding Assistant")
        print("="*60)
        print(f"📁 Workspace: {self.workspace}")
        print(f"🤖 AI Model: DeepSeek R1 8B")
        print("\n💡 What can I help you with today?")
        print("  • Analyze your codebase")
        print("  • Create new files")
        print("  • Explain existing code")
        print("  • Find and fix bugs")
        print("  • Optimize performance")
        print("  • Write tests")
        print("\n" + "="*60 + "\n")
    
    def check_setup(self):
        """Check if everything is set up correctly"""
        try:
            # Check Ollama
            result = subprocess.run(
                ["curl", "-s", "http://127.0.0.1:11434/api/version"], 
                capture_output=True, 
                timeout=2
            )
            if result.returncode != 0:
                return False, "Ollama server not running. Please run: ollama serve"
        except:
            return False, "Ollama not detected. Please install and run: ollama serve"
        
        # Check DeepSeek model
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            if "deepseek-r1" not in result.stdout:
                return False, "DeepSeek model not found. Run: ollama pull deepseek-r1:8b"
        except:
            return False, "Could not check Ollama models"
        
        return True, "Setup OK"
    
    def call_mcp_server(self, tool, input_data):
        """Call the MCP server and get response"""
        import uuid
        
        request = {
            "id": str(uuid.uuid4()),
            "tool": tool,
            "input": input_data
        }
        
        try:
            # Start MCP server process
            proc = subprocess.Popen(
                [sys.executable, str(Path(__file__).parent / "server.py")],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            
            # Send request
            request_json = json.dumps(request)
            proc.stdin.write(request_json + "\n")
            proc.stdin.flush()
            
            # Collect response
            response_parts = []
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                    
                try:
                    response = json.loads(line.strip())
                    if response.get('type') == 'progress':
                        payload = response.get('payload', {})
                        if 'message' in payload:
                            message = payload['message']
                            if not message.startswith('<think>') and not message.startswith('</think>'):
                                print(message, end='', flush=True)
                    elif response.get('type') == 'result':
                        if response.get('id') == request['id']:
                            proc.terminate()
                            return response.get('payload', {})
                except json.JSONDecodeError:
                    continue
                except:
                    break
            
            proc.terminate()
            return {}
            
        except Exception as e:
            print(f"❌ Error calling server: {e}")
            return {}
    
    async def ask_ai(self, question, context_files=None):
        """Ask AI a question with context"""
        # Build context
        context = ""
        workspace_info = ""
        
        # Get workspace context
        files_result = self.call_mcp_server("fs.list", {"dir": "."})
        if files_result:
            file_types = {}
            for item in files_result:
                if item['type'] == 'file':
                    ext = Path(item['name']).suffix.lower()
                    if ext:
                        file_types[ext] = file_types.get(ext, 0) + 1
            
            if file_types:
                workspace_info = f"\nWorkspace context: This appears to be a project with {', '.join([f'{count} {ext} files' for ext, count in file_types.items() if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.go', '.rs']])}"
        
        # Add file context if specified
        if context_files:
            context += "\n=== RELEVANT FILES ===\n"
            for file_path in context_files[:3]:  # Limit to 3 files
                file_data = self.call_mcp_server("fs.read", {"path": file_path})
                if file_data.get('data'):
                    context += f"\n--- {file_path} ---\n{file_data['data'][:2000]}\n"
        
        # Enhanced system prompt for better responses
        system_prompt = """You are CodeDev, an advanced AI coding assistant. You help developers with:

🎯 Core Expertise:
- Code analysis, review, and optimization
- Bug detection and debugging assistance  
- Architecture design and best practices
- Testing strategies and implementation
- Performance optimization
- Security vulnerability assessment
- Documentation and code explanation

💡 Response Style:
- Be practical and actionable
- Provide code examples when relevant
- Explain reasoning behind suggestions
- Use emojis appropriately for readability
- Structure responses with clear sections
- Give step-by-step guidance when needed

🔍 Context Awareness:
- Consider the programming language and framework being used
- Understand project structure and dependencies
- Provide solutions appropriate to the codebase maturity
- Suggest modern best practices and patterns

Always provide helpful, detailed responses that demonstrate deep understanding of software development."""
        
        # Prepare enhanced prompt
        full_prompt = f"{workspace_info}{context}\n\n=== DEVELOPER QUERY ===\n{question}\n\nPlease provide a comprehensive, helpful response as CodeDev AI assistant."
        
        request_data = {
            'prompt': full_prompt,
            'system': system_prompt,
            'model': 'deepseek-r1:8b'
        }
        
        print("\n🤖 CodeDev AI: ", end="")
        result = self.call_mcp_server("ollama.chat", request_data)
        print("\n")
        
        return result
    
    async def list_files(self, directory="."):
        """List files in directory"""
        result = self.call_mcp_server("fs.list", {"dir": directory})
        
        if result:
            print(f"\n📁 Files in {directory}:")
            for item in result:
                icon = "📁" if item['type'] == 'dir' else "📄"
                print(f"  {icon} {item['name']}")
        else:
            print(f"❌ Could not list files in {directory}")
    
    async def read_file(self, file_path):
        """Read and display file"""
        result = self.call_mcp_server("fs.read", {"path": file_path})
        
        if result.get('data'):
            print(f"\n📄 {file_path}:")
            print("-" * 50)
            print(result['data'])
            print("-" * 50)
        else:
            print(f"❌ Could not read {file_path}")
    
    async def create_file(self, file_path, content):
        """Create a new file"""
        result = self.call_mcp_server("fs.write", {"path": file_path, "data": content})
        
        if result.get('ok'):
            print(f"✅ Created {file_path}")
        else:
            print(f"❌ Failed to create {file_path}")
    
    async def analyze_codebase(self):
        """Analyze the codebase"""
        print("🔍 Analyzing codebase...")
        
        # Get file list
        files_result = self.call_mcp_server("fs.list", {"dir": "."})
        
        if not files_result:
            print("❌ Could not access files")
            return
        
        # Categorize files
        code_files = []
        config_files = []
        doc_files = []
        file_types = {}
        
        for item in files_result:
            if item['type'] == 'file':
                name = item['name']
                path = Path(name)
                ext = path.suffix.lower()
                
                # Count file types
                if ext:
                    file_types[ext] = file_types.get(ext, 0) + 1
                
                # Categorize files
                if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs', '.php', '.rb']:
                    code_files.append(name)
                elif name in ['README.md', 'CHANGELOG.md', 'LICENSE'] or ext in ['.md', '.txt']:
                    doc_files.append(name)
                elif name in ['package.json', 'requirements.txt', 'Cargo.toml', 'go.mod', 'setup.py', 'pyproject.toml', 'composer.json']:
                    config_files.append(name)
        
        if not code_files:
            print("❌ No code files found to analyze")
            return
        
        # Build comprehensive analysis prompt
        file_structure = f"Project contains: {len(code_files)} code files, {len(config_files)} config files, {len(doc_files)} documentation files"
        file_types_summary = ", ".join([f"{count} {ext} files" for ext, count in file_types.items() if count > 0])
        
        # Read key files for analysis
        key_files_content = ""
        key_files = (config_files + code_files)[:5]  # Analyze top 5 important files
        
        for file_path in key_files:
            file_data = self.call_mcp_server("fs.read", {"path": file_path})
            if file_data.get('data'):
                content = file_data['data']
                # Truncate very long files
                if len(content) > 3000:
                    content = content[:3000] + "\n... (truncated)"
                key_files_content += f"\n=== {file_path} ===\n{content}\n"
        
        analysis_prompt = f"""Please analyze this codebase comprehensively:

📊 PROJECT OVERVIEW:
{file_structure}
File types: {file_types_summary}
Key files analyzed: {', '.join(key_files)}

📁 FILE CONTENTS:
{key_files_content}

🎯 ANALYSIS REQUESTED:
Please provide a detailed analysis covering:

1. **🏗️ Project Architecture**: What type of application is this? What's the overall structure?

2. **⚙️ Technologies & Frameworks**: What programming languages, frameworks, and tools are being used?

3. **📦 Dependencies & Setup**: What are the main dependencies? How is the project configured?

4. **🔍 Code Quality**: Overall code quality assessment and any patterns observed

5. **🚀 Potential Improvements**: Suggestions for better structure, performance, or maintainability

6. **🛡️ Security & Best Practices**: Any security considerations or best practice recommendations

7. **📋 Next Steps**: What should a developer focus on next?

Provide actionable insights that would help a developer understand and improve this codebase."""
        
        # Use enhanced AI response
        await self.ask_ai(analysis_prompt)
    
    async def run_command(self, command):
        """Run shell command"""
        print(f"🔧 Running: {command}")
        
        result = self.call_mcp_server("shell.run", {"cmd": command, "cwd": self.workspace})
        
        if result.get('ok'):
            print(f"✅ Command completed (exit code: {result.get('code', 0)})")
        else:
            print(f"❌ Command failed (exit code: {result.get('code', 1)})")
    
    def show_help(self):
        """Show help"""
        print("""
💡 CodeDev Commands:

🚀 QUICK ACTIONS:
  analyze              - Deep analysis of your codebase
  files [dir]          - List files in directory
  read <file>          - Read and display file
  create <file>        - Create new file interactively
  run <command>        - Execute shell command

🤖 AI INTERACTIONS:
  ask <question>       - Ask AI anything about your code
  
🎯 SMART QUESTIONS TO TRY:
  ask "Review my code for security issues"
  ask "How can I optimize performance?"
  ask "Write unit tests for the main functions"
  ask "Explain the architecture of this project"
  ask "Find potential bugs in my code"
  ask "Suggest better design patterns"
  ask "Add error handling to this code"
  ask "How to deploy this application?"
  ask "Write documentation for this function"
  ask "Refactor this code to be more maintainable"

📋 INSTANT HELPERS:
  review               - Quick code review of current directory
  security             - Security vulnerability scan
  optimize             - Performance optimization suggestions
  test                 - Generate test suggestions
  deploy               - Deployment guidance
  docs                 - Documentation assistance

⚙️ SPECIAL COMMANDS:
  help                 - Show this help
  exit, quit           - Exit CodeDev
  clear                - Clear screen

💡 Pro Tips:
• Start with 'analyze' to understand your codebase
• Use specific questions for better AI responses
• AI understands your project context automatically
• All file operations create backups automatically

🔥 Advanced Features:
• Natural language processing for code queries
• Context-aware responses based on your project
• Multi-language support and framework detection
• Intelligent code suggestions and improvements
""")
    
    async def quick_review(self):
        """Quick code review"""
        await self.ask_ai("Please perform a quick code review of this project. Focus on code quality, potential issues, and improvement suggestions.")
    
    async def security_scan(self):
        """Security vulnerability scan"""
        await self.ask_ai("Please scan this codebase for potential security vulnerabilities, including common issues like SQL injection, XSS, insecure dependencies, and poor authentication/authorization patterns.")
    
    async def optimize_suggestions(self):
        """Performance optimization suggestions"""
        await self.ask_ai("Please analyze this codebase for performance optimization opportunities. Look for inefficient algorithms, database queries, memory usage, and suggest improvements.")
    
    async def test_suggestions(self):
        """Generate test suggestions"""
        await self.ask_ai("Please analyze this codebase and suggest a comprehensive testing strategy. Include unit tests, integration tests, and specific test cases for the main functions.")
    
    async def deploy_guidance(self):
        """Deployment guidance"""
        await self.ask_ai("Please provide deployment guidance for this project. Include setup instructions, environment configuration, dependencies, and best practices for production deployment.")
    
    async def docs_assistance(self):
        """Documentation assistance"""
        await self.ask_ai("Please help improve the documentation for this project. Suggest what documentation is missing, how to improve existing docs, and provide templates for API documentation or README improvements.")
    
    async def handle_input(self, user_input):
        """Handle user input"""
        parts = user_input.strip().split(' ', 1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if command in ['exit', 'quit']:
            self.running = False
            print("👋 Happy coding!")
            
        elif command == 'help':
            self.show_help()
            
        elif command == 'clear':
            os.system('clear' if os.name == 'posix' else 'cls')
            self.print_banner()
            
        elif command == 'analyze':
            await self.analyze_codebase()
            
        elif command == 'files':
            await self.list_files(args if args else ".")
            
        elif command == 'read':
            if args:
                await self.read_file(args)
            else:
                print("❌ Usage: read <file_path>")
                
        elif command == 'create':
            if args:
                print(f"Creating {args}...")
                print("Enter content (press Ctrl+D when done):")
                content_lines = []
                try:
                    while True:
                        line = input()
                        content_lines.append(line)
                except EOFError:
                    content = '\n'.join(content_lines)
                    await self.create_file(args, content)
            else:
                print("❌ Usage: create <file_path>")
                
        elif command == 'run':
            if args:
                await self.run_command(args)
            else:
                print("❌ Usage: run <command>")
                
        elif command == 'ask':
            if args:
                await self.ask_ai(args)
            else:
                print("❌ Usage: ask <question>")
        
        # Instant helper commands
        elif command == 'review':
            await self.quick_review()
        elif command == 'security':
            await self.security_scan()
        elif command == 'optimize':
            await self.optimize_suggestions()
        elif command == 'test':
            await self.test_suggestions()
        elif command == 'deploy':
            await self.deploy_guidance()
        elif command == 'docs':
            await self.docs_assistance()
                
        else:
            # Treat as AI question
            await self.ask_ai(user_input)
    
    async def run(self):
        """Main run loop"""
        self.print_banner()
        
        # Check setup
        setup_ok, setup_msg = self.check_setup()
        if not setup_ok:
            print(f"❌ Setup issue: {setup_msg}")
            print("\n🔧 Quick fix:")
            if "ollama serve" in setup_msg:
                print("  1. Install Ollama: https://ollama.ai")
                print("  2. Run: ollama serve")
                print("  3. Run: ollama pull deepseek-r1:8b")
            elif "httpx" in setup_msg:
                print("  Run: pip install httpx")
            
            choice = input("\nContinue anyway? (y/N): ").strip().lower()
            if choice not in ['y', 'yes']:
                return
        else:
            print("✅ Setup looks good!")
        
        print("\n💡 Try: 'analyze' to start, or 'help' for commands")
        
        self.running = True
        while self.running:
            try:
                user_input = input("\n🚀 codedev> ").strip()
                if user_input:
                    await self.handle_input(user_input)
                    
            except KeyboardInterrupt:
                print("\n👋 Happy coding!")
                break
            except EOFError:
                print("\n👋 Happy coding!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Entry point"""
    try:
        codedev = CodeDev()
        asyncio.run(codedev.run())
    except KeyboardInterrupt:
        print("\n👋 Happy coding!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    main()

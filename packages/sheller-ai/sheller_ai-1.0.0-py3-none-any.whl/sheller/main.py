"""
Main module for Sheller - AI-Powered Terminal Command Assistant
"""

import subprocess
import sys
import os
import asyncio
import threading
import time
from dotenv import load_dotenv
import google.generativeai as genai
from pydantic import BaseModel
load_dotenv()

# Check for API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("\033[38;5;196m❌ GEMINI_API_KEY not found!\033[0m")
    print("\033[38;5;214m📋 Setup Instructions:\033[0m")
    print("1. Get your API key from: https://makersuite.google.com/app/apikey")
    print("2. Set environment variable:")
    print("   Windows: setx GEMINI_API_KEY \"your_api_key_here\"")
    print("   macOS/Linux: export GEMINI_API_KEY=\"your_api_key_here\"")
    print("3. Or run: python setup_env.py")
    print("\033[38;5;208m⚠️  Natural language processing will be disabled.\033[0m")
    print("\033[38;5;240m" + "─" * 60 + "\033[0m")
    model = None
else:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        print("\033[38;5;46m✅ Gemini API configured successfully!\033[0m")
    except Exception as e:
        print(f"\033[38;5;196m❌ Error configuring Gemini API: {e}\033[0m")
        print("\033[38;5;208m⚠️  Natural language processing will be disabled.\033[0m")
        model = None

# For cross-platform keyboard input
try:
    import msvcrt  # Windows
    import platform
    IS_WINDOWS = platform.system() == "Windows"
except ImportError:
    IS_WINDOWS = False

command_prompt = """You are an command assistant agent that processes the user's input and returns a ready-to-execute command with placeholders if needed. 
    Use the context to determine the platform and shell to use. 
    
    IMPORTANT: Since this is running on Windows with CMD as the default shell, suggest Windows-appropriate commands:
    - Use 'dir' instead of 'ls'
    - Use 'tracert' instead of 'traceroute'
    - Use 'ipconfig' instead of 'ifconfig'
    - Use 'tasklist' instead of 'ps'
    - Use 'findstr' instead of 'grep'
    - Use 'type' instead of 'cat'
    - Use 'copy' instead of 'cp'
    - Use 'move' instead of 'mv'
    - Use 'del' instead of 'rm'
    
    For PowerShell-specific operations, use PowerShell cmdlets like Get-Process, Get-ChildItem, etc.
    
    Only return the command as command: <command> no other text."""

class CommandContext(BaseModel):
    platform: str = "windows"
    shell: str = "cmd"
    def __str__(self):
        return f"Platform: {self.platform}\nShell: {self.shell}"

class TerminalUI:
    def __init__(self):
        self.command_history = []
        self.history_index = 0
        self.current_input = ""
        self.suggested_command = ""
        self.is_processing = False
        self.ctx = CommandContext()
        self.ctx.shell = detect_subprocess_shell()
        
    def clear_line(self):
        """Clear the current line"""
        print("\r" + " " * 100 + "\r", end="", flush=True)
    
    def print_prompt(self, input_text="", show_suggestion=False):
        """Print the prompt with current input or suggestion"""
        self.clear_line()
        if show_suggestion and self.suggested_command:
            print(f"\r\033[38;5;226m🤖\033[0m \033[38;5;51m{self.suggested_command}\033[0m", end="", flush=True)
        else:
            print(f"\r\033[38;5;46m💻\033[0m \033[38;5;255m{input_text}\033[0m", end="", flush=True)
    
    def show_progress(self):
        """Show animated progress indicator"""
        chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while self.is_processing:
            self.clear_line()
            print(f"\r\033[38;5;226m{chars[i]}\033[0m \033[38;5;51mProcessing request...\033[0m", end="", flush=True)
            time.sleep(0.1)
            i = (i + 1) % len(chars)
    
    def get_input(self):
        """Get input with keyboard shortcuts"""
        if IS_WINDOWS:
            return self.get_input_windows()
        else:
            return self.get_input_unix()
    
    def get_input_windows(self):
        """Windows-specific input handling with keyboard shortcuts"""
        input_chars = []
        cursor_pos = 0
        
        while True:
            if msvcrt.kbhit():
                char = msvcrt.getch()
                
                # Handle special keys
                if char == b'\r':  # Enter
                    current_input = ''.join(input_chars)
                    # If there's a suggested command and no current input, use suggestion
                    if self.suggested_command and not current_input.strip():
                        return self.suggested_command
                    else:
                        # Execute current input (prioritize direct commands)
                        return current_input
                
                elif char == b'\x1b':  # Escape
                    next_char = msvcrt.getch()
                    if next_char == b'[':
                        arrow = msvcrt.getch()
                        if arrow == b'A':  # Up arrow - history
                            if self.command_history:
                                self.history_index = max(0, self.history_index - 1)
                                input_chars = list(self.command_history[self.history_index])
                                cursor_pos = len(input_chars)
                        elif arrow == b'B':  # Down arrow - history
                            if self.history_index < len(self.command_history) - 1:
                                self.history_index += 1
                                input_chars = list(self.command_history[self.history_index])
                                cursor_pos = len(input_chars)
                            else:
                                input_chars = []
                                cursor_pos = 0
                        elif arrow == b'C':  # Right arrow
                            cursor_pos = min(cursor_pos + 1, len(input_chars))
                        elif arrow == b'D':  # Left arrow
                            cursor_pos = max(cursor_pos - 1, 0)
                
                elif char == b'\x0b':  # Ctrl+K
                    current_input = ''.join(input_chars)
                    if current_input.strip():
                        return f"PROCESS:{current_input}"
                
                elif char == b'\x08':  # Backspace
                    if cursor_pos > 0:
                        input_chars.pop(cursor_pos - 1)
                        cursor_pos -= 1
                
                elif char == b'\x7f':  # Delete
                    if cursor_pos < len(input_chars):
                        input_chars.pop(cursor_pos)
                
                elif char in [b'\x03', b'\x04']:  # Ctrl+C or Ctrl+D
                    return "exit"
                
                else:
                    # Regular character
                    try:
                        char_str = char.decode('utf-8')
                        if char_str.isprintable():
                            input_chars.insert(cursor_pos, char_str)
                            cursor_pos += 1
                            # Clear suggested command when user starts typing
                            if self.suggested_command:
                                self.suggested_command = ""
                    except UnicodeDecodeError:
                        pass
                
                # Update display
                self.print_prompt(''.join(input_chars))
    
    def get_input_unix(self):
        """Unix-like input handling (fallback)"""
        try:
            return input("💻 ")
        except KeyboardInterrupt:
            return "exit"
    
    async def process_input(self, user_input):
        """Process user input and get command suggestion"""
        if model is None:
            self.suggested_command = "echo 'AI processing unavailable - please set GEMINI_API_KEY'"
            return
            
        self.is_processing = True
        
        # Start progress indicator in a separate thread
        progress_thread = threading.Thread(target=self.show_progress)
        progress_thread.daemon = True
        progress_thread.start()
        
        try:
            # Get command suggestion
            response = await model.generate_content_async(
                contents= command_prompt + "\n" + "Context: " + str(self.ctx) + "\n" + "User Input: " + user_input
            )
            suggestion = response.text
            
            # Extract command from suggestion
            if "command:" in suggestion:
                self.suggested_command = suggestion.split("command:", 1)[1].strip()
            else:
                self.suggested_command = suggestion.strip()
                
        except Exception as e:
            self.suggested_command = f"echo Error: {str(e)}"
        finally:
            self.is_processing = False
            time.sleep(0.1)  # Brief pause to show completion
    
    def execute_command(self, command):
        """Execute the command and display output"""
        if command.lower() == "exit":
            return False
        
        print(f"\n\033[38;5;226m🚀\033[0m \033[38;5;51mExecuting:\033[0m \033[38;5;255m{command}\033[0m")
        print("\033[38;5;240m" + "═" * 60 + "\033[0m")
        
        try:
            # Translate and execute
            translated_command = translate_unix_to_windows(command)
            
            # First try CMD
            result = subprocess.run(translated_command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                if result.stdout:
                    print("\033[38;5;46m" + result.stdout + "\033[0m")
                if result.stderr:
                    print("\033[38;5;208m" + result.stderr + "\033[0m", file=sys.stderr)
            else:
                # Try PowerShell if CMD fails
                print("\033[38;5;208m⚠️  CMD failed, trying PowerShell...\033[0m")
                try:
                    powershell_cmd = ["powershell", "-Command", translated_command]
                    result = subprocess.run(powershell_cmd, capture_output=True, text=True)
                    
                    if result.stdout:
                        print("\033[38;5;46m" + result.stdout + "\033[0m")
                    if result.stderr:
                        print("\033[38;5;208m" + result.stderr + "\033[0m", file=sys.stderr)
                except Exception as e:
                    print(f"\033[38;5;196m❌ PowerShell also failed: {e}\033[0m")
                    
        except Exception as e:
            print(f"\033[38;5;196m❌ Error executing command: {e}\033[0m")
        
        print("\033[38;5;240m" + "═" * 60 + "\033[0m")
        
        # Add to history
        if command not in self.command_history:
            self.command_history.append(command)
        self.history_index = len(self.command_history)
        
        return True
    
    async def run(self):
        """Main UI loop"""
        # Retro-style ASCII art banner
        print("\033[38;5;51m" + "=" * 80)
        print("""
 ███████╗██╗  ██╗███████╗██╗     ██╗     ███████╗██████╗ 
 ██╔════╝██║  ██║██╔════╝██║     ██║     ██╔════╝██╔══██╗
 ███████╗███████║█████╗  ██║     ██║     █████╗  ██████╔╝
 ╚════██║██╔══██║██╔══╝  ██║     ██║     ██╔══╝  ██╔══██╗
 ███████║██║  ██║███████╗███████╗███████╗███████╗██║  ██║
 ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝
        """)
        print("=" * 80 + "\033[0m")
        
        # Retro-style subtitle
        print("\033[38;5;226m╔══════════════════════════════════════════════════════════════════════════════╗")
        print("║                    🚀 AI-POWERED TERMINAL COMMAND ASSISTANT 🚀                    ║")
        print("║                        ⚡ Natural Language to Commands ⚡                        ║")
        print("╚══════════════════════════════════════════════════════════════════════════════╝\033[0m")
        
        # System info
        print(f"\033[38;5;46m📡 System: {self.ctx.platform.upper()} | Shell: {self.ctx.shell.upper()}\033[0m")
        print(f"\033[38;5;51m🕐 Started: {time.strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
        print()
        
        # Instructions with retro styling
        print("\033[38;5;214m╭─ COMMAND MODES ──────────────────────────────────────────────────────────────╮")
        print("│ 📝 Natural Language: Type your request and press \033[1mCtrl+K\033[0m\033[38;5;214m to process          │")
        print("│ ⚡ Direct Commands: Type commands directly and press \033[1mEnter\033[0m\033[38;5;214m to execute        │")
        print("│ 🔄 History: Use \033[1m↑/↓\033[0m\033[38;5;214m arrow keys to navigate command history              │")
        print("│ ❌ Exit: Press \033[1mCtrl+C\033[0m\033[38;5;214m or type 'exit' to quit                           │")
        print("╰─────────────────────────────────────────────────────────────────────────────────────╯\033[0m")
        print()
        
        # Status indicator
        print("\033[38;5;46m● Ready for commands...\033[0m")
        print("\033[38;5;240m" + "─" * 60 + "\033[0m")
        print()
        
        while True:
            try:
                # Get user input
                user_input = self.get_input()
                
                if user_input == "exit":
                    print("\n👋 Goodbye!")
                    break
                
                if user_input.startswith("PROCESS:"):
                    # Process natural language input
                    natural_input = user_input[8:]  # Remove "PROCESS:" prefix
                    await self.process_input(natural_input)
                    
                    # Show suggested command
                    self.print_prompt(show_suggestion=True)
                    print()  # New line after suggestion
                    
                else:
                    # Direct command execution
                    if not self.execute_command(user_input):
                        break
                        
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")

def translate_unix_to_windows(command):
    """
    Translate common Unix/Linux commands to Windows equivalents.
    """
    command_lower = command.lower().strip()
    
    # Common Unix to Windows command mappings
    translations = {
        'ls -a': 'dir /a',
        'ls -la': 'dir /a',
        'ls -l': 'dir',
        'ls': 'dir',
        'traceroute': 'tracert',
        'pwd': 'cd',
        'whoami': 'whoami',
        'ps aux': 'tasklist',
        'ps': 'tasklist',
        'kill': 'taskkill',
        'grep': 'findstr',
        'cat': 'type',
        'head': 'powershell -Command "Get-Content | Select-Object -First"',
        'tail': 'powershell -Command "Get-Content | Select-Object -Last"',
        'chmod': 'icacls',
        'chown': 'takeown',
        'cp': 'copy',
        'mv': 'move',
        'rm': 'del',
        'rmdir': 'rmdir',
        'mkdir': 'mkdir',
        'touch': 'powershell -Command "New-Item -ItemType File"',
        'df': 'powershell -Command "Get-WmiObject -Class Win32_LogicalDisk | Select-Object DeviceID,Size,FreeSpace"',
        'du': 'powershell -Command "Get-ChildItem -Recurse | Measure-Object -Property Length -Sum"',
        'top': 'powershell -Command "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10"',
        'netstat': 'netstat',
        'ifconfig': 'ipconfig',
        'ping': 'ping',
        'nslookup': 'nslookup',
        'dig': 'nslookup',
        'wget': 'powershell -Command "Invoke-WebRequest"',
        'curl': 'powershell -Command "Invoke-WebRequest"',
    }
    
    # Check for exact matches first
    for unix_cmd, windows_cmd in translations.items():
        if command_lower.startswith(unix_cmd):
            # Replace the Unix command with Windows equivalent
            return command.replace(command[:len(unix_cmd)], windows_cmd, 1)
    
    # Check for commands that need PowerShell equivalents
    if command_lower.startswith('ls '):
        # Convert ls with options to dir or Get-ChildItem
        if '-a' in command_lower or '-la' in command_lower:
            return 'dir /a'
        elif '-l' in command_lower:
            return 'dir'
        else:
            return 'dir'
    
    return command

def detect_subprocess_shell():
    """
    Detect what shell subprocess.run(shell=True) will use.
    This is different from detecting the current shell environment.
    """
    if os.name == "nt":
        # On Windows, subprocess.run(shell=True) uses COMSPEC environment variable
        comspec = os.environ.get("COMSPEC", "").lower()
        
        if "powershell" in comspec:
            return "powershell"
        elif "cmd" in comspec:
            return "cmd"
        else:
            # Default fallback
            return "cmd"
    elif os.name == "posix":
        # On Unix-like systems, subprocess.run(shell=True) uses /bin/sh
        return "sh"
    else:
        return "unknown"

async def main():
    """Main entry point"""
    ui = TerminalUI()
    await ui.run()

def main_sync():
    """Synchronous wrapper for the async main function"""
    asyncio.run(main())

if __name__ == "__main__":
    main_sync()

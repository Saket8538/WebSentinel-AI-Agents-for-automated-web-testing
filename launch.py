import subprocess
import sys
import socket
from pathlib import Path


def check_venv():
    """Check if virtual environment exists"""
    venv_path = Path(".venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("   Run: python -m venv .venv")
        print("   Then: .venv\\Scripts\\activate")
        print("   Then: pip install -r requirements.txt")
        return False
    return True


def kill_port(port):
    """Kill any process holding a given port (Windows only)."""
    if sys.platform != "win32":
        return
    try:
        result = subprocess.run(
            ["netstat", "-ano", "-p", "TCP"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.splitlines():
            if f":{port}" in line and "LISTENING" in line:
                parts = line.split()
                pid = parts[-1]
                if pid.isdigit() and int(pid) != 0:
                    subprocess.run(["taskkill", "/F", "/PID", pid],
                                   capture_output=True, timeout=10)
                    print(f"   ♻️  Freed port {port} (killed PID {pid})")
    except Exception:
        pass


def get_python_executable():
    """Get the Python executable path from venv"""
    if sys.platform == "win32":
        return Path(".venv") / "Scripts" / "python.exe"
    else:
        return Path(".venv") / "bin" / "python"


def launch_web_interface():
    """Launch Gradio Web Interface"""
    python = get_python_executable()
    print("\n🚀 Launching Gradio Web Interface...")
    kill_port(7860)
    print("   URL will be displayed below")
    subprocess.run([str(python), "interfaces/web_interface.py"])


def launch_streamlit_interface():
    """Launch Streamlit Interface"""
    python = get_python_executable()
    print("\n🚀 Launching Streamlit Interface...")
    kill_port(8501)
    print("   URL: http://localhost:8501")
    subprocess.run([str(python), "-m", "streamlit", "run", "interfaces/streamlit_interface.py"])


def launch_cli():
    """Launch CLI Interface"""
    python = get_python_executable()
    print("\n🚀 Launching CLI Interface...")
    print("   Usage: test <url> [--task 'description'] [--no-headless]")
    url = input("   Enter URL to test (or press Enter for help): ").strip()
    if url:
        task = input("   Enter AI task (optional, press Enter to skip): ").strip()
        cmd = [str(python), "interfaces/cli.py", "test", url]
        if task:
            cmd.extend(["--task", task])
        subprocess.run(cmd)
    else:
        subprocess.run([str(python), "interfaces/cli.py", "--help"])


def launch_api_server():
    """Launch FastAPI Server"""
    python = get_python_executable()
    print("\n🚀 Launching API Server...")
    kill_port(8000)
    print("   API Docs: http://localhost:8000/docs")
    subprocess.run([str(python), "interfaces/api_server.py"])


def launch_interactive_agent():
    """Launch Interactive Terminal Agent"""
    python = get_python_executable()
    print("\n🚀 Launching Interactive Agent...")
    subprocess.run([str(python), "interfaces/interactive_agent.py"])


def show_menu():
    """Display main menu"""
    print("\n" + "="*70)
    print("  🛡️  WebSentinel - AI-Powered Web Testing Platform")
    print("="*70)
    print("\n📦 Interfaces:")
    print("  1. Gradio Web Interface (Recommended) - Full visual UI")
    print("  2. Streamlit Interface - Alternative visual UI")
    print("  3. CLI Interface - Command line testing")
    print("  4. FastAPI Server - REST API for integrations")
    print("  5. Interactive Terminal Agent - AI chat interface")
    print("\n  0. Exit")
    print("\n" + "-"*70)
    print("✨ Features: Security Scanning | Accessibility Audit | Performance Analysis")
    print("             AI Insights | Visual Regression | SEO Analysis")
    print("="*70)


def main():
    """Main launcher"""
    # Check virtual environment
    if not check_venv():
        sys.exit(1)

    while True:
        show_menu()
        choice = input("\nEnter choice (0-5): ").strip()

        if choice == "1":
            launch_web_interface()
        elif choice == "2":
            launch_streamlit_interface()
        elif choice == "3":
            launch_cli()
        elif choice == "4":
            launch_api_server()
        elif choice == "5":
            launch_interactive_agent()
        elif choice == "0":
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice. Please try again.")

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)

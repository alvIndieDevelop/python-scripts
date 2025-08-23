#!/usr/bin/env python3

"""
Developer Environment Setup Script for Arch Linux
Automated installation of development tools and packages
Part of Python Scripts Collection
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from datetime import datetime
import shutil
import stat


def show_startup_banner():
    """Display an attractive startup banner"""
    print("╔══════════════════════════════════════════════════════════════════════════════╗")
    print("║                    🚀 DEVELOPER ENVIRONMENT SETUP                           ║")
    print("║                     Professional Development Tools Installer                ║")
    print("║                              Version 1.0                                   ║")
    print("║                    Part of Python Scripts Collection                       ║")
    print("╚══════════════════════════════════════════════════════════════════════════════╝")
    print()
    print("🔧 Complete development environment setup for Arch Linux")
    print("📦 Node.js, Python, Docker, VSCode, Git, and more")
    print("🛡️  Safe, secure, and user-friendly installation")
    print("🏠 Repository: https://github.com/alvIndieDevelop/python-scripts")
    print("=" * 80)
    print()


def clear_screen():
    """Clear the terminal screen"""
    os.system('clear' if os.name == 'posix' else 'cls')


def check_sudo():
    """Check if the script is running with sudo privileges"""
    if os.geteuid() != 0:
        print("❌ This script requires sudo privileges to install packages.")
        print("💡 Please run: sudo python3 developer_enviroment.py")
        sys.exit(1)


def check_arch_linux():
    """Check if the system is running Arch Linux"""
    try:
        with open('/etc/os-release', 'r') as f:
            content = f.read()
            if 'arch' not in content.lower():
                print("⚠️  This script is designed for Arch Linux.")
                print("💡 Some packages may not be available on other distributions.")
                input("Press Enter to continue anyway...")
    except FileNotFoundError:
        print("⚠️  Could not determine OS. Continuing anyway...")


class DeveloperEnvironment:
    def __init__(self):
        self.home_dir = Path.home()
        self.log_file = self.home_dir / ".dev_env_setup.log"
        self.installed_packages = set()
        self.failed_packages = set()
        
        # Development tools configuration
        self.tools = {
            'nvm': {
                'name': 'NVM (Node Version Manager)',
                'description': 'Node.js version manager for easy Node.js installation',
                'package': 'nvm',
                'aur': True,
                'post_install': self._setup_nvm
            },
            'nodejs': {
                'name': 'Node.js',
                'description': 'JavaScript runtime for server-side development',
                'package': 'nodejs',
                'aur': False,
                'post_install': None
            },
            'vscode': {
                'name': 'Visual Studio Code',
                'description': 'Powerful code editor with extensive extensions',
                'package': 'code',
                'aur': False,
                'post_install': None
            },
            'docker': {
                'name': 'Docker',
                'description': 'Container platform for application deployment',
                'package': 'docker',
                'aur': False,
                'post_install': self._setup_docker
            },
            'git': {
                'name': 'Git',
                'description': 'Distributed version control system',
                'package': 'git',
                'aur': False,
                'post_install': None
            },
            'python': {
                'name': 'Python',
                'description': 'Python programming language and tools',
                'package': 'python',
                'aur': False,
                'post_install': None
            },
            'uv': {
                'name': 'UV (Python Package Manager)',
                'description': 'Fast Python package installer and resolver',
                'package': 'uv',
                'aur': False,
                'post_install': None
            },
            'postgresql': {
                'name': 'PostgreSQL',
                'description': 'Advanced open source database',
                'package': 'postgresql',
                'aur': False,
                'post_install': self._setup_postgresql
            },
            'redis': {
                'name': 'Redis',
                'description': 'In-memory data structure store',
                'package': 'redis',
                'aur': False,
                'post_install': None
            },
            'mongodb': {
                'name': 'MongoDB',
                'description': 'Document-oriented NoSQL database',
                'package': 'mongodb',
                'aur': False,
                'post_install': self._setup_mongodb
            }
        }

    def log_action(self, action, success=True, details=""):
        """Log the action to the log file with timestamp and success status"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        log_entry = f"{timestamp} - {action} - {status}"
        if details:
            log_entry += f" - {details}"
        
        with open(self.log_file, "a") as f:
            f.write(log_entry + "\n")

    def run_command(self, command, description=None):
        """Run a command and handle errors with safety checks"""
        if description:
            print(f"🔄 {description}...")
        
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                check=True
            )
            if description:
                print(f"✅ {description} completed successfully")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            if description:
                print(f"❌ {description} failed: {e}")
                if e.stderr:
                    print(f"   Error details: {e.stderr}")
            return False, e.stderr
        except Exception as e:
            if description:
                print(f"❌ Unexpected error during {description}: {e}")
            return False, str(e)

    def check_package_installed(self, package_name):
        """Check if a package is already installed"""
        try:
            result = subprocess.run(
                f"pacman -Q {package_name}",
                shell=True,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except:
            return False

    def install_package(self, tool_key):
        """Install a specific development tool"""
        if tool_key not in self.tools:
            print(f"❌ Unknown tool: {tool_key}")
            return False
        
        tool = self.tools[tool_key]
        package_name = tool['package']
        
        # Check if already installed
        if self.check_package_installed(package_name):
            print(f"ℹ️  {tool['name']} is already installed")
            self.installed_packages.add(tool_key)
            return True
        
        print(f"📦 Installing {tool['name']}...")
        
        # Install package
        if tool['aur']:
            success, output = self.run_command(
                f"yay -S --noconfirm {package_name}",
                f"Installing {tool['name']} from AUR"
            )
        else:
            success, output = self.run_command(
                f"pacman -S --noconfirm {package_name}",
                f"Installing {tool['name']} from official repositories"
            )
        
        if success:
            self.installed_packages.add(tool_key)
            self.log_action(f"Install {tool['name']}", True)
            
            # Run post-install setup if available
            if tool['post_install']:
                print(f"🔧 Running post-install setup for {tool['name']}...")
                try:
                    tool['post_install']()
                except Exception as e:
                    print(f"⚠️  Post-install setup failed: {e}")
                    self.log_action(f"Post-install setup {tool['name']}", False, str(e))
            
            return True
        else:
            self.failed_packages.add(tool_key)
            self.log_action(f"Install {tool['name']}", False, output)
            return False

    def install_all(self):
        """Install all development tools"""
        print("🚀 Installing all development tools...")
        print("=" * 50)
        
        total_tools = len(self.tools)
        successful_installs = 0
        
        for tool_key in self.tools:
            if self.install_package(tool_key):
                successful_installs += 1
            print()
        
        # Show summary
        self.show_installation_summary(successful_installs, total_tools)

    def show_installation_summary(self, successful, total):
        """Display installation summary"""
        print("=" * 50)
        print("📊 Installation Summary")
        print("=" * 50)
        print(f"✅ Successfully installed: {successful}/{total}")
        print(f"❌ Failed installations: {len(self.failed_packages)}")
        
        if self.failed_packages:
            print("\n❌ Failed packages:")
            for tool_key in self.failed_packages:
                tool = self.tools[tool_key]
                print(f"   - {tool['name']}")
        
        if successful == total:
            print("\n🎉 All tools installed successfully!")
        elif successful > 0:
            print(f"\n⚠️  {successful} out of {total} tools installed successfully.")
        else:
            print("\n❌ No tools were installed successfully.")
        
        print(f"\n📝 Check the log file for details: {self.log_file}")

    def _setup_nvm(self):
        """Setup NVM after installation"""
        print("🔧 Setting up NVM...")
        
        # Source NVM in current shell
        nvm_dir = self.home_dir / ".nvm"
        if nvm_dir.exists():
            # Install latest LTS Node.js
            success, _ = self.run_command(
                "source ~/.nvm/nvm.sh && nvm install --lts",
                "Installing latest LTS Node.js"
            )
            if success:
                print("✅ Node.js LTS installed via NVM")
            else:
                print("⚠️  Could not install Node.js LTS")

    def _setup_docker(self):
        """Setup Docker after installation"""
        print("🔧 Setting up Docker...")
        
        # Start and enable Docker service
        success, _ = self.run_command(
            "systemctl enable --now docker",
            "Enabling Docker service"
        )
        
        if success:
            # Add user to docker group
            username = os.getenv('USER')
            if username:
                self.run_command(
                    f"usermod -aG docker {username}",
                    f"Adding {username} to docker group"
                )
                print("💡 You may need to log out and back in for Docker group changes to take effect")

    def _setup_postgresql(self):
        """Setup PostgreSQL after installation"""
        print("🔧 Setting up PostgreSQL...")
        
        # Initialize database
        success, _ = self.run_command(
            "sudo -u postgres initdb -D /var/lib/postgres/data",
            "Initializing PostgreSQL database"
        )
        
        if success:
            # Start and enable service
            self.run_command(
                "systemctl enable --now postgresql",
                "Enabling PostgreSQL service"
            )
            print("💡 PostgreSQL is now running. Use 'sudo -u postgres psql' to connect")

    def _setup_mongodb(self):
        """Setup MongoDB after installation"""
        print("🔧 Setting up MongoDB...")
        
        # Create data directory
        data_dir = Path("/var/lib/mongodb")
        if not data_dir.exists():
            self.run_command(
                "mkdir -p /var/lib/mongodb",
                "Creating MongoDB data directory"
            )
        
        # Start and enable service
        self.run_command(
            "systemctl enable --now mongodb",
            "Enabling MongoDB service"
        )

    def show_available_tools(self):
        """Display all available development tools"""
        print("🛠️  Available Development Tools")
        print("=" * 60)
        
        for i, (tool_key, tool) in enumerate(self.tools.items(), 1):
            status = "✅ Installed" if tool_key in self.installed_packages else "📦 Available"
            print(f"{i:2d}. {tool['name']}")
            print(f"    {tool['description']}")
            print(f"    Status: {status}")
            print()

    def show_menu(self):
        """Display the interactive menu"""
        print("🔧 Developer Environment Setup Menu")
        print("=" * 50)
        print("1.  📦 Install NVM (Node Version Manager)")
        print("2.  🟢 Install Node.js")
        print("3.  💻 Install Visual Studio Code")
        print("4.  🐳 Install Docker")
        print("5.  📝 Install Git")
        print("6.  🐍 Install Python")
        print("7.  ⚡ Install UV (Python Package Manager)")
        print("8.  🐘 Install PostgreSQL")
        print("9.  🔴 Install Redis")
        print("10. 🍃 Install MongoDB")
        print("11. 🚀 Install All Tools")
        print("12. 📋 Show Available Tools")
        print("13. 📊 Show Installation Status")
        print("14. 📝 View Installation Log")
        print("0.  🚪 Exit")
        print("=" * 50)

    def get_user_choice(self):
        """Get user choice from menu"""
        while True:
            try:
                choice = input("🔧 Enter your choice (0-14): ").strip()
                if choice == "0":
                    return 0
                choice_num = int(choice)
                if 1 <= choice_num <= 14:
                    return choice_num
                else:
                    print("❌ Please enter a number between 0 and 14")
            except ValueError:
                print("❌ Please enter a valid number")

    def execute_choice(self, choice):
        """Execute the user's choice"""
        tool_mapping = {
            1: 'nvm',
            2: 'nodejs',
            3: 'vscode',
            4: 'docker',
            5: 'git',
            6: 'python',
            7: 'uv',
            8: 'postgresql',
            9: 'redis',
            10: 'mongodb'
        }
        
        if choice in tool_mapping:
            tool_key = tool_mapping[choice]
            self.install_package(tool_key)
        elif choice == 11:
            self.install_all()
        elif choice == 12:
            self.show_available_tools()
        elif choice == 13:
            self.show_installation_status()
        elif choice == 14:
            self.show_installation_log()

    def show_installation_status(self):
        """Show current installation status"""
        print("📊 Installation Status")
        print("=" * 40)
        
        for tool_key, tool in self.tools.items():
            status = "✅ Installed" if tool_key in self.installed_packages else "📦 Not Installed"
            print(f"{tool['name']}: {status}")
        
        print(f"\n📈 Progress: {len(self.installed_packages)}/{len(self.tools)} tools installed")

    def show_installation_log(self):
        """Show recent installation log entries"""
        print("📝 Recent Installation Log")
        print("=" * 40)
        
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"Last {min(10, len(lines))} log entries:")
                        for line in lines[-10:]:
                            print(f"   {line.strip()}")
                    else:
                        print("No log entries found")
            except Exception as e:
                print(f"❌ Error reading log file: {e}")
        else:
            print("No log file found yet")


def main():
    """Main function to run the developer environment setup script"""
    parser = argparse.ArgumentParser(
        description="🚀 Developer Environment Setup Script - Install development tools on Arch Linux",
        epilog="💡 Use --all to install all tools or run interactively for selective installation.\n🏠 Part of Python Scripts Collection: https://github.com/alvIndieDevelop/python-scripts",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--all", 
        action="store_true", 
        help="🚀 Install all development tools automatically"
    )
    
    parser.add_argument(
        "--list", 
        action="store_true", 
        help="📋 List all available development tools"
    )
    
    parser.add_argument(
        "--status", 
        action="store_true", 
        help="📊 Show current installation status"
    )
    
    parser.add_argument(
        "--log", 
        action="store_true", 
        help="📝 Show installation log"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="Developer Environment Setup Script v1.0 - Part of Python Scripts Collection"
    )
    
    args = parser.parse_args()
    
    # Check system requirements
    check_sudo()
    check_arch_linux()
    
    # Create developer environment instance
    try:
        dev_env = DeveloperEnvironment()
    except Exception as e:
        print(f"❌ Failed to initialize developer environment: {e}")
        sys.exit(1)
    
    # Handle command line arguments
    if args.all:
        dev_env.install_all()
        return
    elif args.list:
        dev_env.show_available_tools()
        return
    elif args.status:
        dev_env.show_installation_status()
        return
    elif args.log:
        dev_env.show_installation_log()
        return
    
    # Interactive menu
    while True:
        clear_screen()
        show_startup_banner()
        dev_env.show_menu()
        
        choice = dev_env.get_user_choice()
        
        if choice == 0:
            print("👋 Thank you for using Developer Environment Setup!")
            print("💡 Your development environment is ready!")
            break
        
        clear_screen()
        dev_env.show_menu()
        print(f"🔄 Executing option {choice}...")
        print("=" * 50)
        
        try:
            dev_env.execute_choice(choice)
        except KeyboardInterrupt:
            print("\n⚠️  Operation interrupted by user")
        except Exception as e:
            print(f"\n❌ Error during operation: {e}")
        
        input("\n⏸️  Press Enter to continue...")


if __name__ == "__main__":
    main()
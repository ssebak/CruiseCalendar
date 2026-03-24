#!/usr/bin/env python3
"""
Cruise Calendar Deployment Script
Copies files to Apache cgi-bin directory with custom path support
"""

import os
import shutil
import sys
from pathlib import Path


def get_target_directory():
    """Prompt user for target deployment directory"""
    
    print("=" * 70)
    print("CRUISE CALENDAR - DEPLOYMENT TO APACHE")
    print("=" * 70)
    print()
    
    print("DEPLOYMENT LOCATIONS:\n")
    print("Option 1: Apache cgi-bin directory (standard CGI)")
    print("Option 2: Custom web folder (e.g., /boh/www/reports)")
    print()
    
    choice = input("Choose deployment location (1 or 2): ").strip()
    
    if choice == '1':
        return get_cgi_bin_directory()
    elif choice == '2':
        return get_custom_web_directory()
    else:
        print("❌ Invalid choice. Using cgi-bin.")
        return get_cgi_bin_directory()


def get_cgi_bin_directory():
    """Prompt user for Apache cgi-bin directory path"""
    
    # Suggest common paths
    if sys.platform == 'win32':
        suggested_paths = [
            r'C:\Apache24\cgi-bin',
            r'C:\Program Files\Apache\Apache24\cgi-bin',
            r'C:\Program Files (x86)\Apache\Apache24\cgi-bin',
        ]
        print("Common Apache cgi-bin paths on Windows:")
    else:
        suggested_paths = [
            '/usr/lib/cgi-bin',
            '/var/www/cgi-bin',
            '/usr/local/apache/cgi-bin',
        ]
        print("Common Apache cgi-bin paths on Linux:")
    
    for i, path in enumerate(suggested_paths, 1):
        print(f"  {i}. {path}")
    print()
    
    while True:
        user_input = input("Enter Apache cgi-bin directory path (or number 1-3): ").strip()
        
        # Check if user entered a number
        if user_input.isdigit() and 1 <= int(user_input) <= len(suggested_paths):
            cgi_bin_path = suggested_paths[int(user_input) - 1]
        else:
            cgi_bin_path = user_input
        
        # Validate the path
        if not cgi_bin_path:
            print("❌ Invalid path. Please try again.")
            continue
        
        cgi_bin_path = os.path.expanduser(cgi_bin_path)
        
        if os.path.isdir(cgi_bin_path):
            print(f"\n✓ Using directory: {cgi_bin_path}")
            return cgi_bin_path
        else:
            response = input(f"\n⚠ Directory does not exist: {cgi_bin_path}\n   Create it? (y/n): ").strip().lower()
            if response == 'y':
                try:
                    os.makedirs(cgi_bin_path, exist_ok=True)
                    print(f"✓ Created directory: {cgi_bin_path}")
                    return cgi_bin_path
                except Exception as e:
                    print(f"❌ Failed to create directory: {str(e)}")
                    continue
            else:
                continue

    """Get custom web directory from user"""
    
    print("\nENTER CUSTOM WEB DIRECTORY")
    print("This is where your web application will be deployed")
    print("(e.g., /boh/www/reports or /var/www/html/cruise-calendar)")
    print()
    
    while True:
        user_path = input("Enter your web directory path: ").strip()
        
        if not user_path:
            print("❌ Invalid path. Please try again.")
            continue
        
        user_path = os.path.expanduser(user_path)
        
        if os.path.isdir(user_path):
            print(f"\n✓ Using directory: {user_path}")
            return user_path
        else:
            response = input(f"\n⚠ Directory does not exist: {user_path}\n   Create it? (y/n): ").strip().lower()
            if response == 'y':
                try:
                    os.makedirs(user_path, exist_ok=True)
                    print(f"✓ Created directory: {user_path}")
                    return user_path
                except Exception as e:
                    print(f"❌ Failed to create directory: {str(e)}")
                    continue
            else:
                continue



def update_calendar_cgi(target_path):
    """Update calendar.cgi with correct path to deployment directory"""
    
    cgi_file = os.path.join(os.path.dirname(__file__), 'calendar.cgi')
    
    # Read the file
    with open(cgi_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the placeholder path
    original_line = "sys.path.insert(0, '/path/to/cgi-bin')"
    new_line = f"sys.path.insert(0, {repr(target_path)})"
    
    updated_content = content.replace(original_line, new_line)
    
    if updated_content == content:
        print("⚠ Warning: Could not find path placeholder in calendar.cgi")
        print("  Make sure the line contains: sys.path.insert(0, '/path/to/cgi-bin')")
    
    return updated_content


def deploy_files(target_path):
    """Copy all necessary files to target directory"""
    
    source_dir = os.path.dirname(__file__)
    files_to_copy = [
        'calendar.cgi',
        'calendar_manager.py',
        'portcall_fetcher.py',
    ]
    
    print("\nDeploying files...")
    print("-" * 70)
    
    # Update calendar.cgi with correct path
    updated_cgi_content = update_calendar_cgi(target_path)
    
    try:
        # Copy calendar.cgi with updated path
        cgi_dest = os.path.join(target_path, 'calendar.cgi')
        with open(cgi_dest, 'w', encoding='utf-8') as f:
            f.write(updated_cgi_content)
        print(f"✓ Deployed: calendar.cgi → {cgi_dest}")
        
        # Make calendar.cgi executable on Unix-like systems
        if sys.platform != 'win32':
            os.chmod(cgi_dest, 0o755)
            print(f"  ✓ Made executable (chmod +x)")
        
        # Copy other files
        for file in files_to_copy[1:]:
            src = os.path.join(source_dir, file)
            dst = os.path.join(target_path, file)
            shutil.copy2(src, dst)
            print(f"✓ Deployed: {file} → {dst}")
            
            # Make Python files executable on Unix-like systems
            if sys.platform != 'win32':
                os.chmod(dst, 0o755)
    
    except Exception as e:
        print(f"❌ Deployment failed: {str(e)}")
        return False
    
    return True


def print_next_steps(target_path):
    """Print next steps for the user based on deployment type"""
    
    print("\n" + "=" * 70)
    print("DEPLOYMENT COMPLETE ✓")
    print("=" * 70)
    print()
    print("Deployed to:", target_path)
    print()
    
    # Determine deployment type
    is_cgi_bin = 'cgi-bin' in target_path.lower()
    
    print("Next Steps:")
    print()
    
    if is_cgi_bin:
        print("1. VERIFY APACHE CONFIGURATION (cgi-bin)")
        print("   CGI should already be enabled for cgi-bin directories")
        print()
        print("2. RESTART APACHE")
        if sys.platform == 'win32':
            print("   Windows: Services → Apache24 → Restart")
        else:
            print("   Linux: sudo systemctl restart apache2")
        print()
        print("3. ACCESS THE CALENDAR")
        print("   http://localhost/cgi-bin/calendar.cgi")
        print("   or")
        print("   http://your-server/cgi-bin/calendar.cgi")
    
    else:
        print("1. CONFIGURE APACHE FOR CGI IN YOUR WEB DIRECTORY")
        print()
        
        if sys.platform == 'win32':
            print("   Add to httpd.conf:")
            print(f'   <Directory "{target_path}">')
            print('       AllowOverride None')
            print('       Options +ExecCGI')
            print('       AddHandler cgi-script .cgi')
            print('       Require all granted')
            print('   </Directory>')
        else:
            print("   Add to Apache configuration (e.g., /etc/apache2/sites-enabled/000-default.conf):")
            print(f'   <Directory "{target_path}">')
            print('       AllowOverride None')
            print('       Options +ExecCGI')
            print('       AddHandler cgi-script .cgi')
            print('       Require all granted')
            print('   </Directory>')
        
        print()
        print("2. RESTART APACHE")
        if sys.platform == 'win32':
            print("   Windows: Services → Apache24 → Restart")
        else:
            print("   Linux: sudo systemctl restart apache2")
        print()
        print("3. ACCESS THE CALENDAR")
        print(f"   http://localhost/boh/www/reports/calendar.cgi")
        print("   or based on your Apache DocumentRoot")
    
    print()
    print("4. TROUBLESHOOTING")
    print("   - Check if the calendar loads at all")
    print("   - Check Apache error log:")
    if sys.platform == 'win32':
        print("     C:\\Apache24\\logs\\error.log")
    else:
        print("     /var/log/apache2/error.log")
    print()
    print("   - Common issues:")
    print("     • 500 Internal Server Error = CGI not enabled")
    print("     • 404 Not Found = File not deployed correctly")
    print("     • Database import error = Path to includes/ incorrect")
    print()



def main():
    """Main deployment flow"""
    
    try:
        # Get target directory from user
        target_path = get_target_directory()
        print()
        
        # Deploy files
        if deploy_files(target_path):
            print_next_steps(target_path)
            return 0
        else:
            return 1
    
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

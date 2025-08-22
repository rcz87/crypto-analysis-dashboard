#!/usr/bin/env python3

"""
Debug script to check database configuration
"""

import os
import sys
from pathlib import Path

def check_database_config():
    print("🔍 DATABASE CONFIGURATION DEBUG")
    print("=" * 40)
    
    # Check environment variables
    print("\n1. ENVIRONMENT VARIABLES:")
    print("-" * 25)
    
    db_vars = [
        'DATABASE_URL',
        'SQLALCHEMY_DATABASE_URI', 
        'POSTGRES_URL',
        'DB_URL',
        'NEON_DATABASE_URL'
    ]
    
    for var in db_vars:
        value = os.environ.get(var)
        if value:
            # Hide password for security
            safe_value = value[:50] + "..." if len(value) > 50 else value
            if "localhost:5432" in value:
                print(f"❌ {var}={safe_value} (PROBLEM: localhost:5432)")
            elif "neon.tech" in value:
                print(f"✅ {var}={safe_value} (CORRECT: Neon database)")
            else:
                print(f"⚠️  {var}={safe_value}")
        else:
            print(f"❌ {var}=<not set>")
    
    # Check configuration files
    print("\n2. CONFIGURATION FILES:")
    print("-" * 23)
    
    config_files = [
        '.env',
        '.env.production',
        '.env.local',
        'config.py',
        'app.py'
    ]
    
    for file_path in config_files:
        if Path(file_path).exists():
            print(f"\n📄 {file_path}:")
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Look for database URLs
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if any(keyword in line.upper() for keyword in ['DATABASE_URL', 'SQLALCHEMY_DATABASE_URI']):
                        if "localhost:5432" in line:
                            print(f"   Line {i}: ❌ {line.strip()} (PROBLEM)")
                        elif "neon.tech" in line:
                            print(f"   Line {i}: ✅ {line.strip()[:60]}...")
                        else:
                            print(f"   Line {i}: ⚠️  {line.strip()[:60]}...")
                            
                if "localhost:5432" not in content:
                    print("   ✅ No localhost:5432 found")
                    
            except Exception as e:
                print(f"   ❌ Error reading file: {e}")
        else:
            print(f"❌ {file_path}: File not found")
    
    # Check Flask app configuration
    print("\n3. FLASK APP CONFIGURATION:")
    print("-" * 27)
    
    try:
        # Import app to check its configuration
        sys.path.insert(0, '.')
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
            if db_uri:
                safe_uri = db_uri[:50] + "..." if len(db_uri) > 50 else db_uri
                if "localhost:5432" in db_uri:
                    print(f"❌ Flask app DATABASE_URI: {safe_uri} (PROBLEM)")
                elif "neon.tech" in db_uri:
                    print(f"✅ Flask app DATABASE_URI: {safe_uri} (CORRECT)")
                else:
                    print(f"⚠️  Flask app DATABASE_URI: {safe_uri}")
            else:
                print("❌ Flask app DATABASE_URI: Not configured")
                
            # Check other related config
            other_configs = ['DATABASE_URL', 'SQLALCHEMY_ENGINE_OPTIONS']
            for config_key in other_configs:
                value = app.config.get(config_key)
                if value:
                    print(f"ℹ️  {config_key}: {str(value)[:50]}...")
                    
    except Exception as e:
        print(f"❌ Error checking Flask app: {e}")
    
    # Provide solution
    print("\n4. SOLUTION:")
    print("-" * 9)
    
    # Check if we have any localhost:5432 references
    has_localhost = False
    
    # Check environment
    for var in db_vars:
        value = os.environ.get(var, '')
        if "localhost:5432" in value:
            has_localhost = True
            print(f"🔧 Fix environment variable {var}")
    
    if has_localhost:
        print("\n📋 RECOMMENDED ACTIONS:")
        print("1. Update environment variables to use Neon database URL")
        print("2. Restart the application after making changes")
        print("3. Verify with health check endpoint")
    else:
        print("✅ No localhost:5432 found in current configuration")
        print("The issue might be in cached environment or running process")

if __name__ == "__main__":
    check_database_config()
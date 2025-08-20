#!/usr/bin/env python3
"""
Automatic Blueprint Discovery System
Scans all API files and discovers blueprint definitions automatically
"""

import os
import ast
import importlib.util
from typing import List, Tuple, Dict

def discover_blueprints() -> List[Tuple[str, str, str]]:
    """
    Discover all blueprints in the codebase automatically
    
    Returns:
        List of tuples: (import_path, blueprint_name, suggested_prefix)
    """
    
    blueprint_discoveries = []
    
    # Scan ./api/ directory
    api_files = []
    if os.path.exists('./api'):
        for file in os.listdir('./api'):
            if file.endswith('.py') and file != '__init__.py':
                api_files.append(f"./api/{file}")
    
    # Scan root directory for additional blueprint files
    root_files = []
    for file in os.listdir('.'):
        if file.endswith('.py') and any(keyword in file.lower() for keyword in ['routes', 'api', 'endpoints']):
            if file not in ['app.py', 'main.py', 'routes.py']:
                root_files.append(f"./{file}")
    
    all_files = api_files + root_files
    
    print(f"🔍 Scanning {len(all_files)} potential blueprint files...")
    
    for filepath in all_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Skip if no Blueprint import
            if 'Blueprint' not in content or 'from flask' not in content:
                continue
                
            # Try to parse the file to find Blueprint definitions
            try:
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                # Check if this is a Blueprint assignment
                                if isinstance(node.value, ast.Call):
                                    if (hasattr(node.value.func, 'id') and node.value.func.id == 'Blueprint') or \
                                       (hasattr(node.value.func, 'attr') and node.value.func.attr == 'Blueprint'):
                                        
                                        blueprint_name = target.id
                                        
                                        # Convert file path to import path
                                        if filepath.startswith('./api/'):
                                            import_path = f"api.{filepath[6:-3]}"  # Remove ./api/ and .py
                                        elif filepath.startswith('./'):
                                            import_path = filepath[2:-3]  # Remove ./ and .py
                                        else:
                                            import_path = filepath[:-3]
                                        
                                        # Suggest URL prefix based on file name
                                        base_name = os.path.basename(filepath)[:-3]  # Remove .py
                                        
                                        if 'gpts' in base_name.lower():
                                            prefix = '/api/gpts'
                                        elif 'smc' in base_name.lower():
                                            prefix = '/api/smc'
                                        elif 'signal' in base_name.lower():
                                            prefix = '/api/signals'
                                        elif 'ai' in base_name.lower() or 'reasoning' in base_name.lower():
                                            prefix = '/api/ai'
                                        elif 'news' in base_name.lower():
                                            prefix = '/api/news'
                                        elif 'telegram' in base_name.lower():
                                            prefix = '/api/telegram'
                                        elif 'webhook' in base_name.lower():
                                            prefix = '/api/webhook'
                                        elif 'performance' in base_name.lower():
                                            prefix = '/api/performance'
                                        elif 'security' in base_name.lower():
                                            prefix = '/api/security'
                                        elif 'chart' in base_name.lower():
                                            prefix = '/api/charts'
                                        elif 'backtest' in base_name.lower():
                                            prefix = '/api/backtest'
                                        elif 'coinglass' in base_name.lower():
                                            prefix = '/api/coinglass'
                                        elif 'institutional' in base_name.lower():
                                            prefix = '/api/institutional'
                                        else:
                                            # Generate prefix from filename
                                            clean_name = base_name.replace('_endpoints', '').replace('_api', '').replace('endpoints', '')
                                            prefix = f'/api/{clean_name}'
                                        
                                        blueprint_discoveries.append((import_path, blueprint_name, prefix))
                                        print(f"  📌 Found: {import_path}.{blueprint_name} -> {prefix}")
                                        
            except SyntaxError:
                print(f"  ⚠️ Syntax error in {filepath}, skipping AST parsing")
                
                # Fallback: Simple text scanning for common patterns
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith(('bp = Blueprint', 'api = Blueprint', '_bp = Blueprint')) and 'Blueprint(' in line:
                        # Extract blueprint variable name
                        blueprint_var = line.split('=')[0].strip()
                        
                        # Convert file path to import path
                        if filepath.startswith('./api/'):
                            import_path = f"api.{filepath[6:-3]}"
                        elif filepath.startswith('./'):
                            import_path = filepath[2:-3]
                        else:
                            import_path = filepath[:-3]
                        
                        # Simple prefix generation
                        base_name = os.path.basename(filepath)[:-3]
                        prefix = f'/api/{base_name.replace("_endpoints", "").replace("_api", "")}'
                        
                        blueprint_discoveries.append((import_path, blueprint_var, prefix))
                        print(f"  📌 Found (fallback): {import_path}.{blueprint_var} -> {prefix}")
                        break
                        
        except Exception as e:
            print(f"  ❌ Error scanning {filepath}: {e}")
            continue
    
    print(f"\n🎯 DISCOVERY COMPLETE: Found {len(blueprint_discoveries)} blueprints")
    return blueprint_discoveries

def generate_blueprint_registration_code(discoveries: List[Tuple[str, str, str]]) -> str:
    """Generate Python code for blueprint registration"""
    
    code_lines = []
    code_lines.append("    # 🤖 AUTO-DISCOVERED BLUEPRINTS")
    code_lines.append("    # Generated by auto_blueprint_discovery.py")
    code_lines.append("    ")
    code_lines.append("    auto_discovered_blueprints = [")
    
    for import_path, blueprint_name, prefix in discoveries:
        code_lines.append(f'        ("{import_path}", "{blueprint_name}", "{prefix}"),')
    
    code_lines.append("    ]")
    code_lines.append("    ")
    code_lines.append("    # Register all auto-discovered blueprints")
    code_lines.append("    auto_successful = 0")
    code_lines.append("    for import_path, attr, url_prefix in auto_discovered_blueprints:")
    code_lines.append("        if _register_optional_blueprint(app, import_path, attr, url_prefix):")
    code_lines.append("            auto_successful += 1")
    code_lines.append("    ")
    code_lines.append(f"    logger.info(f'🤖 Auto-discovery: {{auto_successful}}/{len(discoveries)} blueprints registered')")
    
    return '\n'.join(code_lines)

if __name__ == "__main__":
    print("🤖 AUTOMATIC BLUEPRINT DISCOVERY")
    print("=" * 50)
    
    discoveries = discover_blueprints()
    
    if discoveries:
        print(f"\n📋 BLUEPRINT REGISTRATION CODE:")
        print("=" * 50)
        print(generate_blueprint_registration_code(discoveries))
        
        print(f"\n🎯 SUMMARY:")
        print(f"   • Total blueprints discovered: {len(discoveries)}")
        print(f"   • API directory files: {len([d for d in discoveries if d[0].startswith('api.')])}")
        print(f"   • Root directory files: {len([d for d in discoveries if not d[0].startswith('api.')])}")
        
        print(f"\n💡 NEXT STEPS:")
        print("   1. Add the generated code to routes.py")
        print("   2. Update endpoint listing in main route")
        print("   3. Test blueprint registration")
        
    else:
        print("⚠️ No blueprints discovered!")
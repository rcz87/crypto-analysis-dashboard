#!/usr/bin/env python3
"""
Fixed Blueprint Registry - Stable endpoint registration
Maps actual blueprint names found in files to prevent naming inconsistencies
"""

# DEFINITIVE BLUEPRINT REGISTRY - Based on actual file inspection
STABLE_BLUEPRINT_REGISTRY = [
    # Core GPTs API
    ("gpts_routes", "gpts_api", "/api/gpts"),
    
    # Primary API endpoints (verified working)
    ("api.data_quality_endpoints", "data_quality_bp", "/api/data-quality"),
    ("api.security_endpoints", "security_bp", "/api/security"), 
    ("api.performance_endpoints", "performance_bp", "/api/performance"),
    ("api.advanced_optimization_endpoints", "advanced_optimization_bp", "/api/optimization"),
    ("api.ai_reasoning_endpoints", "ai_reasoning_bp", "/api/ai-reasoning"),
    ("api.institutional_endpoints", "institutional_bp", "/api/institutional"),
    ("api.telegram_endpoints", "telegram_bp", "/api/telegram"),
    ("api.webhook_endpoints", "webhook_bp", "/api/webhooks"),
    ("api.smc_zones_endpoints", "smc_zones_bp", "/api/smc-zones"),
    ("api.news_endpoints", "news_api", "/api/news"),
    
    # Trading & Signal endpoints
    ("api.enhanced_signal_endpoints", "enhanced_signals_bp", "/api/signals/enhanced"),
    ("api.sharp_signal_endpoint", "sharp_signal_bp", "/api/signals/sharp"),
    ("api.signal_top_endpoints", "signal_top_bp", "/api/signals/top"),
    ("api.sharp_scoring_endpoints", "sharp_scoring_bp", "/api/signals/scoring"),
    
    # Analysis & Charts
    ("api.backtest_endpoints", "backtest_api", "/api/backtest"),
    ("api.chart_endpoints", "chart_bp", "/api/charts"),
    ("api.missing_endpoints", "missing_bp", "/api/analysis/missing"),
    ("api.modular_endpoints", "modular_bp", "/api/analysis/modular"),
    ("api.improvement_endpoints", "improvement_bp", "/api/analysis/improvements"),
    
    # Enhanced features
    ("api.enhanced_gpts_endpoints", "enhanced_gpts", "/api/gpts/enhanced"),
    ("api.missing_gpts_endpoints", "missing_gpts_bp", "/api/gpts/missing"),
    ("api.gpts_coinglass_endpoints", "gpts_coinglass_bp", "/api/gpts/coinglass"),
    ("api.gpts_coinglass_simple", "coinglass_bp", "/api/coinglass"),
    
    # Utility endpoints  
    ("api.promptbook", "promptbook_bp", "/api/promptbook"),
    ("api.performance_api", "performance_api", "/api/performance/advanced"),
]

def get_stable_blueprint_count():
    """Return count of stable blueprints for consistency"""
    return len(STABLE_BLUEPRINT_REGISTRY)

def generate_stable_registration_code():
    """Generate consistent registration code"""
    code = []
    code.append("    # 🔒 STABLE BLUEPRINT REGISTRY - Fixed naming to prevent changes")
    code.append("    stable_blueprints = [")
    
    for import_path, blueprint_name, prefix in STABLE_BLUEPRINT_REGISTRY:
        code.append(f'        ("{import_path}", "{blueprint_name}", "{prefix}"),')
    
    code.append("    ]")
    code.append("")
    code.append("    # Register stable blueprints")
    code.append("    stable_successful = 0")
    code.append("    for import_path, attr, url_prefix in stable_blueprints:")
    code.append("        if _register_optional_blueprint(app, import_path, attr, url_prefix):")
    code.append("            stable_successful += 1")
    code.append("")
    code.append(f"    logger.info(f'🔒 Stable registry: {{stable_successful}}/{len(STABLE_BLUEPRINT_REGISTRY)} blueprints registered consistently')")
    
    return '\n'.join(code)

if __name__ == "__main__":
    print("🔒 STABLE BLUEPRINT REGISTRY SYSTEM")
    print("=" * 50)
    print(f"Total stable blueprints: {get_stable_blueprint_count()}")
    print("\nGenerated registration code:")
    print(generate_stable_registration_code())
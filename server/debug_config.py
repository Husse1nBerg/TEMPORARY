#!/usr/bin/env python3

import os
from typing import Optional

# Simple debug script to test Pydantic configuration
print("=== Pydantic Configuration Debug ===")

# Check Pydantic version
try:
    import pydantic
    print(f"Pydantic version: {pydantic.VERSION}")
except Exception as e:
    print(f"Pydantic import error: {e}")

# Try different approaches
approaches = [
    "BaseModel with extra='allow'",
    "BaseSettings v1 style", 
    "BaseSettings v2 style",
    "Manual dict loading"
]

print(f"\nTesting {len(approaches)} approaches...\n")

# Approach 1: BaseModel with extra='allow'
print("1. Testing BaseModel with extra='allow':")
try:
    from pydantic import BaseModel
    
    class TestConfig1(BaseModel):
        ANTHROPIC_API_KEY: Optional[str] = None
        DEBUG: bool = False
        
        class Config:
            extra = "allow"
    
    # Test with your actual key
    test_data = {
        "ANTHROPIC_API_KEY": "sk-ant-api03--test-key",
        "DEBUG": True,
        "UNKNOWN_KEY": "should be allowed"
    }
    
    config1 = TestConfig1(**test_data)
    print(f"✅ SUCCESS: {config1.ANTHROPIC_API_KEY[:20]}...")
    
except Exception as e:
    print(f"❌ FAILED: {e}")

print()

# Approach 2: BaseSettings v1 style
print("2. Testing BaseSettings v1 style:")
try:
    from pydantic import BaseSettings
    
    class TestConfig2(BaseSettings):
        ANTHROPIC_API_KEY: Optional[str] = None
        DEBUG: bool = False
        
        class Config:
            extra = "allow"
            case_sensitive = True
    
    config2 = TestConfig2()
    print(f"✅ SUCCESS: {getattr(config2, 'ANTHROPIC_API_KEY', 'NOT_FOUND')}")
    
except Exception as e:
    print(f"❌ FAILED: {e}")

print()

# Approach 3: BaseSettings v2 style  
print("3. Testing BaseSettings v2 style:")
try:
    from pydantic_settings import BaseSettings
    from pydantic import ConfigDict
    
    class TestConfig3(BaseSettings):
        model_config = ConfigDict(extra="allow", case_sensitive=True)
        
        ANTHROPIC_API_KEY: Optional[str] = None
        DEBUG: bool = False
    
    config3 = TestConfig3()
    print(f"✅ SUCCESS: {getattr(config3, 'ANTHROPIC_API_KEY', 'NOT_FOUND')}")
    
except Exception as e:
    print(f"❌ FAILED: {e}")

print()

# Approach 4: Manual dict loading
print("4. Testing manual dict loading:")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    class TestConfig4:
        def __init__(self):
            self.ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
            self.DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    config4 = TestConfig4()
    print(f"✅ SUCCESS: {config4.ANTHROPIC_API_KEY[:20] if config4.ANTHROPIC_API_KEY else 'NOT_FOUND'}...")
    
except Exception as e:
    print(f"❌ FAILED: {e}")

print("\n=== End Debug ===")
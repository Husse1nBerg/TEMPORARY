#!/usr/bin/env python3

import os
from typing import Optional

print("=== Pydantic Configuration Debug ===")

# Check Pydantic version
try:
    import pydantic
    print(f"Pydantic version: {pydantic.VERSION}")
except Exception as e:
    print(f"Pydantic import error: {e}")

print("\n1. Testing BaseModel with extra='allow':")
try:
    from pydantic import BaseModel
    
    class TestConfig1(BaseModel):
        ANTHROPIC_API_KEY: Optional[str] = None
        DEBUG: bool = False
        
        class Config:
            extra = "allow"
    
    test_data = {
        "ANTHROPIC_API_KEY": "sk-ant-api03--test-key",
        "DEBUG": True,
        "UNKNOWN_KEY": "should be allowed"
    }
    
    config1 = TestConfig1(**test_data)
    print(f"SUCCESS: {config1.ANTHROPIC_API_KEY[:20]}...")
    
except Exception as e:
    print(f"FAILED: {e}")

print("\n2. Testing BaseSettings v2 style:")
try:
    from pydantic_settings import BaseSettings
    from pydantic import ConfigDict
    
    class TestConfig3(BaseSettings):
        model_config = ConfigDict(extra="allow", case_sensitive=True)
        
        ANTHROPIC_API_KEY: Optional[str] = None
        DEBUG: bool = False
    
    config3 = TestConfig3()
    print(f"SUCCESS: {getattr(config3, 'ANTHROPIC_API_KEY', 'NOT_FOUND')}")
    
except Exception as e:
    print(f"FAILED: {e}")

print("\n3. Testing manual dict loading:")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    class TestConfig4:
        def __init__(self):
            self.ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
            self.DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    
    config4 = TestConfig4()
    key_preview = config4.ANTHROPIC_API_KEY[:20] if config4.ANTHROPIC_API_KEY else 'NOT_FOUND'
    print(f"SUCCESS: {key_preview}...")
    
except Exception as e:
    print(f"FAILED: {e}")

print("\n=== End Debug ===")
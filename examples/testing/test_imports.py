#!/usr/bin/env python3
"""
Test script to isolate import issues.
"""

print("Testing imports...")

try:
    print("1. Testing FastAPI import...")
    from fastapi import FastAPI
    print("   ✅ FastAPI imported successfully")
    
    print("2. Testing CORS middleware import...")
    from fastapi.middleware.cors import CORSMiddleware
    print("   ✅ CORSMiddleware imported successfully")
    
    print("3. Testing basic FastAPI app creation...")
    app = FastAPI()
    print("   ✅ FastAPI app created successfully")
    
    print("4. Testing CORS middleware addition...")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    print("   ✅ CORS middleware added successfully")
    
    print("5. Testing heartbeat router import...")
    from modules.routes import heartbeat_router
    print("   ✅ Heartbeat router imported successfully")
    
    print("6. Testing reflect router import...")
    from modules.routes import reflect_router
    print("   ✅ Reflect router imported successfully")
    
    print("7. Testing router inclusion...")
    app.include_router(heartbeat_router)
    print("   ✅ Heartbeat router included successfully")
    
    app.include_router(reflect_router)
    print("   ✅ Reflect router included successfully")
    
    print("\n🎉 All imports and configurations successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
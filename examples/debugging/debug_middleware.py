#!/usr/bin/env python3
"""
Debug script to identify the middleware issue.
"""

import sys
import traceback

def debug_fastapi():
    print("🔍 Debugging FastAPI middleware issue...")
    
    try:
        print("1. Importing FastAPI...")
        from fastapi import FastAPI
        print("   ✅ FastAPI imported")
        
        print("2. Creating FastAPI app...")
        app = FastAPI()
        print("   ✅ FastAPI app created")
        
        print("3. Checking app.middleware attribute...")
        print(f"   app.middleware type: {type(app.middleware)}")
        print(f"   app.middleware value: {app.middleware}")
        
        print("4. Checking app.user_middleware attribute...")
        if hasattr(app, 'user_middleware'):
            print(f"   app.user_middleware type: {type(app.user_middleware)}")
            print(f"   app.user_middleware value: {app.user_middleware}")
        else:
            print("   app.user_middleware not found")
        
        print("5. Attempting to add simple route...")
        @app.get("/test")
        async def test():
            return {"message": "test"}
        print("   ✅ Route added")
        
        print("6. Attempting to build middleware stack manually...")
        try:
            # This is what FastAPI does internally
            middleware_stack = app.build_middleware_stack()
            print("   ✅ Middleware stack built successfully")
        except Exception as e:
            print(f"   ❌ Middleware stack build failed: {e}")
            print("   Full traceback:")
            traceback.print_exc()
            
            # Let's inspect the middleware list
            print("\n   Inspecting middleware list:")
            if hasattr(app, 'user_middleware'):
                for i, middleware in enumerate(app.user_middleware):
                    print(f"   Middleware {i}: {middleware} (type: {type(middleware)})")
                    if hasattr(middleware, '__len__'):
                        print(f"     Length: {len(middleware)}")
                        if len(middleware) > 0:
                            for j, item in enumerate(middleware):
                                print(f"       Item {j}: {item} (type: {type(item)})")
        
        print("\n🎉 Debug completed!")
        
    except Exception as e:
        print(f"❌ Error during debug: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug_fastapi()
import sys
import os

# Add root project path to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    from backend.app.main import app
except Exception as e:
    import traceback
    err_tb = traceback.format_exc()
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    
    app = FastAPI(title="TCF-FX Startup Diagnostics")
    
    @app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"])
    def catch_all(full_path: str):
        return JSONResponse(
            status_code=500,
            content={
                "error": "Startup Import Exception on Serverless Host",
                "exception_type": type(e).__name__,
                "detail": str(e),
                "traceback": err_tb
            }
        )

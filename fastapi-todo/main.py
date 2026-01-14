from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from pydantic import ValidationError as PydanticValidationError
from routers import todos

app = FastAPI(
    title="Todo API",
    description="A simple todo API with FastAPI",
    version="1.0.0"
)

# Include routers
app.include_router(todos.router, prefix="/api", tags=["todos"])

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    # Convert errors to JSON-serializable format
    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", ""),
            "input": str(error.get("input", "")),
        }
        errors.append(error_dict)
    
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors}
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request, exc):
    # Convert errors to JSON-serializable format
    errors = []
    for error in exc.errors():
        error_dict = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", ""),
            "type": error.get("type", ""),
            "input": str(error.get("input", "")),
        }
        errors.append(error_dict)
    
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": errors}
    )

@app.get("/")
async def root():
    return {"message": "Welcome to Todo API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
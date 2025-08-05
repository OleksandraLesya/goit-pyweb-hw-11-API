# main.py

import uvicorn
from fastapi import FastAPI
# The import from app.routes.contacts is a great solution!

from app.routes.contacts import router as contacts_router

# We create an instance of our FastAPI application with a title.
app = FastAPI(title="Contacts API")

# We include our contacts router with a professional /api prefix.
app.include_router(contacts_router, prefix="/api")


@app.get("/")
def read_root():
    """
    Root endpoint for our application.
    """
    return {"message": "Hello World"}


if __name__ == "__main__":
    # The uvicorn server will run our application on localhost at port 8000.
    uvicorn.run(app, host="0.0.0.0", port=8000)

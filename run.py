import uvicorn

from urls import app

if __name__ == '__main__':
    uvicorn.run(app=app)
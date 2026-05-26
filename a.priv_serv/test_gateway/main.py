from datetime import datetime
from fastapi import FastAPI

app = FastAPI(title="Test Gateway")


@app.get("/")
def root():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"result": f"{now} aaa"}

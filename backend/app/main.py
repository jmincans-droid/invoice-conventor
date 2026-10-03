from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.invoices import router as invoices_router

app = FastAPI(title="PDF -> E-Rēķins", version="0.1.1")
app.include_router(invoices_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def review_ui() -> str:
    with open("app/templates/index.html", encoding="utf-8") as template:
        return template.read()

"""FastAPI route handlers."""

import json
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from backend.api.analyzer import compare_analyses, get_analysis, run_analysis
from backend.reports.report_generator import generate_pdf_report

router = APIRouter()
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "outputs"
DEMO_DIR = Path(__file__).resolve().parents[2] / "demo_images"

ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}


async def _read_and_validate(file: UploadFile) -> bytes:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Accepted: JPG, JPEG, PNG, WEBP.")
    data = await file.read()
    if len(data) < 100:
        raise HTTPException(status_code=400, detail="File appears corrupted or empty.")
    return data


@router.post("/analyze")
async def analyze(
    file: UploadFile = File(...),
    crop: str = Form(default=""),
):
    try:
        data = await _read_and_validate(file)
        crop_dict = json.loads(crop) if crop else None
        result = run_analysis(data, crop=crop_dict, filename=file.filename or "upload.jpg")
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/compare")
async def compare(
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
):
    try:
        data_a = await _read_and_validate(file_a)
        data_b = await _read_and_validate(file_b)
        result_a = run_analysis(data_a, filename=file_a.filename or "screen_a.jpg")
        result_b = run_analysis(data_b, filename=file_b.filename or "screen_b.jpg")
        comparison = compare_analyses(result_a, result_b)
        return JSONResponse(content={
            "analysis_a": result_a,
            "analysis_b": result_b,
            "comparison": comparison,
        })
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison failed: {str(e)}")


@router.get("/analysis/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    result = get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return JSONResponse(content=result)


@router.get("/report/{analysis_id}")
async def download_report(analysis_id: str):
    result = get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    pdf_path = OUTPUT_DIR / f"{analysis_id}_report.pdf"
    generate_pdf_report(result, pdf_path)
    return FileResponse(pdf_path, media_type="application/pdf", filename=f"forensic_report_{analysis_id[:8]}.pdf")


@router.get("/demo/{sample_name}")
async def demo_analysis(sample_name: str):
    sample_path = DEMO_DIR / f"{sample_name}.png"
    if not sample_path.exists():
        sample_path = DEMO_DIR / f"{sample_name}.jpg"
    if not sample_path.exists():
        raise HTTPException(status_code=404, detail=f"Demo sample '{sample_name}' not found.")
    with open(sample_path, "rb") as f:
        data = f.read()
    result = run_analysis(data, filename=sample_path.name)
    return JSONResponse(content=result)


@router.get("/demo-list")
async def demo_list():
    DEMO_DIR.mkdir(parents=True, exist_ok=True)
    samples = []
    for p in sorted(DEMO_DIR.glob("*")):
        if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            samples.append({"name": p.stem, "filename": p.name})
    return {"samples": samples}

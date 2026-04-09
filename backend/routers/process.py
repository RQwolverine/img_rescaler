import json
from fastapi import APIRouter, File, Form, UploadFile, HTTPException

from models.schemas import ImageConfig, ProcessingResponse, ProcessingResultItem
from services.pipeline import process_image

router = APIRouter()


@router.post("/process", response_model=ProcessingResponse)
async def process_images(
    files: list[UploadFile] = File(...),
    configs: str = Form(...),
):
    """
    Process 1-9 A4 line-art images with per-image scaling configuration.

    - files: 1-9 image files (multipart)
    - configs: JSON array of ImageConfig objects (order-matched to files)
    """
    if not 1 <= len(files) <= 9:
        raise HTTPException(status_code=400, detail="Upload between 1 and 9 images.")

    try:
        config_list = [ImageConfig(**c) for c in json.loads(configs)]
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid configs JSON: {e}")

    if len(config_list) != len(files):
        raise HTTPException(
            status_code=400,
            detail=f"Number of configs ({len(config_list)}) must match number of files ({len(files)}).",
        )

    results: list[ProcessingResultItem] = []
    for upload, config in zip(files, config_list):
        image_bytes = await upload.read()
        result = process_image(image_bytes, config)
        results.append(result)

    return ProcessingResponse(results=results)

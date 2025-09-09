from typing import Annotated

from fastapi import APIRouter, Query, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.config import DB_JSON_FILENAME
from app.controllers.resources import ResourcesController
from app.handlers.exceptions import ResponseHeaders
from app.handlers.messages import (
    GET_RESOURCE_ID_DESCRIPTION,
    POST_RESOURCE_ID_DESCRIPTION,
)

router = APIRouter()

resources_ctlr = ResourcesController()


@router.get(
    "/",
    summary="Get list of available resources.",
    tags=["API"],
    response_description="Resources names and their total number of items.",
)
async def get_resources_list() -> list[dict[str, int]]:
    return resources_ctlr.get_resources_list()


@router.get(
    "/{resource}",
    summary="Get all the data of the resource.",
    tags=["API"],
)
async def get_resource_data(
    resource,
    page: Annotated[int, Query(gt=0)] = resources_ctlr.page,
    limit: Annotated[
        int,
        Query(
            ge=10, description="The maximum number of items to retrieve for each page."
        ),
    ] = resources_ctlr.limit,
):
    return resources_ctlr.get_resource_data(resource, page, limit)


@router.get(
    "/{resource}/{id}",
    summary="Get the resource ID data.",
    description=GET_RESOURCE_ID_DESCRIPTION,
    tags=["API"],
)
async def get_resources_by_id(resource, id: int | str):
    return resources_ctlr.retrieve_resources_by_id(resource, id)


@router.put(
    "/{resource}/{id}",
    summary="Add ID data into resource.",
    description=POST_RESOURCE_ID_DESCRIPTION,
    tags=["API"],
)
async def put_resources_by_id(resource: str, id: int | str, data: dict) -> dict:
    response = resources_ctlr.put_resources_data_by_id(resource, id, data)

    return JSONResponse(
        content=jsonable_encoder(response),
        headers=ResponseHeaders.JSON_HEADERS.value,
        status_code=status.HTTP_202_ACCEPTED,
    )


@router.delete(
    "/{resource}/{id}",
    summary="Delete ID data into resource.",
    tags=["API"],
)
async def delete_resource_id(resource: str, id: int | str) -> dict:
    response = resources_ctlr.delete_resource_id(resource, id)

    return JSONResponse(
        content=jsonable_encoder(response),
        headers=ResponseHeaders.JSON_HEADERS.value,
        status_code=status.HTTP_202_ACCEPTED,
    )


@router.put(
    "/upload",
    summary=f"Update DB JSON file ({DB_JSON_FILENAME}) from CSV file content.",
    description="""
    
    """,
    tags=["API"],
)
async def create_json_file_from_csv(csv_file: UploadFile):
    response = await resources_ctlr.update_db_json_from_csv(csv_file)
    return response

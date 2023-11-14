from fastapi import APIRouter

router = APIRouter(
    prefix="/company",
    tags=["companyapis"],
    responses={
        418 : {"message": "For internal use only"}
    }
)

@router.get("/")
async def get_company_name():
    return {"company" : "Algo-rhythm LLC"}

@router.get("/employees")
async def get_employees():
    return {"employees" : "List of employees"}

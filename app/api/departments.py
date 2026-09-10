"""
部门 API
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import require_super_admin
from app.core.exceptions import NotFoundException, ConflictException
from app.models import Department, Admin
from app.schemas.common import success
from app.schemas.__init__ import DepartmentCreate, DepartmentInfo

router = APIRouter()


@router.post("/", summary="新增部门（仅超管）")
def create_department(
    data: DepartmentCreate,
    admin: Admin = Depends(require_super_admin),
    db: Session = Depends(get_db),
):
    if db.query(Department).filter(Department.name == data.name, Department.is_deleted == False).first():
        raise ConflictException("部门名称已存在")
    dept = Department(**data.model_dump())
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return success(data=DepartmentInfo.model_validate(dept).model_dump(mode="json"), message="部门创建成功")


@router.get("/", summary="部门列表")
def list_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).filter(Department.is_deleted == False).all()
    return success(data=[DepartmentInfo.model_validate(d).model_dump(mode="json") for d in depts])


@router.get("/{dept_id}", summary="部门详情")
def get_department(dept_id: int, db: Session = Depends(get_db)):
    dept = db.query(Department).filter(
        Department.id == dept_id, Department.is_deleted == False
    ).first()
    if not dept:
        raise NotFoundException("部门不存在")
    return success(data=DepartmentInfo.model_validate(dept).model_dump(mode="json"))

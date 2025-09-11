from contextlib import contextmanager
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any

from sqlalchemy import and_, desc, asc

from lesscode.core.database import get_session_local
from lesscode.models.base import BaseModel

# Use a more descriptive name for the TypeVar
ModelT = TypeVar("ModelT", bound=BaseModel)


class BaseRepository(Generic[ModelT]):
    """仓储基类"""

    def __init__(self, model: Type[ModelT], database_name: str = "default"):
        self.model = model
        self.database_name = database_name
        self.session_local = get_session_local(database_name)

    @contextmanager
    def _get_session(self):
        """获取数据库会话上下文管理器"""
        db = self.session_local()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    def create(self, obj_in: Dict[str, Any]) -> ModelT:
        """创建记录"""
        with self._get_session() as db:
            db_obj = self.model(**obj_in)
            db.add(db_obj)
            db.flush()  # 刷新但不提交
            db.refresh(db_obj)  # 刷新对象
            # 创建一个新的对象来返回，避免会话绑定问题
            result_dict = {column.name: getattr(db_obj, column.name) for column in
                           db_obj.__table__.columns}
            return self.model(**result_dict)

    def get(self, record_id: int) -> Optional[ModelT]:
        """根据ID获取记录"""
        with self._get_session() as db:
            return db.query(self.model).filter(
                and_(self.model.id == record_id)
            ).first()

    def get_multi(
            self,
            skip: int = 0,
            limit: int = 100,
            order_by: Optional[str] = None,
            desc_order: bool = False,
            filters: Optional[Dict[str, Any]] = None
    ) -> List[ModelT]:
        """获取多条记录"""
        with self._get_session() as db:
            query = db.query(self.model)

            # 添加过滤条件
            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        if isinstance(value, list):
                            query = query.filter(getattr(self.model, key).in_(value))
                        else:
                            query = query.filter(getattr(self.model, key) == value)

            # 添加排序
            if order_by and hasattr(self.model, order_by):
                if desc_order:
                    query = query.order_by(desc(getattr(self.model, order_by)))
                else:
                    query = query.order_by(asc(getattr(self.model, order_by)))

            return query.offset(skip).limit(limit).all()

    def get_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """获取记录总数"""
        with self._get_session() as db:
            query = db.query(self.model).filter(self.model.is_deleted is False)

            if filters:
                for key, value in filters.items():
                    if hasattr(self.model, key):
                        if isinstance(value, list):
                            query = query.filter(getattr(self.model, key).in_(value))
                        else:
                            query = query.filter(getattr(self.model, key) == value)

            return query.count()

    def update(self, record_id: int, obj_in: Dict[str, Any]) -> Optional[ModelT]:
        """更新记录"""
        with self._get_session() as db:
            db_obj = db.query(self.model).filter(
                and_(self.model.id == record_id)
            ).first()

            if db_obj:
                for key, value in obj_in.items():
                    if hasattr(db_obj, key):
                        setattr(db_obj, key, value)
                db.flush()
                db.refresh(db_obj)
                # 返回分离的对象
                result_dict = {column.name: getattr(db_obj, column.name) for column in
                               db_obj.__table__.columns}
                return self.model(**result_dict)

            return None

    def delete(self, record_id: int) -> bool:
        """删除记录"""
        with self._get_session() as db:
            db_obj = db.query(self.model).filter(
                and_(self.model.id == record_id)
            ).first()

            if db_obj:
                db.delete(db_obj)
                return True

            return False

    def get_by_field(self, field: str, value: Any) -> Optional[ModelT]:
        """根据字段获取记录"""
        if not hasattr(self.model, field):
            return None

        with self._get_session() as db:
            return db.query(self.model).filter(
                getattr(self.model, field) == value
            ).first()

    def get_multi_by_field(
            self,
            field: str,
            value: Any,
            skip: int = 0,
            limit: int = 100
    ) -> List[ModelT]:
        """根据字段获取多条记录"""
        if not hasattr(self.model, field):
            return []

        with self._get_session() as db:
            return db.query(self.model).filter(
                getattr(self.model, field) == value,
            ).offset(skip).limit(limit).all()

    def batch_create(self, objs_in: List[Dict[str, Any]]) -> List[ModelT]:
        """批量创建"""
        with self._get_session() as db:
            db_objs = [self.model(**obj_in) for obj_in in objs_in]
            db.add_all(db_objs)
            db.flush()
            for obj in db_objs:
                db.refresh(obj)
            # 返回分离的对象
            results = []
            for obj in db_objs:
                result_dict = {column.name: getattr(obj, column.name) for column in
                               obj.__table__.columns}
                results.append(self.model(**result_dict))
            return results

    def exists(self, record_id: int) -> bool:
        """检查记录是否存在"""
        with self._get_session() as db:
            return db.query(self.model).filter(self.model.id == record_id
                                               ).first() is not None

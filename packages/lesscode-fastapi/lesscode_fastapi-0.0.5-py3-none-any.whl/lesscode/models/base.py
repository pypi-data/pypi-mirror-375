from lesscode.core.database import Base


class BaseModel(Base):
    """数据库模型基类"""
    __abstract__ = True

    # id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    #
    # @declared_attr
    # def created_at(cls):
    #     return Column(DateTime, default=datetime.utcnow, comment="创建时间")
    #
    # @declared_attr
    # def updated_at(cls):
    #     return Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    #
    # @declared_attr
    # def is_deleted(cls):
    #     return Column(Boolean, default=False, comment="是否删除")

    def to_dict(self):
        """转换为字典"""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"

from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy import JSON, BigInteger, Boolean, DateTime, Integer, String, Text
from sqlalchemy.sql import func
from datetime import datetime


Base = declarative_base()


class Artifact(Base):
    __tablename__ = "forensic_data_files"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment="고유 식별자")
    pc_id: Mapped[str] = mapped_column(String(255), nullable=True, comment="PC 고유 식별자")
    task: Mapped[str] = mapped_column(String(255), nullable=True, comment="작업 또는 태스크 정보")
    module_type: Mapped[str] = mapped_column(String(100), nullable=True, comment="모듈 유형 (browser, deleted, usb 등)")
    collection_time: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="데이터 수집 시간")
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=True, comment="파일 크기 (바이트)")
    checksum: Mapped[str] = mapped_column(String(64), nullable=True, comment="파일 체크섬 (MD5, SHA256 등)")
    json_data: Mapped[dict] = mapped_column(JSON, nullable=True, comment="원본 JSON 데이터")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=func.now(), comment="레코드 생성 시간")
    update_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=func.now(), onupdate=func.now(), comment="레코드 업데이트 시간")
    processed: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False, comment="처리 완료 여부")
    error_message: Mapped[str] = mapped_column(Text, nullable=True, comment="처리 중 발생한 오류 메시지")
    extracted_info: Mapped[dict] = mapped_column(JSON, nullable=True, comment="추출/가공된 정보")

    def to_dict(self):
        """객체를 딕셔너리로 변환"""
        return {
            'id': self.id,
            'pc_id': self.pc_id,
            'task': self.task,
            'module_type': self.module_type,
            'collection_time': self.collection_time.isoformat() if self.collection_time else None,
            'file_size': self.file_size,
            'checksum': self.checksum,
            'json_data': self.json_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'update_at': self.update_at.isoformat() if self.update_at else None,
            'processed': self.processed,
            'error_message': self.error_message,
            'extracted_info': self.extracted_info
        }
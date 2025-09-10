import os
import json
import tempfile
from typing import Optional, Any
from ..core import Category
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from .base import Config_db, get_db
from .data import Artifact
from sqlalchemy.orm import Session

 
class DataLoader:
    def __init__(self):
        self.data_dir = "./data/agent_result"
        self.file_path: str = ""
        self.config: Optional[Config_db] = None
        self.db: Optional[Session] = None
        self._s3_client: Optional[Any] = None

    def local_data_load(self, category: Category, directory=None) -> dict:
        if directory:
            self._set_data_dir(directory)
        self._get_file_path(category)
        with open(self.file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    
    def _set_data_dir(self, directory:str) -> None:
        if not os.path.exists(directory):
            raise NotADirectoryError(f"디렉토리가 존재하지 않습니다: {directory}")
        self.data_dir = directory
    
    def _get_file_path(self, category: Category) -> None:
        file_list = os.listdir(self.data_dir)
        matching_files = [filename for filename in file_list if filename.lower().startswith(category.value)]
        
        if not matching_files:
            raise FileNotFoundError(f"No file starts with '{category.value}' in {self.data_dir}")
        
        file_path = os.path.join(self.data_dir, matching_files[0])
        self.file_path = file_path
        
    def s3_data_load(self, category: Category, s3_config: dict) -> dict:
        """
        S3에서 데이터를 로드합니다.
        
        Args:
            category: 데이터 카테고리
            s3_config: S3 설정 딕셔너리
                - bucket (str): S3 버킷 이름
                - task_id (str): 작업 ID (UUID)
                - region (str, optional): AWS 리전
                - profile (str, optional): AWS 프로파일
        
        Returns:
            dict: 로드된 데이터
            
        Example:
            s3_config = {
                'bucket': 'my-forensics-bucket',
                'task_id': '550e8400-e29b-41d4-a716-446655440000',
                'region': 'us-east-1'
            }
            data = loader.s3_data_load(Category.BROWSER, s3_config)
        """
        required_keys = ['bucket', 'task_id']
        for key in required_keys:
            if key not in s3_config:
                raise ValueError(f"s3_config에 '{key}' 파라미터가 필요합니다.")
        
        # task_id와 category를 이용해 S3 키 생성
        s3_key = f"{s3_config['task_id']}/{category.value}_data.json"
        
        self._init_s3_client(s3_config)

        with tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix='.json') as temp_file:
            temp_path = temp_file.name
        
        try:
            if not self._s3_client:
                raise RuntimeError("S3 클라이언트가 초기화되지 않았습니다.")
                
            self._s3_client.download_file(
                s3_config['bucket'], 
                s3_key, 
                temp_path
            )
            
            with open(temp_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {e}")
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise FileNotFoundError(f"S3 파일을 찾을 수 없습니다: s3://{s3_config['bucket']}/{s3_key}")
            elif error_code == 'NoSuchBucket':
                raise FileNotFoundError(f"S3 버킷을 찾을 수 없습니다: {s3_config['bucket']}")
            else:
                raise Exception(f"S3 다운로드 오류: {e}")
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def _init_s3_client(self, s3_config: dict) -> None:
        try:
            client_kwargs = {}
            
            if 'region' in s3_config:
                client_kwargs['region_name'] = s3_config['region']
                
            if 'profile' in s3_config:
                session = boto3.Session(profile_name=s3_config['profile'])
                self._s3_client = session.client('s3', **client_kwargs)
            else:
                self._s3_client = boto3.client('s3', **client_kwargs)
                
        except NoCredentialsError:
            raise NoCredentialsError()
        
    def set_database(self, config: Config_db) -> None:
        """데이터베이스 설정을 초기화합니다."""
        self.config = config
        try:
            # 기존 세션이 있다면 닫기
            if self.db:
                self.db.close()
            self.db = get_db(self.config)
        except Exception as e:
            raise ConnectionRefusedError(f"데이터베이스 연결 실패: {e}")
        

    def _ensure_db_connection(self) -> None:
        """데이터베이스 연결 상태를 확인하고 필요시 재연결합니다."""
        if not self.config:
            raise ValueError("데이터베이스 설정이 필요합니다. set_database()를 먼저 호출하세요.")
        
        # 세션이 없거나 비활성 상태인 경우 새로 연결
        if not self.db or not self.db.is_active:
            try:
                if self.db:
                    self.db.close()
                self.db = get_db(self.config)
            except Exception as e:
                raise ConnectionError(f"데이터베이스 재연결 실패: {e}")

    def _close_db_session(self) -> None:
        """데이터베이스 세션을 안전하게 닫습니다."""
        if self.db:
            try:
                self.db.close()
            except Exception:
                pass  # 이미 닫힌 세션이거나 다른 이유로 닫기 실패시 무시
            finally:
                self.db = None

    def database_data_load(self, task_id: str, category: Category) -> dict:
        """데이터베이스에서 지정된 task_id와 category에 해당하는 데이터를 로드합니다.
        
        Args:
            task_id: 작업 ID
            category: 데이터 카테고리
            
        Returns:
            dict: 로드된 JSON 데이터
            
        Raises:
            ValueError: 데이터베이스 설정이 없거나 데이터를 찾을 수 없는 경우
            ConnectionError: 데이터베이스 연결 오류
        """
        try:
            self._ensure_db_connection()
            # 모듈 타입 생성 (예: BROWSER_DATA, USB_DATA 등)
            module_type = f"{category.value.upper()}_DATA"
            
            # SQLAlchemy 쿼리 실행 시 self.db가 None이 아님을 보장
            if not self.db:
                raise ConnectionError("데이터베이스 세션이 초기화되지 않았습니다.")
                
            data = self.db.query(Artifact).filter(
                Artifact.task == task_id,
                Artifact.module_type == module_type
            ).first()

            if not data:
                raise ValueError(
                    f"task_id '{task_id}'와 module_type '{module_type}'에 해당하는 데이터를 찾을 수 없습니다."
                )

            if not data.json_data:
                raise ValueError(
                    f"task_id '{task_id}'의 데이터에 json_data가 없습니다."
                )

            return data.json_data
            
        except Exception as e:
            # 데이터베이스 오류의 경우 세션을 닫고 다시 throw
            if "database" in str(e).lower() or "connection" in str(e).lower():
                self._close_db_session()
            raise
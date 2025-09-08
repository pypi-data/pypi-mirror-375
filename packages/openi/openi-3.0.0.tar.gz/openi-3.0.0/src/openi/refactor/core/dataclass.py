from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class UploadDirectArgs:
    # file_name	string	是	文件名
    # subject_id	string	是	关联id，如上传数据集下文件时传的是数据集id
    # subject_type	string	是	数据类型，数据集为1
    # file_type	string	是	文件类型
    # size	int64	是	文件大小
    file_name: str
    subject_id: str
    subject_type: str
    file_type: str
    size: int
    extra: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class UploadCompleteDirectArgs:
    # file_name_list	string	是	文件名数组，用英文逗号分割
    # subject_id	string	是	关联id，如上传数据集下文件时传的是数据集id
    # subject_type	string	是	数据类型，数据集为1
    file_name_list: List[str]
    subject_id: str
    subject_type: str


@dataclass
class UploadGetChunksArgs:
    # md5	string	是	待上传文件的MD5值
    # file_name	string	是	文件名
    # subject_id	string	是	关联id，如上传数据集下文件时传的是数据集id
    # subject_type	string	是	数据类型，数据集为1
    md5: str
    file_name: str
    subject_id: str
    subject_type: str
    extra: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class UploadNewMultipartArgs:
    # md5	string	是	待上传文件的MD5值
    # file_name	string	是	文件名
    # subject_id	string	是	关联id，如上传数据集文件时传的是数据集id
    # subject_type	string	是	数据类型，数据集为1
    # file_type	string	是	文件类型
    # size	int64	是	文件大小
    # total_chunk_counts	int	是	分片数量
    md5: str
    file_name: str
    subject_id: str
    subject_type: str
    file_type: str
    size: int
    total_chunk_counts: int
    extra: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class UploadGetMultipartUrlArgs:
    # uuid	string	是	上一个接口返回的uuid
    # chunk_number	int	是	分片编号
    # size	int64	是	本分片大小
    uuid: str
    chunk_number: int
    size: int
    extra: Optional[Dict[str, Any]] = field(default_factory=dict)



class FileUtils:
    """파일 관련 유틸리티"""
    
    @staticmethod
    def get_file_info(upload_file: UploadFile) -> tuple[Union[str, None], int]:
        """파일 정보 추출 (이미지 타입, 파일 크기)"""
        contents = upload_file.file.read()
        file_size = len(contents)
        file_like = io.BytesIO(contents)
        image_type = imghdr.what(file_like)
        upload_file.file.seek(0)
        return image_type, file_size
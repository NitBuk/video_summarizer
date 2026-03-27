from video_summarizer.ui import _build_upload_token


class DummyUpload:
    def __init__(self, name: str, *, file_id: str | None, size: int):
        self.name = name
        self.file_id = file_id
        self.size = size


def test_build_upload_token_distinguishes_same_name_uploads():
    first = DummyUpload("lecture.mp4", file_id="upload-1", size=1024)
    second = DummyUpload("lecture.mp4", file_id="upload-2", size=1024)

    assert _build_upload_token(first) != _build_upload_token(second)


def test_build_upload_token_falls_back_to_name_and_size():
    upload = DummyUpload("lecture.mp4", file_id=None, size=2048)

    assert _build_upload_token(upload) == (None, "lecture.mp4", 2048)

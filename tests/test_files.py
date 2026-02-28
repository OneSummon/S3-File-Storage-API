from datetime import datetime

import pytest
from unittest.mock import patch
import io
from httpx import AsyncClient

from app.crud.files import get_file
from app.database.models import File


@pytest.mark.asyncio
async def test_upload_unauth(client):
    fake_file = io.BytesIO(b"fake image")

    response = await client.post(
        "/files/uploads",
        files={"file": ("test_image.jpg", fake_file, "image/jpeg")}
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_success(auth_client: AsyncClient, test_user, mock_get_client):
    mock_file_result = {
        "id": 1,
        "original_filename": "test_image.jpg",
        "stored_filename": "some-uuid.jpg",
        "url": "https://s3.selectel.ru/some-uuid.jpg",
        "bucket": "test-bucket",
        "size": 100,
        "content_type": "image/jpeg",
        "owner_id": test_user.id,
        "created_at": "2024-01-01T00:00:00"
    }

    fake_file = io.BytesIO(b"fake image")

    with patch("app.routers.files.s3_client.get_client", mock_get_client), \
        patch("app.services.storage_s3_selectel.set_file", return_value=mock_file_result):

        response = await auth_client.post(
            "/files/uploads",
            files={"file": ("test_image.jpg", fake_file, "image/jpeg")}
        )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_all_files_success(auth_client, test_files, test_user):
    response = await auth_client.get("/files/all")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_all_files_empty(auth_client):
    response = await auth_client.get("/files/all")

    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_all_files_only_own_files(auth_client, test_files, test_user):
    response = await auth_client.get("/files/all")

    assert response.status_code == 200
    data = response.json()
    for file in data:
        assert file["owner_id"] == test_user.id


async def test_get_all_files_pagination_limit(auth_client, test_files):
    response = await auth_client.get("/files/all?limit=1")
    
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_delete_file_success(auth_client, test_files, test_user, db_session, mock_get_client):
    file_id = test_files[0].id

    with patch("app.routers.files.s3_client.get_client", mock_get_client):
        response = await auth_client.delete(f"/files/{file_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data == {"detail": "File deleted successfully"}

    deleted = await get_file(file_id, db_session)
    assert deleted is None


@pytest.mark.asyncio
async def test_delete_file_not_found(auth_client):
    response = await auth_client.delete("/files/9999")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_other_file(auth_client, test_user, db_session):
    other_file = File(
        original_filename="other.jpg",
        stored_filename="other-uuid.jpg",
        url="https://s3.selectel.ru/other-uuid.jpg",
        bucket="test-bucket",
        size=100,
        content_type="image/jpeg",
        owner_id=99999,
        created_at=datetime.now()
    )
    db_session.add(other_file)
    await db_session.commit()

    response = await auth_client.delete(f"/files/{other_file.id}")

    assert response.status_code == 403
    assert response.json()['detail'] == 'Forbidden'


@pytest.mark.asyncio
async def test_delete_file_unauth(client, test_files):
    file_id = test_files[0].id
    response = await client.delete(f"/files/{file_id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_meta_success(auth_client, test_files):
    file_id = test_files[0].id
    response = await auth_client.get(f"/files/{file_id}")

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_meta_not_found(auth_client):
    response = await auth_client.get("/files/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_meta_only_own(auth_client, test_files, test_user):
    file_id = test_files[0].id
    response = await auth_client.get(f"/files/{file_id}")

    assert response.status_code == 200
    data = response.json()
    assert data['owner_id'] == test_user.id


@pytest.mark.asyncio
async def test_meta_unauth(client, test_files):
    file_id = test_files[0].id
    response = await client.get(f"/files/{file_id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_download_file_success(auth_client, test_files, mock_get_client):
    file = test_files[0]
    fake_content = b"fake file content"

    async def mock_download(stored_filename):
        yield fake_content

    with patch("app.routers.files.s3_client.download_file", mock_download):
        response = await auth_client.get(f"/files/{file.id}/download")

    assert response.status_code == 200
    assert response.content == fake_content


@pytest.mark.asyncio
async def test_download_file_headers(auth_client, test_files):
    file = test_files[0]

    async def mock_download(stored_filename):
        yield b"content"

    with patch("app.routers.files.s3_client.download_file", mock_download):
        response = await auth_client.get(f"/files/{file.id}/download")

    assert response.headers["content-type"] == file.content_type
    assert f"filename={file.original_filename}" in response.headers["content-disposition"]
    assert response.headers["content-length"] == str(file.size)


@pytest.mark.asyncio
async def test_download_file_not_found(auth_client):
    response = await auth_client.get("/files/99999/download")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_download_file_forbidden(auth_client, db_session):
    other_file = File(
        original_filename="other.jpg",
        stored_filename="other-uuid.jpg",
        url="https://s3.selectel.ru/other-uuid.jpg",
        bucket="test-bucket",
        size=100,
        content_type="image/jpeg",
        owner_id=99999,
        created_at=datetime.now(),
    )
    db_session.add(other_file)
    await db_session.commit()

    response = await auth_client.get(f"/files/{other_file.id}/download")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_download_file_unauthorized(client, test_files):
    file_id = test_files[0].id
    response = await client.get(f"/files/{file_id}/download")
    assert response.status_code == 401
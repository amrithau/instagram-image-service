# tests/test_image_router.py

from fastapi.testclient import TestClient


def get_test_client():

    from main import app

    return TestClient(app)


def upload_sample_image(client):

    files = {
        "file": (
            "sample.jpg",
            b"fake-image-content",
            "image/jpeg"
        )
    }

    response = client.post(
        "/images?user_id=user1&title=sunset&tags=nature,travel",
        files=files
    )

    return response


def test_upload_image_success():

    client = get_test_client()

    response = upload_sample_image(client)

    assert response.status_code == 201

    data = response.json()

    assert "image_id" in data
    assert data["message"] == "uploaded successfully"


def test_upload_image_missing_file():

    client = get_test_client()

    response = client.post(
        "/images?user_id=user1&title=sunset&tags=nature"
    )

    assert response.status_code == 422


def test_upload_invalid_file_type():

    client = get_test_client()

    files = {
        "file": (
            "sample.txt",
            b"invalid-content",
            "text/plain"
        )
    }

    response = client.post(
        "/images?user_id=user1&title=test&tags=test",
        files=files
    )

    assert response.status_code == 400

    data = response.json()

    assert data["detail"] == "Invalid image type"


def test_list_images():

    client = get_test_client()

    upload_sample_image(client)

    response = client.get(
        "/images"
    )

    assert response.status_code == 200

    data = response.json()

    assert "items" in data
    assert len(data["items"]) >= 1


def test_list_images_filter_by_user():

    client = get_test_client()

    files = {
        "file": (
            "sample.jpg",
            b"fake-image-content",
            "image/jpeg"
        )
    }

    client.post(
        "/images?user_id=user1&title=sunset&tags=nature",
        files=files
    )

    client.post(
        "/images?user_id=user2&title=beach&tags=travel",
        files=files
    )

    response = client.get(
        "/images?user_id=user1"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) >= 1
    assert data["items"][0]["user_id"] == "user1"


def test_list_images_filter_by_tag():

    client = get_test_client()

    files = {
        "file": (
            "sample.jpg",
            b"fake-image-content",
            "image/jpeg"
        )
    }

    client.post(
        "/images?user_id=user1&title=sunset&tags=nature,travel",
        files=files
    )

    client.post(
        "/images?user_id=user2&title=city&tags=urban",
        files=files
    )

    response = client.get(
        "/images?tag=nature"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) >= 1
    assert "nature" in data["items"][0]["tags"]


def test_pagination():

    client = get_test_client()

    files = {
        "file": (
            "sample.jpg",
            b"fake-image-content",
            "image/jpeg"
        )
    }

    for i in range(5):

        client.post(
            f"/images?user_id=user1&title=image{i}&tags=test",
            files=files
        )

    response = client.get(
        "/images?limit=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) <= 2


def test_get_image_success():

    client = get_test_client()

    upload_response = upload_sample_image(client)

    image_id = upload_response.json()["image_id"]

    response = client.get(
        f"/images/{image_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["image_id"] == image_id
    assert "download_url" in data


def test_get_image_not_found():

    client = get_test_client()

    response = client.get(
        "/images/invalid-image-id"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Image not found"


def test_delete_image_success():

    client = get_test_client()

    upload_response = upload_sample_image(client)

    image_id = upload_response.json()["image_id"]

    response = client.delete(
        f"/images/{image_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Image deleted successfully"


def test_delete_image_not_found():

    client = get_test_client()

    response = client.delete(
        "/images/invalid-image-id"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Image not found"
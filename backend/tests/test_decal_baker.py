from pathlib import Path

import pytest
from fastapi import HTTPException, status

from app.services.decal_baker import DecalBakeService


def decal_service() -> DecalBakeService:
    return object.__new__(DecalBakeService)


def test_bake_skips_when_design_has_no_stickers(tmp_path: Path) -> None:
    service = decal_service()

    assert service.bake(tmp_path / "missing.glb", tmp_path, {"stickers": []}) is False


def test_prepare_stickers_decodes_svg_data_uri_and_normalizes_legacy_fields(tmp_path: Path) -> None:
    service = decal_service()
    config = {
        "stickers": [
            {
                "id": "sticker 001",
                "type": "image",
                "imageUrl": "data:image/svg+xml;utf8,%3Csvg%20xmlns%3D%22http%3A//www.w3.org/2000/svg%22/%3E",
                "position": [1, 2, 3],
                "rotation": [0, 1.57, 0],
                "scale": 0.35,
            }
        ]
    }

    stickers = service._prepare_stickers(tmp_path, config)

    assert len(stickers) == 1
    assert stickers[0]["id"] == "sticker_001"
    assert stickers[0]["mimeType"] == "image/svg+xml"
    assert stickers[0]["width"] == pytest.approx(0.35)
    assert stickers[0]["height"] == pytest.approx(0.35)
    assert stickers[0]["projectionDepth"] == pytest.approx(0.525)
    assert Path(stickers[0]["imagePath"]).read_text(encoding="utf-8").startswith("<svg")


def test_prepare_stickers_rejects_remote_images(tmp_path: Path) -> None:
    service = decal_service()

    with pytest.raises(HTTPException) as exc:
        service._prepare_stickers(
            tmp_path,
            {
                "stickers": [
                    {
                        "id": "remote",
                        "type": "image",
                        "imageUrl": "https://example.com/sticker.png",
                        "position": [0, 0, 0],
                        "rotation": [0, 0, 0],
                        "scale": 0.2,
                    }
                ]
            },
        )

    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST

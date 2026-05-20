from app.db.database import SessionLocal
from app.models import ScanStatus
from app.services.reconstruction import ReconstructionService
from app.services.scan_sessions import ScanSessionService


def process_scan_session(scan_session_id: str) -> None:
    db = SessionLocal()
    try:
        ReconstructionService(db).process(scan_session_id)
    except Exception as exc:
        message = str(exc)
        status = (
            ScanStatus.TOOLCHAIN_UNAVAILABLE
            if message.startswith("Reconstruction is not ready:")
            else ScanStatus.FAILED
        )
        ScanSessionService(db).set_status(scan_session_id, status, message)
    finally:
        db.close()

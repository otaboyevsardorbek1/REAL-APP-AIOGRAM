import os, base64, json, hashlib, uuid, sys
from pathlib import Path
from dotenv import load_dotenv
from PIL import Image
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask

# ✅ Python versiyasini avtomatik tekshiramiz
if sys.version_info < (3, 10):
    from typing import Optional
    QRLogoType = Optional[str]
else:
    QRLogoType = str | None

load_dotenv()
QR_FOLDER = os.getenv("QR_FOLDER", "qr_codes")
Path(QR_FOLDER).mkdir(parents=True, exist_ok=True)

def make_token() -> str:
    """Short unique token (URL-safe)"""
    return uuid.uuid4().hex[:22]

def encode_payload(key: str) -> str:
    """Base64 URL-safe encoder (shorten payload)"""
    b = key.encode("utf-8")
    return base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")

def decode_payload(payload: str) -> str:
    """Decode base64 payload safely"""
    try:
        padding = '=' * (-len(payload) % 4)
        data = base64.urlsafe_b64decode(payload + padding)
        return data.decode("utf-8")
    except Exception:
        return payload

def generate_qr_image(link: str, filename: str, logo_path: QRLogoType = None) -> str:
    img = qrcode.make(link)
    out_path = os.path.join(QR_FOLDER, filename)
    img.save(out_path)

    # Paste logo if provided
    if logo_path and os.path.exists(logo_path):
        try:
            qr = Image.open(out_path).convert("RGBA")
            logo = Image.open(logo_path).convert("RGBA")
            w, h = qr.size
            logo_size = (w // 4, h // 4)
            logo.thumbnail(logo_size)
            lx = (w - logo.size[0]) // 2
            ly = (h - logo.size[1]) // 2
            qr.paste(logo, (lx, ly), logo)
            qr.save(out_path)
        except Exception as e:
            print("Logo paste failed:", e)
    return out_path

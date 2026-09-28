"""QR image rendering (deskapk generator goes here). Falls back gracefully without libraries."""
def qr_photo(data: str, size: int = 260):
    try:
        import qrcode
        from PIL import ImageTk
        img = qrcode.make(data).convert("RGB").resize((size, size))
        return ImageTk.PhotoImage(img)
    except Exception:
        return None   # UI shows the token text instead

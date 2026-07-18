from io import BytesIO

import qrcode
from aiogram.types import BufferedInputFile


class QRService:

    @staticmethod
    def generate(data: str) -> BufferedInputFile:
        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=2,
        )

        qr.add_data(data)
        qr.make(fit=True)

        image = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)

        return BufferedInputFile(
            buffer.read(),
            filename="vpn_qr.png",
        )


qr_service = QRService()
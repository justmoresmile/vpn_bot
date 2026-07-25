from io import BytesIO

import qrcode


class QRService:

    @staticmethod
    def generate(data: str) -> BytesIO:

        qr = qrcode.QRCode(
            version=1,
            box_size=10,
            border=2,
        )

        qr.add_data(data)

        qr.make(fit=True)

        image = qr.make_image(
            fill_color="black",
            back_color="white",
        )

        buffer = BytesIO()

        image.save(
            buffer,
            format="PNG",
        )

        buffer.seek(0)

        return buffer


qr_service = QRService()
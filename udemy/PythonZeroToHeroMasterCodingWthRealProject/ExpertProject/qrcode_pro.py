import qrcode as pyqr

def qrcode_maker(data):
    qr = pyqr.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    picture = qr.make_image()
    picture.save('qrcode.png')
    print('QR code generated successfully!')

qrcode_maker('https://youtu.be/ksfH7W7N9w4?si=1f8HuA3iDk2iXHAL')
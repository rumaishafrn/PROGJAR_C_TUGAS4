import sys
import os
import uuid
from glob import glob
from datetime import datetime


class HttpServer:
    def __init__(self):
        self.sessions = {}
        self.types = {
            '.pdf': 'application/pdf',
            '.jpg': 'image/jpeg',
            '.txt': 'text/plain',
            '.html': 'text/html',
            '.png': 'image/png',
            '.json': 'application/json'
        }

    def response(self, kode=404, message='Not Found', messagebody=bytes(), headers={}):
        tanggal = datetime.now().strftime('%c')
        resp = []
        resp.append("HTTP/1.0 {} {}\r\n".format(kode, message))
        resp.append("Date: {}\r\n".format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n".format(len(messagebody)))
        for kk in headers:
            resp.append("{}: {}\r\n".format(kk, headers[kk]))
        resp.append("\r\n")

        response_headers = ''.join(resp)
        if type(messagebody) is not bytes:
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
        return response

    def proses(self, data):
        # Pisah antara header dan body (jika POST)
        parts = data.split('\r\n\r\n', 1)
        header_part = parts[0]
        body_part = parts[1] if len(parts) > 1 else ''

        requests = header_part.split("\r\n")
        baris = requests[0]
        all_headers = [n for n in requests[1:] if n != '']

        j = baris.split(" ")
        try:
            method = j[0].upper().strip()
            if method == 'GET':
                object_address = j[1].strip()
                return self.http_get(object_address, all_headers)
            if method == 'POST':
                object_address = j[1].strip()
                return self.http_post(object_address, all_headers, body_part)
            else:
                return self.response(400, 'Bad Request', '', {})
        except IndexError:
            return self.response(400, 'Bad Request', '', {})

    def http_get(self, object_address, headers):
        thedir = './'
        if object_address == '/':
            return self.response(200, 'OK', 'Ini Adalah web Server percobaan', {})

        if object_address == '/video':
            return self.response(302, 'Found', '', {'Location': 'https://youtu.be/katoxpnTf04'})

        if object_address == '/santai':
            return self.response(200, 'OK', 'santai saja', {})

        if object_address == '/list':
            # List file di direktori
            files = [f for f in os.listdir(thedir) if os.path.isfile(os.path.join(thedir, f))]
            list_text = "\n".join(files)
            return self.response(200, 'OK', list_text, {'Content-Type': 'text/plain'})

        # Jika akses file biasa
        object_address = object_address[1:]
        fullpath = os.path.join(thedir, object_address)
        if not os.path.isfile(fullpath):
            return self.response(404, 'Not Found', 'File tidak ditemukan', {'Content-Type': 'text/plain'})
        try:
            with open(fullpath, 'rb') as fp:
                isi = fp.read()
        except Exception as e:
            return self.response(500, 'Internal Server Error', str(e), {'Content-Type': 'text/plain'})

        fext = os.path.splitext(fullpath)[1]
        content_type = self.types.get(fext, 'application/octet-stream')

        headers = {'Content-Type': content_type}
        return self.response(200, 'OK', isi, headers)

    def http_post(self, object_address, headers, body):
        thedir = './'
        if object_address == '/upload':
            # Body adalah isi file, nama file harus dari header atau default nama random
            # Cari header Content-Disposition filename jika ada (atau buat default nama)
            filename = None
            for h in headers:
                if h.lower().startswith('content-disposition'):
                    # Contoh: Content-Disposition: form-data; name="file"; filename="test.txt"
                    parts = h.split(';')
                    for p in parts:
                        p = p.strip()
                        if p.startswith('filename='):
                            filename = p.split('=')[1].strip('"')
            if not filename:
                filename = f'upload_{uuid.uuid4().hex}.bin'

            try:
                with open(os.path.join(thedir, filename), 'wb') as f:
                    f.write(body.encode() if isinstance(body, str) else body)
                return self.response(200, 'OK', f'File {filename} berhasil diupload', {'Content-Type': 'text/plain'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'Gagal upload file: {str(e)}', {'Content-Type': 'text/plain'})

        if object_address == '/delete':
            # Menghapus file. Nama file di body (plain text)
            filename = body.strip()
            fullpath = os.path.join(thedir, filename)
            if not os.path.isfile(fullpath):
                return self.response(404, 'Not Found', f'File {filename} tidak ditemukan', {'Content-Type': 'text/plain'})
            try:
                os.remove(fullpath)
                return self.response(200, 'OK', f'File {filename} berhasil dihapus', {'Content-Type': 'text/plain'})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'Gagal menghapus file: {str(e)}', {'Content-Type': 'text/plain'})

        return self.response(400, 'Bad Request', 'Invalid POST endpoint', {'Content-Type': 'text/plain'})



if __name__ == "__main__":
    httpserver = HttpServer()
    d = httpserver.proses('GET /list HTTP/1.0\r\n\r\n')
    print(d.decode())

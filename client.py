import sys
import socket
import logging


server_address = ('localhost', 8889)  # sesuaikan dengan server thread pool
# server_address = ('localhost', 8889)  # jika pakai process pool


def make_socket(destination_address='localhost', port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")


def send_command(command_str):
    alamat_server = server_address[0]
    port_server = server_address[1]

    sock = make_socket(alamat_server, port_server)

    try:
        logging.warning("sending message")
        sock.sendall(command_str.encode())
        logging.warning(command_str)

        data_received = ""
        while True:
            data = sock.recv(2048)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break

        return data_received
    except Exception as ee:
        logging.warning(f"error during data receiving {str(ee)}")
        return False


def list_files():
    cmd = "GET /list HTTP/1.1\r\nHost: localhost\r\n\r\n"
    hasil = send_command(cmd)
    print("Daftar file di server:")
    print(hasil)


def upload_file(filepath):
    try:
        with open(filepath, "rb") as f:
            isi = f.read()
    except Exception as e:
        print(f"Gagal baca file {filepath}: {e}")
        return

    filename = filepath.split("/")[-1]

    cmd = (
        "POST /upload HTTP/1.1\r\n"
        "Host: localhost\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Length: {len(isi)}\r\n"
        "\r\n"
    )

    try:
        sock = make_socket(server_address[0], server_address[1])
        sock.sendall(cmd.encode() + isi)

        data_received = ""
        while True:
            data = sock.recv(2048)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break

        print("Response upload file:", data_received)
    except Exception as e:
        print(f"Gagal upload file: {e}")
    finally:
        sock.close()


def delete_file(filename):
    body = filename + "\r\n"

    cmd = (
        "POST /delete HTTP/1.1\r\n"
        "Host: localhost\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"
        + body
    )

    hasil = send_command(cmd)
    print(f"Response hapus file '{filename}':")
    print(hasil)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Client untuk HTTP Server sederhana")
    parser.add_argument("action", choices=["list", "upload", "delete"], help="aksi yang dilakukan")
    parser.add_argument("--file", help="file path untuk upload atau delete")

    args = parser.parse_args()

    if args.action == "list":
        list_files()
    elif args.action == "upload":
        if not args.file:
            print("Perlu --file untuk upload")
        else:
            upload_file(args.file)
    elif args.action == "delete":
        if not args.file:
            print("Perlu --file untuk delete (nama file di server)")
        else:
            delete_file(args.file)

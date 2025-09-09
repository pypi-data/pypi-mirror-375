import json
import socket


def requesttobyte(path, content_type="json", method="get", body=None, host="localhost"):
    method = method.upper()
    if not path.startswith("/"):
        path = "/" + path

    if content_type == "json":
        mime = "application/json"
    elif content_type == "form":
        mime = "application/x-www-form-urlencoded"
    else:
        mime = "text/plain"

    body = body or ""
    if isinstance(body, dict):
        import json
        body = json.dumps(body)

    if not isinstance(body, str):
        raise TypeError("Body must be a str or dict")

    body_bytes = body.encode("utf-8")
    content_length = len(body_bytes)

    headers = [
        f"{method} {path} HTTP/1.1",
        f"Host: {host}",
        f"Content-Type: {mime}",
        f"Content-Length: {content_length}",
        "",  # end of headers
        ""  # body follows here
    ]

    request_str = "\r\n".join(headers)
    full_request = request_str.encode("utf-8") + body_bytes
    return full_request


def request(host, port, endpoint):

 # Create a socket
 s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 s.connect((host, port))

# Send HTTP GET request
 request = f"GET {endpoint} HTTP/1.1\r\nHost: {host}\r\nAccept: application/json\r\nConnection: close\r\n\r\n"
 s.sendall(request.encode())

# Receive response
 response = b""
 while True:
     part = s.recv(4096)
     if not part:
         break
     response += part

 s.close()

 # Decode response
 response_text = response.decode('utf-8', errors='replace')  # be gentle with decoding

 # Split headers and body
 header_text, _, body = response_text.partition('\r\n\r\n')

 # Optional: print headers if curious
 # print(header_text)
 status_line = response_text.split('\r\n')[0]
 print("Status Line:", status_line)

 # Extract and print status code
 status_code = int(status_line.split()[1])
 print("Status Code:", status_code)
 # Parse JSON body
 try:
     data = json.loads(body)
     print("Parsed JSON:", data)
 except json.JSONDecodeError as e:
     print("Failed to parse JSON:", e)
     print("Raw body:", body)
     data = None
 return data , status_code
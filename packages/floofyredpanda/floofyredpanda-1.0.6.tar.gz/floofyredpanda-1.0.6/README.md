# update: 1.0.6
### added requesttobyte 



# to install
```bash
pip install floofyredpanda
```

# to use

```python
from floofyredpanda import start_floofy_server

def handle(conn, addr):
    conn.send(b"bonk\n")
    conn.close()

start_floofy_server(9000, handle)
```


## ssl

```python
from floofyredpanda import ParanoidPanda

def handle_secure(conn, addr):
    conn.send(b"secure bonk\n")
    conn.close()

server = Paranoid_Panda(port=4443, handler=handle_secure, cert="cert.pem", key="key.pem")
server.start_paranoid_server()


```


## client side

```python
from floofyredpanda import tell_the_server

response = tell_the_server("localhost", 9000, "bonk")
print(response)

```
## ssl
```python
from floofyredpanda import secretly_tell_the_server

response = secretly_tell_the_server("localhost", 9000, "secret bonk") # ca is required to load selfsigned stuff response = secretly_tell_the_server("localhost", 9000, "secret bonk" ca = "the content of the ca.pem here")
print(response)

```
## requesttobyte
```python
from floofyredpanda import RedPandaClient, requesttobyte
castr = """the base64 of your ca pem here unfortunately it is
           required for https even if you dont need a ca since
           its a public site but its required to use ssl i will add just a tls = True or False in the future"""
s = RedPandaClient("www.example.com",443,ca = castr)
x = requesttobyte("/",host = "www.example.com",method = "get")
s.send(x.decode()) # you need to decode again because im stupid and encode everything that is in that queue
print(next(s.recv()))
```
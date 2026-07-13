import socket,importlib.util,sys
# from diffie_heilman import genRandPrime,genCand,genPKey
# from aes import key_schedule, encryption, decryption, handle_key,to_ascii
# from config import key,host,port,mode
import re,os
from PIL import Image
from pathlib import Path

current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "2105084_aes.py")

module_name = "2105084_aes"

spec = importlib.util.spec_from_file_location(module_name, file_path)
aes_module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = aes_module
spec.loader.exec_module(aes_module)

key_schedule = aes_module.key_schedule
remove_pad = aes_module.remove_pad
encryption = aes_module.encryption
decryption = aes_module.decryption
to_hex = aes_module.to_hex
to_ascii = aes_module.to_ascii
pkcs7 = aes_module.pkcs7


file_path = os.path.join(current_dir, "2105084_diffie_heilman.py")

module_name = "2105084_diffie_heilman"

spec = importlib.util.spec_from_file_location(module_name, file_path)
aes_module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = aes_module
spec.loader.exec_module(aes_module)

genRandPrime = aes_module.genRandPrime
genCand = aes_module.genCand
genPKey = aes_module.genPKey


file_path = os.path.join(current_dir, "2105084_config.py")

module_name = "2105084_config"

spec = importlib.util.spec_from_file_location(module_name, file_path)
aes_module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = aes_module
spec.loader.exec_module(aes_module)

key = aes_module.key
host = aes_module.host
port = aes_module.port
mode = aes_module.mode

rand_IV = os.urandom(16)

def for_img(img_path,mode):
    img = Image.open(img_path).convert("RGB")
    width, height = img.size
    pix_bytes = img.tobytes()
    # print(f"Width: {width}, Height: {height}")
    cipher_bytes = encryption(pix_bytes,rand_IV,mode)
    # print("Encryption done")
    clean_cipher = cipher_bytes[:width*height*3]
    cipher_img = Image.frombytes("RGB", (width, height), clean_cipher)
    out_fn = f"cipher_img{mode.upper()}.jpg"
    cipher_img.save(out_fn)
    return cipher_bytes

def for_all(path,mode):
    with open(path, "rb") as f:
        file_bytes = f.read()
    cipher_bytes = encryption(file_bytes, rand_IV, mode)
    return cipher_bytes    

def server():
    p,q = genRandPrime(len(key)*8)
    g = genCand(p,q)
    k_a = genPKey(len(key)*8,p)
    a = pow(g,k_a,p)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"[SERVER] Listening on {host}:{port}...")
        try:
            while True:
                try:
                    c,_ = server_socket.accept()
                except ConnectionAbortedError:
                    print("Connection Closed")
                    break
                c.sendall("Connection Established?".encode('utf-8'))
                r = c.recv(1024).decode('utf-8')
                if re.search("yes",r,re.IGNORECASE):
                    print(f"Alice sending public parameters P,g,A")
                    payload = f"{p},{g},{a}"
                    c.sendall(payload.encode('utf-8'))
                    b = int(c.recv(1024).decode('utf-8'))
                    print(f"Bob sent B: {b}")
                    s_a = pow(b,k_a,p)
                    print("Ready for transmission from server")
                    c.sendall("Ready for transmission from server".encode('utf-8'))
                    r = c.recv(1024).decode('utf-8')
                    if re.search("ready",r,re.IGNORECASE):
                       key_schedule(s_a.to_bytes(len(key),byteorder='big'))
                       choice = input("Would you like to enter text or image/files: ")
                       c.sendall(choice.encode('utf-8'))
                       if re.search("image/files",choice,re.IGNORECASE):
                           pth = input("Enter the image/files path: ")
                           fname = Path(pth).name
                        #    cipher = for_img(pth,mode)
                           cipher = for_all(path=pth,mode=mode)
                           payload = rand_IV + cipher
                           c.sendall(str(f"File:{fname}, Size:{len(payload)}").encode('utf-8'))
                           ack = c.recv(1024).decode('utf-8')
                           if re.search("ack",ack,re.IGNORECASE):
                               
                                c.sendall(payload)
                                continue
                       text = input("Enter the text you want to send: ")
                       tmp = text
                       t_b = text.encode('utf-8')
                    #    print(s_a)
                       
                       cipher = encryption(t_b,rand_IV,mode=mode)
                       payload = rand_IV + cipher
                       c.sendall(payload)
                       c_text = to_ascii(c.recv(1024))
                       print(f"c_text:{c_text}")
                       print(f"tmp:{tmp}")
                       if c_text == tmp:
                           print(f"Confirmed! Bob got the message Alice sent: {tmp}")
                       else:
                           print("There has been some issue")
                           c.shutdown()
                           c.close()
                    else:
                        print("Client didn't send ready")
                        c.shutdown()
                        c.close()        
                elif not r:
                    print("Connection not established!")
                    c.shutdown()
                    c.close()
                    break 
        except KeyboardInterrupt:
            print("\n[SERVER] Terminating terminal... ")

server()
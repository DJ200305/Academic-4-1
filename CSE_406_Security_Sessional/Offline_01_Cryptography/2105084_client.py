import socket,importlib.util,sys
# from diffie_heilman import genRandPrime,genCand,genPKey
# from aes import key_schedule, encryption, decryption, handle_key,to_ascii,remove_pad
import re,os
# from config import key,mode,host,port
from PIL import Image

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

def for_dec_img(decrypted_bytes):
    rec_img = Image.frombytes("RGB", (64, 64), decrypted_bytes)
    out_fn = f"rec_img_{mode.upper()}.jpg"
    rec_img.save(out_fn)

def for_dec_all(decrypted_bytes,fname):
    out_pth = f"rec_{mode.upper()}_{fname}"
    with open(out_pth, "wb") as f:
        f.write(decrypted_bytes)

def client():
    try:
        while True:    
            cmd = input("Press enter to initiate connection or type exit: ")
            if cmd.strip().lower() == 'exit':
                break  
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect((host, port))
                c = client_socket
                
                        
                r = c.recv(1024).decode('utf-8')
                if re.search("established",r,re.IGNORECASE):
                    c.sendall("YES".encode('utf-8'))
                    pl = c.recv(1024).decode('utf-8')
                                # print(str(pl))
                    p_str, g_str, a_str = pl.split(",")
                    p = int(p_str)
                    g = int(g_str)
                    a = int(a_str)
                    k_b = genPKey(len(key)*8,p=p)
                    b = pow(g,k_b,p)
                    c.sendall(str(b).encode('utf-8'))
                    s_b = pow(a,k_b,p)
                    r = c.recv(1024).decode('utf-8')
                    if re.search("transmission",r,re.IGNORECASE):
                        c.sendall("Ready".encode('utf-8'))
                    else:
                        print("No transmission")
                        c.close()
                    key_schedule(s_b.to_bytes(len(key),byteorder='big'))    
                    choice = c.recv(1024).decode('utf-8')
                    if re.search("image/files",choice,re.IGNORECASE):
                        print("Ready for image/files")
                        sz_header = (c.recv(1024).decode('utf-8'))
                        fname = sz_header.split(":")[1].split(",")[0]
                        header = int(sz_header.split(":")[2])
                        # print(header)
                        c.sendall("ack for image/files".encode('utf-8'))
                        payload = b""
                        while len(payload) < header:
                            pkt = c.recv(4096)
                            if not pkt:
                                break
                            payload += pkt
                        rand_IV = payload[:16]
                        cipher = payload[16:]    
                        decrypted_bytes = remove_pad(decryption(cipher,rand_IV, mode))
                        for_dec_all(decrypted_bytes,fname)
                        continue    

                    payload = c.recv(1024)
                    rand_IV = payload[:16]
                    cipher = payload[16:]
                    decrypted_text = to_ascii(remove_pad(decryption(cipher,rand_IV,mode)))
                    print(f"Message from Alice: {decrypted_text}")
                    c.sendall(str(decrypted_text).encode('utf-8'))
                else:
                    print("Connection not established")
                    continue   
    except KeyboardInterrupt:
        print("\n[CLIENT] Terminating terminal... ")

client()
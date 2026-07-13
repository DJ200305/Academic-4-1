import importlib.util
import sys
import os,time,random

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

random.seed(42)
rand_IV = bytes(random.getrandbits(8) for _ in range(16))

def main():
    key = b"BUET CSE20 BATCH"
    text = b"We need picnic"
    mode = "CBC"
    s = time.perf_counter_ns()
    key_schedule(key)
    e = time.perf_counter_ns()
    key_schedule_time = (e-s)/1_000_000.0
    s = time.perf_counter_ns()
    ciphertext = encryption(text,rand_IV,mode)
    e = time.perf_counter_ns()
    enc_time = (e-s)/1_000_000.0
    s = time.perf_counter_ns()
    decrypted_bytes = decryption(ciphertext,rand_IV,mode)
    e = time.perf_counter_ns()
    dec_time = (e-s)/1_000_000.0
    unpad_dec = remove_pad(decrypted_bytes)

    print("KEY: ")
    print(f"IN ASCII: {to_ascii(key)}")
    print(f"IN HEX: {to_hex(key)}")
    print(" ")
    print("Plaintext: ")
    print(f"IN ASCII: {to_ascii(text)}")
    print(f"IN HEX: {to_hex(text)}")
    print(f"IN ASCII (After padding): {to_ascii(pkcs7(text))}")
    print(f"IN HEX (After padding): {to_hex(pkcs7(text))}")
    print(" ")
    print("Ciphertext:")
    print("(IV is the first 16 bytes, followed by the actual ciphertexts)")
    print(f"In HEX: {to_hex(ciphertext)}")
    print(f"In ASCII: {to_ascii(ciphertext)}")
    print("Deciphered text:")
    print("Before Unpadding:")
    print(f"In HEX: {to_hex(decrypted_bytes)}")
    print(f"In ASCII: {to_ascii(decrypted_bytes)}")
    print("After Unpadding:")
    print(f"In HEX: {to_hex(unpad_dec)}")
    print(f"In ASCII: {to_ascii(unpad_dec)}")
    print("Execution Time Details:")
    print(f"Key Schedule Time: {key_schedule_time}")
    print(f"Encryption Time: {enc_time}")
    print(f"Decryption Time: {dec_time}")
main()
    
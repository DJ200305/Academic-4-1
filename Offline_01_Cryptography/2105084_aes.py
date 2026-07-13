from aes_helpers import Sbox, InvSbox, Rcon, Mixer, InvMixer, gf_mult

import os

BLOCK_SIZE = 16
STATE_ROW = 4
STATE_COL = 4
key_dict = {}

def to_hex(text):
    return " ".join(f"{t:02x}" for t in text)

def to_ascii(text):
    return text.decode('latin-1')

def subBytes(s_mat):
    for i in range(STATE_ROW):
        for j in range(STATE_COL):
            s_mat[i][j] = Sbox[s_mat[i][j]] 
    return s_mat
def shiftRows(s_mat):
    for i in range(STATE_ROW):
        s_mat[i] = s_mat[i][i:] + s_mat[i][:i]
    return s_mat

def mixColumns(s_mat):
    mix_mat = [[0] * 4 for _ in range(4)]
    for c in range(4):
        for r in range(4):
            mix_mat[r][c] = (
            gf_mult(Mixer[r][0],s_mat[0][c])^
            gf_mult(Mixer[r][1],s_mat[1][c])^
            gf_mult(Mixer[r][2],s_mat[2][c])^
            gf_mult(Mixer[r][3],s_mat[3][c])
        )  
    return mix_mat   


def key_schedule(key):
    w = []
    for i in range(4):
        w.append(list(key[i*4:(i+1)*4]))
    for i in range(4,44):
        tmp = list(w[i-1])
        if i % 4 == 0:
            tmp = tmp[1:] + tmp[:1]
            for x in range(4):
                tmp[x] = Sbox[tmp[x]]
            tmp[0] ^= Rcon[i//4]
        tr_w = []
        for j in range(4):
            tr_w.append(w[i-4][j] ^ tmp[j])
        w.append(tr_w)
    for round in range(11):
        w_r = w[round*4:(round+1)*4]
        w_mat = [[0] * 4 for _ in range(4)]
        for x in range(STATE_ROW):
            for y in range(STATE_COL):
               w_mat[x][y] = w_r[y][x] 
        key_dict[round] = w_mat

def pkcs7(x):
    pad_len = (BLOCK_SIZE-(len(x) % BLOCK_SIZE))
    pad_x = bytes([pad_len]*pad_len)
    return bytes(x)+pad_x

def handle_key(key):
    if len(key) == 16:
        return key
    elif len(key) > 16:
        return key[:16]
    return pkcs7(key)

def addKeyRound(key,s):
        for r in range(4):
            for c in range(4):
                s[r][c] = s[r][c] ^ key[r][c]
        return s        

def func_smat(block):
    s_mat = [[0] * 4 for _ in range(4)]
    for i in range(BLOCK_SIZE):
        r = i % 4
        c = i // 4
        s_mat[r][c] = block[i]    
    return s_mat

def func_block(s_mat):
    block = []
    for c in range(4):
        for r in range(4):
            block.append(s_mat[r][c])
    return bytes(block)           

def cbc_mode(plain,cipher):
    s_mat = [[0] * 4 for _ in range(4)]
    for i in range(STATE_ROW):
        for j in range(STATE_COL):
           s_mat[i][j] = plain[i][j] ^ cipher[i][j]
    return s_mat       

def prep_text(plaintext):
    blocks = []
    padded_text = pkcs7(plaintext)
    for i in range(0,len(padded_text),BLOCK_SIZE):
        block = padded_text[i:i+BLOCK_SIZE]
        blocks.append(block)
    return blocks    

def prep_cipher(cipher):
    blocks = []
    for i in range(0,len(cipher),BLOCK_SIZE):
        block = cipher[i:i+BLOCK_SIZE]
        blocks.append(block)
    return blocks    

def encryption(plaintext,rand_IV,mode="ECB"):
    round = 10
    blocks = prep_text(plaintext)
    # key_schedule(key)
    
    ciphertexts = []
    prev = func_smat(rand_IV)
    for i in range(len(blocks)):
        if i % 100 == 0 and i > 0:
            print(f"[AES] Processed {i}/{len(blocks)} blocks...")
        block = blocks[i]
        s_mat = func_smat(block)
        if mode.lower() == "cbc":
            s_mat = cbc_mode(s_mat,prev)
        s_mat = addKeyRound(key_dict[0],s_mat)  
        for j in range(1,round,1):
            s_mat = subBytes(s_mat)
            s_mat = shiftRows(s_mat)
            s_mat = mixColumns(s_mat)
            s_mat = addKeyRound(key_dict[j],s_mat)  
        s_mat = subBytes(s_mat)
        s_mat = shiftRows(s_mat)
        s_mat = addKeyRound(key_dict[10],s_mat)
        if mode.lower() == "cbc":
            for r in range(STATE_ROW):
                for c in range(STATE_COL):
                    prev[r][c] = s_mat[r][c]     
        ciphertexts.append(func_block(s_mat))
    return b"".join(ciphertexts)    

def invSubBytes(s_mat):
    for i in range(STATE_ROW):
        for j in range(STATE_COL):
            s_mat[i][j] = InvSbox[s_mat[i][j]] 
    return s_mat
def invShiftRows(s_mat):
    for i in range(STATE_ROW):
        s_mat[i] = s_mat[i][-i:] + s_mat[i][:-i]
    return s_mat    

def invMixColumns(s_mat):
    mix_mat = [[0] * 4 for _ in range(4)]
    for c in range(4):
        for r in range(4):
            mix_mat[r][c] = (
            gf_mult(InvMixer[r][0],s_mat[0][c])^
            gf_mult(InvMixer[r][1],s_mat[1][c])^
            gf_mult(InvMixer[r][2],s_mat[2][c])^
            gf_mult(InvMixer[r][3],s_mat[3][c])
        )  
    return mix_mat

def remove_pad(d_text):
    pad_len = d_text[-1]
    pad_bytes = d_text[-pad_len:]
    expected = bytes([pad_len]*pad_len)
    # print(f"Expected len: {len(expected)}")
    # print(f"With pad len: {len(pad_bytes)}")
    if pad_bytes != expected:
        raise ValueError("Padding Corrupted")
    return d_text[:-pad_len]

def decryption(cipher,rand_IV,mode="ECB"):
    round = 10
    cipherBlocks = prep_cipher(cipher)
    plaintexts = []
    prev = func_smat(rand_IV)
    for i in range(len(cipherBlocks)):
        # print(f"DEBUG [{mode}]: Decrypting exactly {len(cipherBlocks)} blocks.")
        if i % 100 == 0 and i > 0:
            print(f"[AES] Processed {i}/{len(cipherBlocks)} blocks...")
        block = cipherBlocks[i]
        s_mat = func_smat(block)
        org = [[0] * 4 for _ in range(4)]
        for x in range(STATE_ROW):
            for y in range(STATE_COL):
                org[x][y] = s_mat[x][y]
        s_mat = addKeyRound(key_dict[10], s_mat)
        s_mat = invShiftRows(s_mat)
        s_mat = invSubBytes(s_mat)
        for j in range(9,0,-1):
            s_mat = addKeyRound(key_dict[j],s_mat)
            s_mat = invMixColumns(s_mat)
            s_mat = invShiftRows(s_mat)
            s_mat = invSubBytes(s_mat)
        s_mat = addKeyRound(key_dict[0], s_mat)
        if mode.lower() == "cbc":
            s_mat = cbc_mode(s_mat,prev)  
            for x in range(STATE_ROW):
                for y in range(STATE_COL):
                    prev[x][y] = org[x][y]
        plaintexts.append((func_block(s_mat)))
    return (b"".join(plaintexts))            
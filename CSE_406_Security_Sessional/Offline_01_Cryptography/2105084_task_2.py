import importlib.util
import sys,os


current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, "2105084_diffie_heilman.py")

module_name = "2105084_diffie_heilman"

spec = importlib.util.spec_from_file_location(module_name, file_path)
aes_module = importlib.util.module_from_spec(spec)
sys.modules[module_name] = aes_module
spec.loader.exec_module(aes_module)

genRandPrime = aes_module.genRandPrime
genCand = aes_module.genCand
genPKey = aes_module.genPKey


# from diffie_heilman import genRandPrime,genCand,genPKey
import time,random
def main():
    key = b"BUET CSE20 BATCH"
    key_bits = "".join(f"{i:08b}" for i in key)
    # t = time.time()
    # gen_prime,q = genRandPrime(len(key_bits))
    # t = time.time()
    # gen_cand = genCand(gen_prime,q)
    report = {}
    for i in [128,192,256]:
       random.seed(42)
       gen_prime,q = genRandPrime(i)
       gen_cand = genCand(gen_prime,q)
       t_a = 0
       t_b = 0
       t_s = 0
       issue = False
       for _ in range(5):
           k_a = genPKey(i,gen_prime)
           k_b = genPKey(i,gen_prime)
           s = time.perf_counter_ns()
           a = pow(gen_cand,k_a,gen_prime)
           e = time.perf_counter_ns()
           t_a += (e-s) / 1_000_000.0
           s = time.perf_counter_ns()
           b = pow(gen_cand,k_b,gen_prime)
           e = time.perf_counter_ns()
           t_b += (e-s) / 1_000_000.0
           s = time.perf_counter_ns() 
           s_a = pow(b,k_a,gen_prime)
           s_b = pow(a,k_b,gen_prime)
           if s_a != s_b:
               issue = True
               break
           e = time.perf_counter_ns()
           t_s += (e-s) / 1_000_000.0
       if issue:
           print("Terminating! Shared key mismatch!")
           return -1   
       avg_a = t_a / 5
       avg_b = t_b / 5
       avg_s = t_s / 5
       report[f"{i}"] = [avg_a,avg_b,avg_s]
    print("Key       A                    B             shared key s")
    for key,vals in report.items():
       print(f"{key}       {vals[0]:.4f}             {vals[1]:.4f}           {vals[2]:.4f}")            

main()
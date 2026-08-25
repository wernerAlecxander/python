import socket
import struct
from concurrent.futures import ThreadPoolExecutor

# Ajuste para a faixa de IPs do seu escritório
base_ip = "192.168.4.1"

# Pacote hexadecimal padrão para negociar protocolo SMBv1 (SMB_COM_NEGOTIATE)
# Esse cabeçalho força o servidor a dizer se ainda fala o dialeto SMB 1.0
MENSAGEM_SMBv1 = (
    b"\x00\x00\x00\x2f\xff\x53\x4d\x42\x72\x00\x00\x00\x00\x18\x53\xc8"
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xfe"
    b"\x00\x00\x40\x00\x00\x0c\x00\x02\x4e\x54\x20\x4c\x4d\x20\x30\x2e"
    b"\x12\x00"
)

def checar_smbv1(ip):
    try:
        # Cria uma conexão direta com a porta de compartilhamento (445)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1.5)
            s.connect((ip, 445))
            
            # Envia o pacote solicitando conexão SMBv1
            s.sendall(MENSAGEM_SMBv1)
            resposta = s.recv(1024)
            
            # Analisa o cabeçalho de resposta do protocolo
            # O cabeçalho padrão de um pacote SMB válido começa com \xffSMB (ou)
            if len(resposta) >= 8 and resposta[4:8] == b"\xffSMB":
                # O comando correspondente a negociação bem-sucedida é o byte \x72 na posição 8
                if resposta[8] == 0x72:
                    print(f"[ALERTA CRÍTICO] IP: {ip} possui o protocolo SMBv1 ATIVO e está vulnerável!")
                    return
            
            print(f"[SEGURO] IP: {ip} respondeu em SMB moderno (SMBv2/v3).")
    except (socket.timeout, ConnectionRefusedError):
        # Dispositivo offline ou com a porta 445 fechada no Firewall
        pass
    except Exception:
        pass

print(f"Iniciando varredura em busca de SMBv1 na rede {base_ip}0/24...")
print("Aguarde, analisando respostas dos dispositivos...")

# Executa o teste em paralelo para varrer os 254 IPs rapidamente
with ThreadPoolExecutor(max_workers=60) as executor:
    for i in range(1, 255):
        executor.submit(checar_smbv1, f"{base_ip}{i}")

print("Varredura de protocolo encerrada.")

import socket
import struct

target = "192.168.4.19"
port = 137

# Pacote NetBIOS Node Status Request padrão (Equivalente ao nmblookup -A)
# Esse pacote solicita a tabela de nomes que a máquina registrou na rede
netbios_request = (
    b"\x80\x64"  # Transaction ID
    b"\x00\x00"  # Flags (Query padrão)
    b"\x00\x01"  # Question Count (1)
    b"\x00\x00"  # Answer Count
    b"\x00\x00"  # Authority Count
    b"\x00\x00"  # Additional Count
    # Nome da pergunta: CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA (Status do nó)
    b"\x20\x43\x4b\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41"
    b"\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41\x41"
    b"\x41\x00"
    b"\x00\x21"  # Tipo: NBSTAT
    b"\x00\x01"  # Classe: IN
)

print(
    f"[*] Enviando requisição NetBIOS via UDP para {target}:{port} (Simulando SMB-OS-Discover)..."
)

try:
    # Criamos um socket UDP (SOCK_DGRAM)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3.0)

    # Envia o pacote UDP direto para o alvo
    s.sendto(netbios_request, (target, port))
    data, addr = s.recvfrom(1024)
    s.close()

    print("[+] Resposta recebida da máquina alvo!")
    print("-" * 60)

    # O cabeçalho da resposta NetBIOS tem 56 bytes fixos antes dos nomes
    if len(data) > 56:
        num_names = data[56]  # Número de registros retornados
        offset = 57

        print(f"Resultados de Descoberta para {target}:")

        for _ in range(num_names):
            if offset + 18 > len(data):
                break

            # Cada nome NetBIOS tem exatamente 15 caracteres + 1 byte de tipo + 2 bytes de flags
            name_bytes = data[offset : offset + 15]
            name_type = data[offset + 15]
            name = name_bytes.decode("utf-8", errors="ignore").strip()

            # Traduz os sufixos padrão do Windows (Tipos de Registro NetBIOS)
            if name_type == 0x00:
                print(f"  |-> Nome da Máquina (Workstation): {name}")
            elif name_type == 0x20:
                print(f"  |-> Serviço Ativo (File Server SMB): {name}")
            elif name_type == 0x1E or name_type == 0x1D:
                print(f"  |-> Grupo de Trabalho / Domínio: {name}")
            elif name_type == 0x03:
                print(f"  |-> Usuário Logado na Máquina: {name}")

            offset += 18  # Avança para o próximo nome na tabela

        # Extrai o endereço MAC que o Windows envia no final do pacote NetBIOS
        if offset + 6 <= len(data):
            mac_bytes = data[offset : offset + 6]
            mac_address = ":".join(f"{b:02x}" for b in mac_bytes)
            print(f"  |-> Endereço MAC de Origem: {mac_address}")

        print("-" * 60)
    else:
        print("[-] Resposta inválida ou incompleta recebida.")

except socket.timeout:
    print("[-] Erro: Timeout total. A porta UDP 137 também está bloqueada.")
except Exception as e:
    print(f"[-] Ocorreu um erro: {e}")

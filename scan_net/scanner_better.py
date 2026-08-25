import struct
import socket

target = "192.168.4.19"
port = 445

# Pacote binário de negociação SMBv1 (padrão para extrair dados de SO)
smb_negotiate_packet = (
    b"\x00\x00\x00\x55"  # NetBIOS Session Service (Tamanho)
    b"\xff\x53\x4d\x42"  # Protocolo: \xffSMB
    b"\x72"  # Comando: Negotiate Protocol
    b"\x00\x00\x00\x00"  # Status
    b"\x18"  # Flags
    b"\x53\xc8"  # Flags2 (Suporta Unicode)
    b"\x00\x00"  # PID High
    b"\x00\x00\x00\x00\x00\x00\x00\x00"  # Signature
    b"\x00\x00"  # Reserved
    b"\x00\x00"  # TID
    b"\x00\x00"  # PID
    b"\x00\x00"  # UID
    b"\x00\x00"  # MID
    b"\x00"  # Word Count
    b"\x32\x00"  # Byte Count
    # Dialetos suportados (NT LM 0.12 é o que expõe o S.O.)
    b"\x02\x4c\x41\x4e\x4d\x41\x4e\x31\x2e\x30\x00"
    b"\x02\x4c\x4d\x31\x2e\x32\x00"
    b"\x02\x4e\x54\x20\x4c\x4d\x20\x30\x2e\x31\x32\x00"
)

print(f"[*] Conectando a {target}:{port} para simular 'smb-os-discover'...")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    s.connect((target, port))

    # Envia o pacote de negociação SMB
    s.send(smb_negotiate_packet)
    response = s.recv(1024)
    s.close()

    if len(response) > 0:
        print("[+] Resposta recebida do servidor SMB!")
        print("-" * 50)

        # Tenta extrair strings em formato Unicode (padrão do Windows)
        # Filtra os bytes nulos normais do Unicode para tornar o texto legível
        strings_encontradas = []
        temp_str = ""

        # Varre os dados decodificando o que for texto utilizável
        for b in response:
            if 32 <= b <= 126:  # Caracteres ASCII imprimíveis
                temp_str += chr(b)
            elif b == 0:
                if len(temp_str) > 1:
                    strings_encontradas.append(temp_str)
                temp_str = ""

        # Limpa e exibe os dados coletados (Simulando o output do Nmap)
        print(f"Alvo: {target}\n")
        print("Resultados do Script SMB-OS-Discover Simulado:")

        # Tenta categorizar o que o Windows jogou no pacote
        for item in strings_encontradas:
            if item in ["NT LM 0.12", "Windows", "LM1.2", "LANMAN1.0"]:
                continue
            if (
                "Windows" in item
                or "Server" in item
                or "Version" in item
                or "." in item
            ):
                print(f"  |  S.O. Provável: {item}")
            elif len(item) > 2:
                print(f"  |  Nome da Máquina / Domínio detectado: {item}")

        print("-" * 50)
    else:
        print("[-] O servidor fechou a conexão sem enviar dados.")

except Exception as e:
    print(f"[-] Erro ao conectar ou extrair dados: {e}")

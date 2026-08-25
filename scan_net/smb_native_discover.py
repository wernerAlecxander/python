import socket
import struct

target = "192.168.4.19"
port = 445

# Pacote estruturado manualmente simulando a negociação oficial do Windows 10/11
# Contém os dialetos modernos (SMB 2.x e SMB 3.x) exigidos pelos firewalls internos
smb3_negotiate_payload = (
    b"\xfe\x53\x4d\x42"  # Protocol ID: \xfeSMB
    b"\x40\x00"  # Structure Size (64 bytes fixos do cabeçalho)
    b"\x00\x00"  # Credit Charge
    b"\x00\x00\x00\x00"  # Status
    b"\x00\x00"  # Command: Negotiate (0)
    b"\x00\x00"  # Credits Requested
    b"\x00\x00\x00\x00"  # Flags
    b"\x00\x00\x00\x00"  # Next Command
    b"\x01\x00\x00\x00\x00\x00\x00\x00"  # Message ID: 1
    b"\xfe\xdc\xba\x98"  # Process ID fictício
    b"\x00\x00\x00\x00"  # Tree ID
    b"\x00\x00\x00\x00\x00\x00\x00\x00"  # Session ID
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # Signature
    # --- Corpo da Requisição de Negociação ---
    b"\x24\x00"  # Structure Size (36)
    b"\x05\x00"  # Dialect Count: 5 dialetos cadastrados abaixo
    b"\x01\x00"  # Security Mode: Signing Enabled
    b"\x00\x00"  # Reserved
    b"\x7f\x00\x00\x00"  # Capabilities (Suporte a criptografia básica)
    # Client GUID simulado
    b"\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"  # Contexto / Start Time
    # Lista de Dialetos aceitos (O Windows precisa ver estes códigos)
    b"\x02\x02"  # SMB 2.002
    b"\x10\x02"  # SMB 2.1
    b"\x00\x03"  # SMB 3.0
    b"\x02\x03"  # SMB 3.02
    b"\x11\x03"  # SMB 3.1.1
)

# Adiciona o cabeçalho NetBIOS Framing (obrigatório antes do pacote SMB em TCP bruto)
packet_len = len(smb3_negotiate_payload)
netbios_header = struct.pack(">I", packet_len)
full_packet = netbios_header + smb3_negotiate_payload

print(
    f"[*] Enviando handshake SMBv2/v3 legítimo para {target}:{port}..."
)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    s.connect((target, port))

    s.send(full_packet)
    response = s.recv(2048)
    s.close()

    if response and len(response) > 4:
        print("[+] Conexão aceita pelo Windows alvo!")
        print("-" * 60)

        # Filtra os dados binários para extrair strings legíveis em formato Unicode/ASCII
        strings_encontradas = []
        temp_str = ""

        for b in response:
            if 32 <= b <= 126:  # Caracteres ASCII válidos
                temp_str += chr(b)
            else:
                if len(temp_str) > 2:
                    # Ignora assinaturas estruturais do próprio protocolo
                    if not any(
                        x in temp_str for x in ["SMB", "FE", "MSExchange"]
                    ):
                        strings_encontradas.append(temp_str.strip())
                temp_str = ""

        # Remove duplicatas mantendo a ordem
        resultados_unicos = list(dict.fromkeys(strings_encontradas))

        print(f"Resultados obtidos de {target}:")
        if resultados_unicos:
            for item in resultados_unicos:
                if len(item) > 1:
                    print(f"  |-> Identificador do Host: {item}")
        else:
            print("  |-> Conexão efetuada com sucesso.")
            print(
                "  |-> O host respondeu de forma estrita (sem vazar strings brutas no handshake)."
            )

        if b"\xfeSMB" in response:
            print("  |-> Protocolo Confirmado: Windows SMBv2/v3 Ativo")
        print("-" * 60)

except Exception as e:
    print(f"[-] Erro ao interagir com a porta 445: {e}")

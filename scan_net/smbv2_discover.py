import socket
import struct

target = "192.168.4.19"
port = 445

# Cabeçalho NetBIOS (4 bytes) + Cabeçalho SMBv2 (64 bytes) + Negotiate Request
# Este pacote avisa o Windows que queremos conversar usando SMBv2/SMBv3
smb2_negotiate = (
    b"\x00\x00\x00\x44"  # NetBIOS Session Message (Tamanho do payload)
    # --- PROTOCOLO SMB2 CABEÇALHO ---
    b"\xfe\x53\x4d\x42"  # Protocolo: \xfeSMB
    b"\x40\x00"  # Tamanho do cabeçalho (64 bytes)
    b"\x00\x00"  # Credit Charge
    b"\x00\x00\x00\x00"  # Status
    b"\x00\x00"  # Comando: Negotiate (0x0000)
    b"\x00\x00"  # Credits Requested
    b"\x00\x00\x00\x00"  # Flags
    b"\x00\x00\x00\x00"  # Next Command
    b"\x00\x00\x00\x00\x00\x00\x00\x00"  # Message ID
    b"\x00\x00\x00\x00"  # Process ID
    b"\x00\x00\x00\x00"  # Tree ID
    b"\x00\x00\x00\x00\x00\x00\x00\x00"  # Session ID
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # Signature
    # --- REQUISIÇÃO DE NEGOCIAÇÃO ---
    b"\x24\x00"  # Structure Size (36)
    b"\x02\x00"  # Dialect Count (2 dialetos: SMB 2.002 e SMB 2.1)
    b"\x01\x00"  # Security Mode (Signing enabled)
    b"\x00\x00"  # Reserved
    b"\x00\x00\x00\x00"  # Capabilities
    # Client GUID (Aleatório)
    b"\x11\x22\x33\x44\x55\x66\x77\x88\x99\xaa\xbb\xcc\xdd\xee\xff\x00"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"  # Client Start Time
    b"\x02\x02"  # Dialeto 1: SMB 2.002
    b"\x10\x02"  # Dialeto 2: SMB 2.1
)

print(f"[*] Conectando a {target}:{port} via SMBv2 (Moderno)...")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    s.connect((target, port))

    # Envia a estrutura SMBv2
    s.send(smb2_negotiate)
    response = s.recv(2048)
    s.close()

    if response and len(response) > 4:
        print("[+] Resposta SMBv2 recebida com sucesso!")
        print("-" * 60)

        # O Windows costuma devolver o GUID do sistema e dados do domínio no pacote de resposta
        # Vamos extrair texto legível (ASCII e Unicode) do payload recebido
        strings_encontradas = []
        temp_str = ""

        for b in response:
            if 32 <= b <= 126:  # Caracteres válidos
                temp_str += chr(b)
            else:
                if len(temp_str) > 3:
                    # Filtra ruídos normais do protocolo
                    if not any(
                        x in temp_str for x in ["SMB", "FE", "MSExchange"]
                    ):
                        strings_encontradas.append(temp_str)
                temp_str = ""

        print(f"Metadados extraídos de {target}:")
        visto = set()
        for item in strings_encontradas:
            item_clean = item.strip()
            if len(item_clean) > 2 and item_clean not in visto:
                visto.add(item_clean)
                print(f"  |-> String encontrada no Host: {item_clean}")

        # Se o pacote contiver estruturas específicas do Windows, ele valida que está ativo
        if b"\xfeSMB" in response:
            print("  |-> Protocolo Confirmado: Windows SMBv2/SMBv3 Ativo")

        print("-" * 60)
    else:
        print("[-] O host respondeu com um pacote vazio.")

except socket.timeout:
    print(
        "[-] Erro: Timeout. O host rejeitou a conexão ou o firewall barrou o pacote."
    )
except Exception as e:
    print(f"[-] Erro na comunicação: {e}")

import socket
import struct

target = "192.168.4.19"
port = 135

# 1. Pacote RPC BIND para a interface do Endpoint Mapper (UUID: e1af8308-5d1f-11c9-91a4-08002b14a0fa)
rpc_bind_epm = (
    b"\x05\x00"  # Versão RPC (5.0)
    b"\x0b"  # Tipo: Bind
    b"\x03"  # Flags
    b"\x10\x00\x00\x00"  # Data Representation
    b"\x48\x00"  # Auth Length
    b"\x00\x00\x00\x00"  # Call ID
    b"\xb8\x0f"  # Max Transmit Frag
    b"\xb8\x0f"  # Max Receive Frag
    b"\x00\x00\x00\x00"  # Assoc Group
    b"\x01\x00\x00\x00"  # Num Ctx Items
    b"\x00\x00"  # Context ID
    b"\x01\x00"  # Num Transfer Syntaxes
    # UUID da Interface Endpoint Mapper
    b"\x08\x83\xaf\xe1\x1f\x5d\xc9\x11\x91\xa4\x08\x00\x2b\x14\xa0\xfa"
    b"\x03\x00\x00\x00"  # Interface Ver Major/Minor (3.0)
    # UUID do Transfer Syntax (NDR)
    b"\x04\x5d\x88\x8a\xeb\x1c\xc9\x11\x9f\xe8\x08\x00\x2b\x10\x48\x60"
    b"\x02\x00\x00\x00"  # Transfer Syntax Ver
)

# 2. Pacote RPC REQUEST para executar a função Lookup (Coletar informações do host)
rpc_lookup_request = (
    b"\x05\x00"  # Versão RPC (5.0)
    b"\x00"  # Tipo: Request
    b"\x03"  # Flags (Last Fragm / First Fragm)
    b"\x10\x00\x00\x00"  # Data Representation
    b"\x00\x00"  # Auth Length
    b"\x01\x00\x00\x00"  # Call ID
    b"\x2c\x00\x00\x00"  # Alloc Hint
    b"\x00\x00"  # Context ID
    b"\x02\x00"  # Opnum (2 = Lookup)
    # --- Parâmetros da Função Lookup ---
    b"\x00\x00\x00\x00"  # Inquire Type
    b"\x00\x00\x00\x00"  # Object (Null Pointer)
    b"\x00\x00\x00\x00"  # If id (Null Pointer)
    b"\x00\x00\x00\x00"  # Versão major/minor
    b"\x00\x00\x00\x00"  # Entry Handle (Null / Início da busca)
    b"\x01\x00\x00\x00"  # Max Entries requested
)

print(
    f"[*] Conectando ao RPC Endpoint Mapper em {target}:{port} para extrair metadados..."
)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    s.connect((target, port))

    # Etapa 1: Envia o Bind para registrar a comunicação
    s.send(rpc_bind_epm)
    bind_response = s.recv(1024)

    if bind_response and bind_response[2] == 0x0C:  # 0x0C = Bind_Ack
        print("[+] Conexão RPC aceita e associada!")

        # Etapa 2: Envia a requisição de consulta de metadados
        s.send(rpc_lookup_request)
        lookup_response = s.recv(4096)
        s.close()

        print("[+] Dados retornados pelo serviço RPC.")
        print("-" * 60)

        # Varre o pacote binário buscando por nomes de hosts, domínios ou padrões de rede
        strings_encontradas = []
        temp_str = ""

        for b in lookup_response:
            # Filtra caracteres alfanuméricos e caracteres comuns de rede (.-_)
            if 32 <= b <= 126:
                temp_str += chr(b)
            else:
                if len(temp_str) > 3:
                    # Remove ruídos estruturais do protocolo RPC
                    if not any(
                        x in temp_str
                        for x in ["Ndr", "Bind", "Rpc", "epm", "\\pipe"]
                    ):
                        strings_encontradas.append(temp_str.strip())
                temp_str = ""

        # Remove duplicatas
        resultados = list(dict.fromkeys(strings_encontradas))

        print(f"Metadados extraídos via RPC:")
        for item in resultados:
            # Filtra nomes de rede prováveis (geralmente em maiúsculo ou com padrões de domínio)
            if len(item) > 2:
                print(f"  |-> Identificador / Hostname encontrado: {item}")

        print("-" * 60)
    else:
        print("[-] O host recusou a associação RPC Bind.")
        s.close()

except Exception as e:
    print(f"[-] Erro ao interagir com a porta 135: {e}")

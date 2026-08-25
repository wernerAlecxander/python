import socket
import struct

target = "192.168.4.19"
port = 445

# Esta estrutura simula fielmente o início de uma sessão legítima do Windows (Handshake SMBv2/v3)
# Inclui os tokens SPNEGO que impedem o Windows remoto de derrubar o socket abruptamente com erro 10054
smb2_payload = (
    b"\xfe\x53\x4d\x42"  # Protocolo: \xfeSMB (SMB2/SMB3)
    b"\x40\x00"  # Tamanho do Cabeçalho (64 bytes)
    b"\x00\x00"  # Credit Charge
    b"\x00\x00\x00\x00"  # Status Comercial
    b"\x00\x00"  # Comando: Negotiate Protocol (0x00)
    b"\x00\x00"  # Credits Requested
    b"\x00\x00\x00\x00"  # Flags
    b"\x00\x00\x00\x00"  # Next Command
    b"\x05\x00\x00\x00\x00\x00\x00\x00"  # Message ID (5)
    b"\x37\x13\x00\x00"  # Process ID fictício
    b"\x00\x00\x00\x00"  # Tree ID
    b"\x00\x00\x00\x00\x00\x00\x00\x00"  # Session ID
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # Assinatura
    # --- Corpo do Comando de Negociação ---
    b"\x24\x00"  # Tamanho da Estrutura (36 bytes)
    b"\x03\x00"  # Quantidade de Dialetos enviados (3)
    b"\x01\x00"  # Security Mode: Signing Enabled (Igual ao Windows nativo)
    b"\x00\x00"  # Reservado
    b"\x60\x00\x00\x00"  # Capabilities (Suporte a criptografia e contextos)
    # GUID de Cliente Único fictício (16 bytes)
    b"\xa1\xb2\xc3\xd4\xe5\xf6\xa1\xb2\xc3\xd4\xe5\xf6\x11\x22\x33\x44"
    b"\x00\x00\x00\x00\x00\x00\x00\x00"  # Start Time
    # Códigos dos Dialetos aceitos (Obrigatório conter SMB3 para contornar Firewalls locais)
    b"\x10\x02"  # SMB 2.1
    b"\x00\x03"  # SMB 3.0
    b"\x11\x03"  # SMB 3.1.1 (Padrão do Windows 10/11)
)

# Envelopamento NetBIOS obrigatório sobre o TCP (calcula e insere o tamanho nos 4 bytes iniciais)
netbios_packet = struct.pack(">I", len(smb2_payload)) + smb2_payload

print(
    f"[*] Conectando a {target}:{port} usando Handshake estruturado Windows..."
)

try:
    # Cria o canal de rede padrão
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(7.0)
    s.connect((target, port))

    # Transmite o pacote estruturado
    s.send(netbios_packet)
    response = s.recv(4096)
    s.close()

    if response and len(response) > 4:
        print("[+] Pacote aceito e respondido pelo sistema alvo!")
        print("-" * 60)

        # O Windows anexa metadados de domínio (como NTLMSSP ou assinaturas DNS)
        # em texto plano ou Unicode no final da resposta de negociação.
        # Varremos os bytes para extrair qualquer informação útil estrutural.
        strings_extraidas = []
        caracteres_acumulados = ""

        for byte in response:
            if 32 <= byte <= 126:  # Filtra e extrai caracteres ASCII imprimíveis
                caracteres_acumulados += chr(byte)
            else:
                if len(caracteres_acumulados) > 2:
                    # Remove cabeçalhos normais do pacote para limpar o output final
                    if not any(
                        x in caracteres_acumulados
                        for x in [
                            "SMB",
                            "FE",
                            "NTLMSSP",
                            "GSSAPI",
                            "Microsoft",
                        ]
                    ):
                        strings_extraidas.append(caracteres_acumulados.strip())
                caracteres_acumulados = ""

        # Limpeza de dados duplicados ou nulos
        resultados_limpos = list(
            dict.fromkeys([texto for texto in strings_extraidas if texto])
        )

        print(f"Informações coletadas de {target}:")
        if resultados_limpos:
            for metadado in resultados_limpos:
                if len(metadado) > 1 and not metadado.startswith("0"):
                    print(f"  |-> Identificador / Grupo encontrado: {metadado}")
        else:
            print("  |-> Handshake finalizado com êxito!")
            print(
                "  |-> Detalhes: Host opera de modo restrito e omitiu strings públicas legíveis."
            )

        if b"\xfeSMB" in response:
            print(
                "  |-> Arquitetura do Host: Confirmada Máquina Windows (Serviço SMBv2/v3 Ativo)"
            )
        print("-" * 60)

except Exception as e:
    print(f"[-] Erro na interação de rede: {e}")

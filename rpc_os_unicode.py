import socket
import struct

target = "192.168.4.19"
port = 135

# Pacote RPC Bind para a interface de ativação remota (DCOM)
rpc_dcom_bind = (
    b"\x05\x00\x0b\x03\x10\x00\x00\x00\x48\x00\x00\x00\x00\x00\x00\x00"
    b"\xb8\x0f\xb8\x0f\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00"
    b"\xb8\x4a\x9f\x4d\x1c\x7d\xcf\x11\x86\x1e\x00\x20\xaf\x6e\x7c\x57"
    b"\x00\x00\x00\x00\x04\x5d\x88\x8a\xeb\x1c\xc9\x11\x9f\xe8\x08\x00"
    b"\x2b\x10\x48\x60\x02\x00\x00\x00"
)

print(f"[*] Extraindo metadados estruturados de {target}...")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    s.connect((target, port))
    s.send(rpc_dcom_bind)
    response = s.recv(4096)
    s.close()

    if response:
        print("[+] Resposta binária recebida. Decodificando metadados...")
        print("-" * 60)
        
        # 1. Tenta decodificar o pacote inteiro como UTF-16LE (Unicode padrão do Windows)
        # Substitui caracteres binários inválidos por espaços para não quebrar o script
        texto_unicode = response.decode("utf-16-le", errors="replace")
        
        # Filtra e limpa as palavras encontradas no dump Unicode
        strings_unicode = []
        palavra_atual = ""
        
        for char in texto_unicode:
            # Mantém apenas caracteres alfanuméricos normais, hifens e pontos
            if char.isalnum() or char in "-.":
                palavra_atual += char
            else:
                if len(palavra_atual) > 3:
                    # Filtra falsos positivos comuns do protocolo RPC
                    if not any(x in palavra_atual.lower() for x in ["ndr", "bind", "rpc", "ntlm", "ms"]):
                        strings_unicode.append(palavra_atual.strip())
                palavra_atual = ""

        # 2. Tenta extrair a versão exata do sistema operacional através do bloco NTLM (se presente)
        if b"NTLMSSP" in response:
            print("  |-> Arquitetura Confirmada: Sistema Baseado em Windows OS")
            idx = response.find(b"NTLMSSP")
            # No protocolo NTLM, a versão do Kernel do Windows fica localizada 48 bytes após a assinatura
            if len(response) > idx + 56:
                version_bytes = response[idx+48 : idx+56]
                major, minor, build = struct.unpack("<BBH", version_bytes[:4])
                # Mapeamento básico de versões de Kernel do Windows
                if major == 10 and minor == 0:
                    print(f"  |-> Versão do S.O. Estimada: Windows 10 / Windows 11 / Server (Build {build})")
                elif major == 6 and minor == 3:
                    print(f"  |-> Versão do S.O. Estimada: Windows 8.1 / Server 2012 R2")
                elif major == 6 and minor == 1:
                    print(f"  |-> Versão do S.O. Estimada: Windows 7 / Server 2008 R2")

        # Exibe os Hostnames/Nomes de rede que foram limpos do decodificador Unicode
        resultados_unicos = list(dict.fromkeys(strings_unicode))
        
        print("\nIdentificadores de Rede Encontrados (Unicode):")
        if resultados_unicos:
            for item in resultados_unicos:
                # Evita imprimir strings que sejam apenas números isolados
                if not item.isdigit():
                    print(f"  |-> Hostname / Nome detectado: {item}")
        else:
            print("  |-> O host não enviou strings de texto legíveis no handshake inicial.")
            print("  |-> Dica: O Windows remoto está aplicando políticas rígidas de isolamento de tráfego.")
        print("-" * 60)
        
    else:
        print("[-] O servidor fechou a conexão sem enviar dados.")

except Exception as e:
    print(f"[-] Erro na coleta de metadados: {e}")

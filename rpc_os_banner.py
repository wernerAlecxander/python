import socket
import struct

target = "192.168.4.19"
port = 135

# Pacote RPC Bind que solicita a interface de ativação remota (DCOM)
# Essa requisição força o Windows a responder com um token NTLMSSP legítimo
rpc_dcom_bind = (
    b"\x05\x00\x0b\x03\x10\x00\x00\x00\x48\x00\x00\x00\x00\x00\x00\x00"
    b"\xb8\x0f\xb8\x0f\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00"
    # UUID da Interface IRemoteActivation (4d9f4ab8-7d1c-11cf-861e-0020af6e7c57)
    b"\xb8\x4a\x9f\x4d\x1c\x7d\xcf\x11\x86\x1e\x00\x20\xaf\x6e\x7c\x57"
    b"\x00\x00\x00\x00\x04\x5d\x88\x8a\xeb\x1c\xc9\x11\x9f\xe8\x08\x00"
    b"\x2b\x10\x48\x60\x02\x00\x00\x00"
)

print(f"[*] Extraindo metadados de S.O. via DCOM RPC em {target}...")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    s.connect((target, port))
    
    s.send(rpc_dcom_bind)
    response = s.recv(4096)
    s.close()

    if response:
        print("[+] Resposta de metadados recebida!")
        print("-" * 60)
        
        # Procura pela assinatura NTLMSSP na memória do pacote
        if b"NTLMSSP" in response:
            idx = response.find(b"NTLMSSP")
            # O Windows anexa a versão do Kernel nos bytes logo após a assinatura
            # ex: Major version, Minor version, Build number
            print("[+] Assinatura de Segurança Encontrada: Windows OS")
        
        # Filtra strings legíveis em formato ASCII/Unicode enviadas pelo Host
        strings_limpas = []
        acumulador = ""
        
        for b in response:
            if 32 <= b <= 126:
                acumulador += chr(b)
            else:
                if len(acumulador) > 3:
                    if not any(x in acumulador for x in ["Ndr", "Bind", "Rpc", "NTLMSSP"]):
                        strings_limpas.append(acumulador.strip())
                acumulador = ""
                
        resultados = list(dict.fromkeys([s for s in strings_limpas if s]))
        
        print("Informações de Identidade coletadas:")
        for item in resultados:
            if len(item) > 2 and not item.startswith("0") and item != target:
                print(f"  |-> Nome de Rede / Host detectado: {item}")
        
        print("-" * 60)
    else:
        print("[-] Nenhuma resposta de metadados do serviço.")

except Exception as e:
    print(f"[-] Falha na comunicação RPC: {e}")

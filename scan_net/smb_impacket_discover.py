import sys
from impacket.smbconnection import SMBConnection

target = "192.168.4.19"

print(f"[*] Conectando a {target} via Impacket (Simulando SMB-OS-Discover)...")
print("-" * 60)

try:
    # Cria a conexão SMB legítima na porta 445 (Gerencia SMBv2 e SMBv3 de forma transparente)
    # Tenta estabelecer uma sessão de convidado/nula para extração de metadados nativos
    smb = SMBConnection(
        remoteName=target, remoteHost=target, sess_port=445, timeout=7
    )
    smb.login(user="", password="", domain="")

    print("[+] Conexão SMB estabelecida com sucesso!")
    print("-" * 60)

    # Coleta as propriedades estruturais da máquina retornadas no aperto de mão
    os_version = smb.getServerOS()
    domain_name = smb.getServerDomain()
    dns_name = smb.getServerDNSDomainName()

    print(f"Resultados obtidos do Alvo ({target}):")
    print(f"  |-> Versão do Sistema Operacional (S.O.): {os_version}")
    print(f"  |-> Grupo de Trabalho / Domínio detectado: {domain_name}")
    print(f"  |-> Nome de Domínio DNS completo: {dns_name}")

    # Tenta capturar o nome de rede NetBIOS do computador
    try:
        server_name = smb.getServerName()
        print(f"  |-> Nome NetBIOS do Host: {server_name}")
    except:
        pass

    smb.logoff()
    print("-" * 60)

except Exception as e:
    error_msg = str(e)
    # Se o Windows aceitar a conexão mas rejeitar o login anônimo, ele costuma
    # vazar os dados do sistema operacional no cabeçalho do erro. Verificamos isso aqui:
    if "STATUS_ACCESS_DENIED" in error_msg or "Guest" in error_msg:
        print(
            "[!] O host remoto rejeitou o acesso anônimo (Null Session) aos arquivos,"
        )
        print(
            "    mas a conexão inicial foi efetuada e validou o protocolo."
        )
    else:
        print(f"[-] Erro na negociação do protocolo SMB: {e}")

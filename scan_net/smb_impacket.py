import sys
from impacket.smbconnection import SMBConnection

target = "192.168.4.19"

print(f"[*] Conectando a {target} via Impacket (Simulando SMB-OS-Discover)...")
print("-" * 60)

try:
    # Cria uma conexão SMB na porta 445 (Tenta SMBv2 e SMBv3 automaticamente)
    # Usamos usuário e senha vazios (Null Session) para colher metadados públicos
    smb = SMBConnection(
        remoteName=target, remoteHost=target, sess_port=445, timeout=5
    )
    smb.login(user="", password="", domain="")

    print("[+] Conexão SMB Estabelecida com sucesso!")

    # Extrai os dados do sistema operacional armazenados na sessão
    os_version = smb.getServerOS()
    domain_name = smb.getServerDomain()
    dns_name = smb.getServerDNSDomainName()

    print(f"\nResultados para {target}:")
    print(f"  |-> Sistema Operacional (S.O.): {os_version}")
    print(f"  |-> Domínio / Workgroup: {domain_name}")
    print(f"  |-> Nome de Domínio DNS: {dns_name}")

    # Tenta descobrir o nome NetBIOS da máquina pelas propriedades internas
    try:
        server_name = smb.getServerName()
        print(f"  |-> Nome NetBIOS da Máquina: {server_name}")
    except:
        pass

    smb.logoff()
    print("-" * 60)

except Exception as e:
    # Se der erro de Access Denied, o Windows exige autenticação, mas as propriedades básicas podem ter sido capturadas antes
    error_msg = str(e)
    if "STATUS_ACCESS_DENIED" in error_msg or "Guest" in error_msg:
        print("[!] O Host exige credenciais válidas para listar compartilhamentos,")
        print("    mas conseguimos forçar o aperto de mão do protocolo.")
    else:
        print(f"[-] Erro ao negociar SMB: {e}")

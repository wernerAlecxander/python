import os
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor
from mac_vendor_lookup import MacLookup, InvalidMacError

# Inicializa o resolvedor de fabricantes de MAC
try:
    mac_lookup = MacLookup()
    # Caso seja a primeira vez rodando, ele baixa a base mais atualizada da IEEE automaticamente se tiver internet.
    mac_lookup.load_vendors()
except Exception:
    mac_lookup = None

def ping_ip(ip):
    """Envia um único ping rápido para o IP para forçá-lo a aparecer no ARP."""
    # -n 1 (1 pacote), -w 150 (timeout de 150ms para ser rápido)
    comando = f"ping -n 1 -w 150 {ip}"
    subprocess.run(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def varrer_rede_com_pings(subrede):
    """Dispara pings em paralelo para todos os 254 IPs possíveis da subrede."""
    print(f"Enviando pings automáticos para a faixa {subrede}.1 até {subrede}.254...")
    ips = [f"{subrede}.{i}" for i in range(1, 255)]
    
    # Usa 50 threads em paralelo para varrer a rede inteira em poucos segundos
    with ThreadPoolExecutor(max_workers=50) as executor:
        executor.map(ping_ip, ips)
    print("Pings concluídos! Coletando dados da tabela ARP do Windows...\n")

def obter_dados_arp(subrede):
    """Lê a tabela ARP do Windows e extrai IP, MAC e Fabricante."""
    try:
        output = subprocess.check_output("arp -a", shell=True).decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Erro ao ler tabela ARP: {e}")
        return []

    # Captura apenas os IPs que pertencem à subrede desejada
    padrao_regex = fr"({re.escape(subrede)}\.\d+)\s+([0-9a-fA-F-]+)\s+(din|est)"
    matches = re.findall(padrao_regex, output, re.IGNORECASE)
    
    dispositivos = []
    mac_vistos = set()

    for ip, mac, _ in matches:
        mac_formatado = mac.replace('-', ':').lower()
        
        # Evita duplicatas de MAC no relatório
        if mac_formatado in mac_vistos:
            continue
        mac_vistos.add(mac_formatado)
        
        # Descobre o fabricante usando a biblioteca local
        fabricante = "Desconhecido"
        if mac_lookup:
            try:
                fabricante = mac_lookup.lookup(mac_formatado)
            except InvalidMacError:
                fabricante = "Formato de MAC Inválido"
            except Exception:
                fabricante = "Não Encontrado na Base"

        dispositivos.append({
            'ip': ip,
            'mac': mac_formatado.upper(),
            'fabricante': fabricante
        })
        
    # Ordena a lista pelo último octeto do IP
    dispositivos.sort(key=lambda x: int(x['ip'].split('.')[-1]))
    return dispositivos

def salvar_e_exibir_resultados(dispositivos, nome_arquivo="relatorio_rede.txt"):
    linhas_relatorio = []
    linhas_relatorio.append("=" * 75)
    linhas_relatorio.append(f"{'Endereço IP':<18}{'Endereço MAC':<22}{'Fabricante/Nome do Dispositivo'}")
    linhas_relatorio.append("=" * 75)
    
    for dev in dispositivos:
        linhas_relatorio.append(f"{dev['ip']:<18}{dev['mac']:<22}{dev['fabricante']}")
        
    linhas_relatorio.append("=" * 75)
    linhas_relatorio.append(f"Total de dispositivos mapeados ativos: {len(dispositivos)}")
    
    # Exibe na tela do terminal
    conteudo_final = "\n".join(linhas_relatorio)
    print(conteudo_final)
    
    # Salva no arquivo de texto TXT
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo_final)
    print(f"\n[SUCESSO] Relatório salvo com sucesso em: {os.path.abspath(nome_arquivo)}")

if __name__ == "__main__":
    # DIGITE AQUI OS 3 PRIMEIROS JOGOS DE NÚMEROS DA SUA REDE (sem o último ponto)
    # Exemplos comuns: "192.168.1" ou "192.168.0" ou "10.0.0"
    SUBREDE_ALVO = "192.168.1.1" 
    
    # Execução das etapas
    varrer_rede_com_pings(SUBREDE_ALVO)
    dispositivos_encontrados = obter_dados_arp(SUBREDE_ALVO)
    salvar_e_exibir_resultados(dispositivos_encontrados)

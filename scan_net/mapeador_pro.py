import os
import re
import socket
import subprocess
from concurrent.futures import ThreadPoolExecutor
from mac_vendor_lookup import MacLookup, InvalidMacError

# Configura um timeout global rápido para requisições de rede do Python
socket.setdefaulttimeout(0.5)

# Inicializa o resolvedor de fabricantes de MAC
try:
    mac_lookup = MacLookup()
    mac_lookup.load_vendors()
except Exception:
    mac_lookup = None

def ping_ip(ip):
    """Envia um único ping ultra-rápido para o IP para atualizar a tabela ARP."""
    comando = f"ping -n 1 -w 100 {ip}"
    subprocess.run(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def obter_hostname(ip):
    """Tenta descobrir o hostname usando DNS local e comando nbtstat do Windows."""
    # Estratégia 1: Resolução padrão de Socket do Python
    try:
        nome, _, _ = socket.gethostbyaddr(ip)
        return nome
    except Exception:
        pass

    # Estratégia 2: Comando nbtstat do Windows (específico para nomes NetBIOS/Windows na rede local)
    try:
        resultado = subprocess.check_output(f"nbtstat -A {ip}", shell=True, timeout=0.5).decode('utf-8', errors='ignore')
        # Procura por linhas que tenham o padrão de nome de máquina NetBIOS (tipo <00> UNIQUE)
        linhas = resultado.split("\n")
        for linha in linhas:
            match = re.search(r"\s+([A-Za-z0-9_-]+)\s+<00>\s+ÚNICO", linha, re.IGNORECASE) or \
                    re.search(r"\s+([A-Za-z0-9_-]+)\s+<00>\s+UNIQUE", linha, re.IGNORECASE)
            if match:
                return match.group(1).strip()
    except Exception:
        pass

    return "Desconhecido"

def varrer_rede(subrede):
    """Dispara pings em paralelo e processa os resultados."""
    print(f"1. Enviando pings automáticos para a faixa {subrede}.1 até {subrede}.254...")
    ips = [f"{subrede}.{i}" for i in range(1, 255)]
    
    # 60 trabalhadores em paralelo para varrer a rede inteira em segundos
    with ThreadPoolExecutor(max_workers=60) as executor:
        executor.map(ping_ip, ips)
    
    print("2. Coletando dados da tabela ARP do Windows...")
    try:
        output = subprocess.check_output("arp -a", shell=True).decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Erro ao ler tabela ARP: {e}")
        return []

    padrao_regex = fr"({re.escape(subrede)}\.\d+)\s+([0-9a-fA-F-]+)\s+(din|est)"
    matches = re.findall(padrao_regex, output, re.IGNORECASE)
    
    dispositivos = []
    mac_vistos = set()

    # Processa os hostnames em paralelo para não travar o script
    print("3. Resolvendo Hostnames e Fabricantes dos dispositivos encontrados...")
    
    def processar_dispositivo(item):
        ip, mac = item
        mac_formatado = mac.replace('-', ':').lower()
        if mac_formatado in mac_vistos:
            return None
        mac_vistos.add(mac_formatado)

        # Descobre o fabricante
        fabricante = "Desconhecido"
        if mac_lookup:
            try:
                fabricante = mac_lookup.lookup(mac_formatado)
            except InvalidMacError:
                fabricante = "MAC Inválido"
            except Exception:
                fabricante = "Não Encontrado"

        # Descobre o hostname
        hostname = obter_hostname(ip)

        return {
            'ip': ip,
            'mac': mac_formatado.upper(),
            'hostname': hostname,
            'fabricante': fabricante
        }

    # Executa a descoberta de detalhes em paralelo
    dados_brutos = [(ip, mac) for ip, mac, _ in matches]
    with ThreadPoolExecutor(max_workers=30) as executor:
        resultados = executor.map(processar_dispositivo, dados_brutos)
        
    for r in resultados:
        if r:
            dispositivos.append(r)
        
    # Ordena pelo IP final
    dispositivos.sort(key=lambda x: int(x['ip'].split('.')[-1]))
    return dispositivos

def salvar_relatorio(dispositivos, nome_arquivo="relatorio_rede_completo.txt"):
    linhas = []
    linhas.append("=" * 105)
    linhas.append(f"{'Endereço IP':<18}{'Endereço MAC':<20}{'Nome de Rede (Hostname)':<27}{'Fabricante Hardware'}")
    linhas.append("=" * 105)
    
    for dev in dispositivos:
        linhas.append(f"{dev['ip']:<18}{dev['mac']:<20}{dev['hostname']:<27}{dev['fabricante']}")
        
    linhas.append("=" * 105)
    linhas.append(f"Total de dispositivos mapeados ativos: {len(dispositivos)}")
    
    conteudo_final = "\n".join(linhas)
    print("\n" + conteudo_final)
    
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo_final)
    print(f"\n[SUCESSO] Relatório salvo com sucesso em: {os.path.abspath(nome_arquivo)}")

if __name__ == "__main__":
    # Ajuste para os 3 primeiros blocos do seu IP local
    SUBREDE_ALVO = "192.168.1" 
    
    dispositivos_encontrados = varrer_rede(SUBREDE_ALVO)
    salvar_relatorio(dispositivos_encontrados)

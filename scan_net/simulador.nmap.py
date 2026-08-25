import sys
from scapy.all import IP, TCP, UDP, ICMP, sr1, traceroute

# Configurações equivalentes aos parâmetros do seu comando Nmap
target = "192.168.4.19"
source_port = 53  # Equivalente ao '-g 53'
ports_to_scan = [21, 22, 23, 25, 53, 80, 139, 443, 445, 3389]  # Portas comuns para teste


def syn_scan_and_version(target_ip, port):
    """Simula o '-sS -sV --reason' (SYN Scan, Versão e Motivo)"""
    # Cria o pacote TCP SYN com a porta de origem customizada (-g 53)
    ip_packet = IP(dst=target_ip)
    tcp_packet = TCP(sport=source_port, dport=port, flags="S")

    # Envia o pacote e aguarda a resposta (-Pn assume que o host está vivo)
    response = sr1(ip_packet / tcp_packet, timeout=1, verbose=0)

    if response is None:
        print(f"Porta {port}/tcp: Filtrada (Sem resposta)")
    elif response.haslayer(TCP):
        flags = response.getlayer(TCP).flags

        # Se responder com SYN-ACK (0x12), a porta está aberta
        if flags == 0x12:
            reason = "received syn-ack"
            banner = "Desconhecido"

            # Simulação básica de -sV (Tenta ler o Banner da porta se estiver aberta)
            try:
                # Envia um pacote complementar para puxar dados básicos (ex: HTTP ou SSH)
                tcp_data = TCP(sport=source_port, dport=port, flags="A")
                banner_res = sr1(
                    IP(dst=target_ip) / tcp_data, timeout=1, verbose=0
                )
                if banner_res and banner_res.haslayer(TCP) and banner_res.load:
                    banner = banner_res.load.decode(
                        "utf-8", errors="ignore"
                    ).strip()
            except:
                pass

            print(
                f"Porta {port}/tcp: ABERTA | Razão: {reason} | Serviço/Banner: {banner}"
            )

            # Destrói a conexão de forma limpa (Envia RST) para não deixar a porta aberta
            sr1(
                IP(dst=target_ip) / TCP(sport=source_port, dport=port, flags="R"),
                timeout=1,
                verbose=0,
            )

        # Se responder com RST (0x14), a porta está fechada
        elif flags == 0x14:
            print(f"Porta {port}/tcp: FECHADA | Razão: received rst")


def run_traceroute(target_ip):
    """Simula o '--traceroute -n'"""
    print("\n--- ROTEAMENTO (--traceroute) ---")
    # Executa o traceroute nativo do Scapy sem resolver nomes (-n)
    traceroute(target_ip, maxttl=20, verbose=0)


# --- Execução do Script ---
print(f"Iniciando escaneamento simulado para {target} (Porta Origem: {source_port})")
print("-" * 60)

# 1. Executa o Scan de Portas (Simulando -sS, -g 53, -Pn, --reason)
for p in ports_to_scan:
    syn_scan_and_version(target, p)

# 2. Executa o Traceroute (Simulando --traceroute)
run_traceroute(target)

print("\nNota: Identificação de S.O. (-O) e scripts SMB requerem privilégios")
print("de baixo nível e bases de dados do Nmap que não estão disponíveis no Python puro.")

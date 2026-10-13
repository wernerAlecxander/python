from scapy.all import IP, TCP, sr1

def tcp_syn_scan(target_ip, port):
    # Constrói o pacote de rede manualmente (Camada IP + Camada TCP com flag SYN)
    ip_packet = IP(dst=target_ip)
    tcp_packet = TCP(dport=port, flags="S") # "S" representa a flag SYN
    packet = ip_packet / tcp_packet
    
    # Envia o pacote bruto e espera por exatamente 1 resposta (sr1)
    response = sr1(packet, timeout=1, verbose=0)
    
    if response is not None:
        # Analisa as flags da resposta do alvo
        if response.haslayer(TCP):
            if response.getlayer(TCP).flags == 0x12: # 0x12 é SYN-ACK em hexadecimal
                print(f"Porta {port}: ABERTA (SYN-ACK recebido)")
                
                # Envia um RST imediatamente para fechar a conexão pendente
                rst_packet = IP(dst=target_ip) / TCP(dport=port, flags="R")
                send(rst_packet, verbose=0)
            elif response.getlayer(TCP).flags == 0x14: # 0x14 é RST-ACK
                print(f"Porta {port}: FECHADA")
    else:
        print(f"Porta {port}: FILTRADA (Nenhuma resposta / Firewall dropou)")

# Exemplo de uso:
tcp_syn_scan("172.19.128.1", 445)
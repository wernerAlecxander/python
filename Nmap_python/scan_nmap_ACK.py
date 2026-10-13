from scapy.all import IP, TCP, sr1

def tcp_ack_scan(target_ip, port):
    # Monta a camada IP e a camada TCP com a flag "A" (ACK)
    packet = IP(dst=target_ip) / TCP(dport=port, flags="A")
    
    print(f"[+] Enviando pacote ACK surpresa para a porta {port}...")
    
    # Envia e aguarda resposta por até 2 segundos
    response = sr1(packet, timeout=2, verbose=0)
    
    if response is None:
        # O firewall inteligente barrou o pacote e não deixou o alvo responder
        print(f"Resultado: Porta {port} está FILTRADA (Firewall Stateful ativo)")
    else:
        if response.haslayer(TCP):
            if response.getlayer(TCP).flags & 0x04:  # 0x04 é a flag RST
                # O pacote passou pelo firewall e o sistema operacional respondeu
                print(f"Resultado: Porta {port} está NÃO FILTRADA (Passou pelo Firewall)")
            else:
                print(f"Resultado: Resposta inesperada com flags: {response.getlayer(TCP).flags}")

# Exemplo de teste contra um IP alvo
tcp_ack_scan("172.19.128.1", 80)
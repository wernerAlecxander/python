from scapy.all import IP, UDP, ICMP, sr1

def udp_port_scan(target_ip, port):
    # Constrói o pacote com a camada IP e a camada UDP apontando para a porta
    packet = IP(dst=target_ip) / UDP(dport=port)
    
    print(f"[+] Enviando pacote UDP bruto para a porta {port}...")
    
    # Envia o pacote e aguarda até 2 segundos por uma resposta
    response = sr1(packet, timeout=2, verbose=0)
    
    if response is None:
        # Silêncio total significa que a porta ignorou o pacote ou o firewall barrou
        print(f"Resultado: Porta {port} está ABERTA ou FILTRADA (Silêncio)")
    else:
        # Se recebemos uma resposta, checamos se é um erro ICMP
        if response.haslayer(ICMP):
            icmp_type = response.getlayer(ICMP).type
            icmp_code = response.getlayer(ICMP).code
            
            # Tipo 3, Código 3 = Port Unreachable (Norma RFC 792)
            if icmp_type == 3 and icmp_code == 3:
                print(f"Resultado: Porta {port} está FECHADA (ICMP Port Unreachable)")
            else:
                print(f"Resultado: Recebido outro erro ICMP (Tipo: {icmp_type}, Código: {icmp_code})")
        elif response.haslayer(UDP):
            # Caso raríssimo em scans vazios, mas se a aplicação responder em UDP, está aberta!
            print(f"Resultado: Porta {port} está ABERTA! (Resposta UDP recebida)")

# Exemplo de teste contra um serviço DNS comum (porta 53)
udp_port_scan("172.19.128.1", 53)
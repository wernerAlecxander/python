from scapy.all import IP, TCP, sr1

def tcp_xmas_scan(target_ip, port):
    # Constrói o cabeçalho IP com o destino
    ip_layer = IP(dst=target_ip)
    
    # Constrói o cabeçalho TCP ativando as flags F (FIN), P (PSH) e U (URG)
    # Visualmente na tabela de bits, essas flags ficam intercaladas: 00101001
    tcp_layer = TCP(dport=port, flags="FPU")
    
    # Junta as camadas para fundir o pacote
    packet = ip_layer / tcp_layer
    
    print(f"[+] Enviando pacote Xmas para a porta {port}...")
    
    # Envia e aguarda uma resposta por até 2 segundos
    response = sr1(packet, timeout=2, verbose=0)
    
    if response is None:
        # Se houve silêncio total, a porta obedeceu à RFC 793 para portas abertas
        print(f"Resultado: Porta {port} está ABERTA ou FILTRADA (Silêncio)")
    else:
        # Se o alvo respondeu, verificamos se ele mandou um pacote RST (Reset)
        if response.haslayer(TCP):
            if response.getlayer(TCP).flags & 0x04:  # 0x04 é a flag RST
                print(f"Resultado: Porta {port} está FECHADA (RST recebido)")
            else:
                print(f"Resultado: Resposta inesperada com flags: {response.getlayer(TCP).flags}")

# Exemplo de execução contra um servidor Linux
tcp_xmas_scan("172.19.128.5", 80)
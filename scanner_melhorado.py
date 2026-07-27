import socket
import sys
import time

# Configurações do seu comando original
target = "192.168.4.19"
source_port = 53  # Equivalente ao '-g 53'
ports_to_scan = [
    21,
    22,
    23,
    25,
    53,
    80,
    135,
    139,
    443,
    445,
    3389,
]  # Inclui portas SMB (139, 445)


def scapy_scan():
    """Tenta rodar o escaneamento avançado usando Scapy"""
    from scapy.all import IP, TCP, sr1

    print(
        f"[Scapy] Iniciando SYN Scan (-sS) com porta de origem {source_port}..."
    )

    for port in ports_to_scan:
        try:
            # Cria pacote idêntico ao comando: Origem=53, Destino=Porta, Flag=SYN
            packet = IP(dst=target) / TCP(sport=source_port, dport=port, flags="S")
            response = sr1(packet, timeout=1, verbose=0)

            if response is None:
                print(f"Porta {port}/tcp: FILTRADA | Razão: no-response")
            elif response.haslayer(TCP):
                flags = response.getlayer(TCP).flags
                if flags == 0x12:  # SYN-ACK
                    print(
                        f"Porta {port}/tcp: ABERTA | Razão: received syn-ack"
                    )
                    # Envia RST para fechar a conexão limpamente
                    sr1(
                        IP(dst=target)
                        / TCP(sport=source_port, dport=port, flags="R"),
                        timeout=1,
                        verbose=0,
                    )
                elif flags == 0x14:  # RST
                    print(f"Porta {port}/tcp: FECHADA | Razão: received rst")
        except Exception as e:
            # Se falhar por falta de permissão ou Npcap, força a mudança de modo
            print(f"\n[!] Scapy falhou (Falta de privilégios/Npcap): {e}")
            print("[+] Mudando automaticamente para o Modo Socket Padrão...\n")
            socket_scan()
            break


def socket_scan():
    """Modo de segurança: Funciona mesmo em usuários limitados no Windows"""
    print(
        f"[Socket] Iniciando Connect Scan (-sT) para {target} (Ignorando '-g 53')..."
    )

    for port in ports_to_scan:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.5)  # Timeout curto para simular rapidez do Nmap

        # Tenta conectar. connect_ex retorna 0 se der certo
        start_time = time.time()
        result = s.connect_ex((target, port))
        end_time = time.time()

        if result == 0:
            # Tenta puxar o Banner do serviço (Simulação básica do -sV)
            banner = "Desconhecido (Use credenciais para SMB)"
            try:
                # Envia um byte vazio para forçar uma resposta de texto do serviço
                s.send(b"\r\n")
                banner = (
                    s.recv(1024).decode("utf-8", errors="ignore").strip()[:50]
                )
            except:
                pass
            print(
                f"Porta {port}/tcp: ABERTA | Razão: connection-established | Banner: {banner}"
            )
        else:
            # Fornece o motivo do erro técnico
            reason = "timeout" if (end_time - start_time) >= 1.4 else "rejected"
            print(f"Porta {port}/tcp: FECHADA/FILTRADA | Razão: {reason}")

        s.close()


# --- Execução Principal ---
print(f"Alvo: {target} (Omitindo ping devido ao '-Pn')")
print("-" * 60)

try:
    # Tenta usar o Scapy primeiro
    scapy_scan()
except ImportError:
    # Se o Scapy não carregar de forma alguma, vai direto para o Socket
    print("[!] Scapy indisponível no ambiente de execução.")
    socket_scan()

import socket

# Configura o script para ouvir em todas as placas de rede do PC do trabalho
HOST = '0.0.0.0'
PORT = 4444 

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print(f"[*] Aguardando conexão do Kali de casa na porta {PORT}...")

conn, addr = server.accept()
print(f"[*] Conexão estabelecida de: {addr}")

# Loop para enviar comandos para o Kali e receber as respostas
while True:
    comando = input("Kali_Shell> ")
    if comando.lower() == 'exit':
        conn.send(b'exit')
        break
    if len(str.encode(comando)) > 0:
        conn.send(str.encode(comando))
        resposta_client = str(conn.recv(10240), "utf-8")
        print(resposta_client, end="")

conn.close()
server.close()

from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import sys

# Armazenamento de estado global
comando_pendente = ""
resposta_recebida = ""
novo_comando_disponivel = threading.Event()
resposta_disponivel = threading.Event()

class RobustWebShellHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # Desativa logs repetitivos no terminal

    def do_GET(self):
        global comando_pendente
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        
        # O cliente de casa bate aqui para pegar o comando
        self.wfile.write(str.encode(comando_pendente))
        comando_pendente = "" # Limpa após entregar

    def do_POST(self):
        global resposta_recebida
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        self.send_response(200)
        self.end_headers()
        
        # O cliente de casa bate aqui para entregar o resultado do comando
        resposta_recebida = post_data.decode('utf-8')
        resposta_disponivel.set() # Avisa a thread principal que a resposta chegou

def prompt_loop():
    global comando_pendente
    print("[*] Servidor Web ativo na porta 8080. Aguardando comandos...")
    
    while True:
        try:
            comando = input("\nKali_WebShell> ")
            if comando.lower() == 'exit':
                print("[*] Encerrando servidor...")
                sys.exit(0)
            
            if not comando.strip():
                continue
                
            resposta_disponivel.clear()
            comando_pendente = comando
            
            # Aguarda o cliente buscar e responder (máximo de 15 segundos de timeout)
            if resposta_disponivel.wait(timeout=15):
                print(resposta_recebida, end="")
            else:
                print("\n[-] Erro: Timeout. O Kali de casa demorou para responder.")
                comando_pendente = "" # Cancela o comando pendente por timeout
                
        except (KeyboardInterrupt, SystemExit):
            break

if __name__ == '__main__':
    # Roda o servidor HTTP em uma thread separada para não travar o input do terminal
    server_address = ('0.0.0.0', 8080)
    httpd = HTTPServer(server_address, RobustWebShellHandler)
    
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # Inicia o loop de comandos interativo
    prompt_loop()

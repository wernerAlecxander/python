import requests
import json

url = "http://192.168.4.1"  # Endpoint padrão de autenticação Huawei
headers = {
    "Content-Type": "application/json",
    "Referer": "http://192.168.4.1"
}

# Lista estrita e segura (Evita o bloqueio total do aparelho)
senhas_para_testar = ["admin", "admin123"]

def testar_senha(senha):
    payload = {
        "username": "admin",
        "password": senha
    }
    try:
        # Envia a requisição de login para o roteador
        response = requests.post(url, data=json.dumps(payload), headers=headers, timeout=3)
        
        # Analisa a resposta do Huawei
        if response.status_code == 200:
            dados = response.json()
            # Se a API não retornar erro de senha, a credencial é válida
            if "error" not in dados or dados.get("error") == 0:
                print(f"[VULNERABILIDADE CRÍTICA] Roteador acessível com a senha: {senha}")
                return True
        print(f"[SEGURO] Tentativa com a senha '{senha}' falhou ou foi rejeitada.")
    except Exception as e:
        print(f"[ERRO] Não foi possível conectar ao roteador: {e}")
    return False

print("Iniciando verificação controlada de credenciais no Huawei AX2...")
for s in senhas_para_testar:
    if testar_senha(s):
        break
print("Análise encerrada.")

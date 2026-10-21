# gerador.py
import itertools
import string
import sys

def gerar_senhas_para_powershell(palavras_gregas, numeros, especiais):
    # 1. Expandir a lista grega
    lista_grega_expandida = []
    for palavra in palavras_gregas:
        lista_grega_expandida.append(palavra.lower())
        lista_grega_expandida.append(palavra.capitalize())
        lista_grega_expandida.append(palavra.upper())
    lista_grega_expandida = list(dict.fromkeys(lista_grega_expandida))

    # 2. Gerar as combinacoes nos mesmos loops do seu script original
    for tam_num in range(1, 5):
        for tam_esp in range(1, 5):
            for pal_grega in lista_grega_expandida:
                comb_num = list(itertools.product(numeros, repeat=tam_num))
                comb_esp = list(itertools.product(especiais, repeat=tam_esp))

                for c_num in comb_num:
                    str_num = "".join(c_num)

                    for c_esp in comb_esp:
                        str_esp = "".join(c_esp)

                        # Padrao 1: Palavra + Numero + Especial
                        tentativa_1 = pal_grega + str_num + str_esp
                        print(tentativa_1, flush=True)

                        # Padrao 2: Palavra + Especial + Numero
                        tentativa_2 = pal_grega + str_esp + str_num
                        print(tentativa_2, flush=True)

if __name__ == "__main__":
    alfabeto_grego = [
        "alpha", "beta", "gamma", "delta", "epsilon", "zeta", "eta", "theta",
        "iota", "kappa", "lambda", "mu", "nu", "xi", "omicron", "pi", 
        "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega"
    ]
    numeros_possiveis = string.digits
    caracteres_especiais = "!@#$%&*+"

    # Executa a geracao direcionando a saida padrao
    gerar_senhas_para_powershell(alfabeto_grego, numeros_possiveis, caracteres_especiais)

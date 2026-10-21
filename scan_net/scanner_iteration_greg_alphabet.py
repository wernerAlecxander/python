import itertools
import string
import time


def brute_force_completo(senha_alvo, palavras_gregas, numeros, especiais):
    print(f"Iniciando forca bruta para: '{senha_alvo}'...")
    inicio = time.time()
    tentativas = 0

    lista_grega_expandida = []
    for palavra in palavras_gregas:
        lista_grega_expandida.append(palavra.lower())
        lista_grega_expandida.append(palavra.capitalize())
        lista_grega_expandida.append(palavra.upper())
    lista_grega_expandida = list(dict.fromkeys(lista_grega_expandida))

    total_palavras = len(lista_grega_expandida)
    print(f"Total de variacoes de palavras gregas: {total_palavras}")

    total_combinacoes_calculadas = 0
    for t_n in range(1, 5):
        for t_e in range(1, 5):
            total_combinacoes_calculadas += (
                total_palavras * (10**t_n) * (8**t_e) * 2
            )

    print(
        f"Total maximo de senhas possiveis no pior cenario: {total_combinacoes_calculadas:,}".replace(
            ",", "."
        )
    )

    for tam_num in range(1, 5):
        for tam_esp in range(1, 5):
            print(
                f"\n[Progresso] Testando tamanhos: numeros ({tam_num}) e especiais ({tam_esp})..."
            )

            if tentativas > 0:
                tempo_decorrido = time.time() - inicio
                velocidade = tentativas / tempo_decorrido
                restantes = total_combinacoes_calculadas - tentativas
                tempo_restante = restantes / velocidade
                print(
                    f"└─ Velocidade atual: {velocidade:.0f} senhas/seg | Tempo restante estimado: {tempo_restante:.2f} segundos"
                )

            for pal_grega in lista_grega_expandida:
                comb_num = list(itertools.product(numeros, repeat=tam_num))
                comb_esp = list(itertools.product(especiais, repeat=tam_esp))

                for c_num in comb_num:
                    str_num = "".join(c_num)

                    for c_esp in comb_esp:
                        str_esp = "".join(c_esp)

                        tentativas += 1
                        tentativa_1 = pal_grega + str_num + str_esp
                        if tentativa_1 == senha_alvo:
                            exibir_sucesso(tentativa_1, tentativas, inicio)
                            return

                        tentativas += 1
                        tentativa_2 = pal_grega + str_esp + str_num
                        if tentativa_2 == senha_alvo:
                            exibir_sucesso(tentativa_2, tentativas, inicio)
                            return

    print("\nSenha nao encontrada nos padroes estabelecidos.")


def exibir_sucesso(senha_encontrada, tentativas, inicio):
    fim = time.time()
    tempo_total = fim - inicio
    print(f"\n[Sucesso!] Senha encontrada: '{senha_encontrada}'")
    print(f"Total de tentativas: {tentativas:,}".replace(",", "."))
    print(f"Tempo gasto: {tempo_total:.4f} segundos")


if __name__ == "__main__":
    alfabeto_grego = [
        "alpha",
        "beta",
        "gamma",
        "delta",
        "epsilon",
        "zeta",
        "eta",
        "theta",
        "iota",
        "kappa",
        "lambda",
        "mu",
        "nu",
        "xi",
        "omicron",
        "pi",
        "rho",
        "sigma",
        "tau",
        "upsilon",
        "phi",
        "chi",
        "psi",
        "omega",
    ]

    numeros_possiveis = string.digits
    caracteres_especiais = "!@#$%&*+"

    senha_secreta = "ALPHA#$42"

    brute_force_completo(
        senha_secreta, alfabeto_grego, numeros_possiveis, caracteres_especiais
    )

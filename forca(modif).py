import random

#cria uma lista de palavras que serão sorteadas.
palavras = ['python','programacao','computador','aula','variavel']

#escolhemos da das palavras
palavra_sorteada = random.choice(palavras)

#Criamos uma string com traços que representam as letras
palavra_escondida = '*' * len(palavra_sorteada)

#criamos uma lista vazia para armazenar as letras que já foram faladas
letras_adivinhadas = []

max_tentativas = 6
letras_erradas = 0
tot_let_pal_sort = len(palavra_sorteada)


while True:
  #mostra na tela a palavra escondida
    print(palavra_escondida)

  #pedimos ao jogador para digitar uma letra
    letra = input('Digite uma letra: ')

  #verificamos se a letra ja foi digitada
    if letra in letras_adivinhadas:
        print('Vocẽ ja digitou essa letra. Tente outra por favor')
        continue

  #adicionar a letra a lista de letras digitadas
    letras_adivinhadas.append(letra)

  #verificar se a letra digitada esta na palavra sorteada
    if letra in palavra_sorteada:
        lista = []
        for indice in range(tot_let_pal_sort):
            if letra == palavra_sorteada[indice]: 
                lista.append(letra)
            else:
                lista.append(palavra_escondida[indice])
                letras_erradas += 1.0
                print(letras_erradas)
        palavra_escondida = ''.join(lista) # se jogador digitou a letra a então teremos = a**a

    else: #letra não esta na palavra sorteada
        max_tentativas -= 1
        print(f'Letra não encontrada. Você tem mais {max_tentativas} tentativas')
    
    porcent_acertos = (((tot_let_pal_sort - letras_erradas)/tot_let_pal_sort)*100)

  #Verificamos se o jogador ganhou ou perdeu
    if palavra_escondida ==  palavra_sorteada:
        print('Parabéns, você ganhou!!')
        break
    elif max_tentativas == 0:
        print(f'Você perdeu. A palavra era {palavra_sorteada}.')
        print(f'sua porcentagem de letras certas foi: {porcent_acertos}.')
        print(letras_erradas)
        print(tot_let_pal_sort)
        break
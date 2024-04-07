import random

# Crie uma lista de palavras
palavras = ['python', 'programacao', 'computador', 'algoritmo', 'variavel', 'lista']

# Escolha uma palavra aleatoriamente
palavra = random.choice(palavras)

# Crie uma string com traços para representar as letras não adivinhadas
palavra_escondida = '*' * len(palavra)

# Crie uma lista para acompanhar as letras já adivinhadas
letras_adivinhadas = []

# Defina o número máximo de tentativas
max_tentativas = 6

# Loop principal do jogo
while True:
    # Exiba a palavra escondida
    print(palavra_escondida)

    # Peça ao jogador para digitar uma letra
    letra = input('Digite uma letra: ')

    # Verifique se a letra já foi adivinhada antes
    if letra in letras_adivinhadas:
        print('Você já tentou essa letra. Tente outra.')
        continue

    # Adicione a letra à lista de letras já adivinhadas
    letras_adivinhadas.append(letra)

    # Verifique se a letra está na palavra
    if letra in palavra:
        # Se a letra está na palavra, atualize a string com traços
        # para mostrar a letra adivinhada
        palavra_escondida = ''.join(letra if letra == palavra[indice] 
                                    else palavra_escondida[indice] for 
                                    indice in range (len(palavra)))
        # lista = []
        # for indice in range(len(palavra)):
        #   if letra == palavra[indice]:
        #     lista.append(letra)
        #   else:
        #     lista.append(palavra_escondida[indice])
        # palavra_escondida = ''.join(lista)
    else:
        # Se a letra não está na palavra, diminua o número de tentativas restantes
        max_tentativas -= 1
        print('Letra não encontrada. Você tem mais', max_tentativas, 'tentativas.')

    # Verifique se o jogador ganhou ou perdeu
    if palavra_escondida == palavra:
        print('Parabéns, você ganhou!')
        break
    elif max_tentativas == 0:
        print('Você perdeu. A palavra era', palavra)
        break
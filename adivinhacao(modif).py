import random
import math

numero_minimo = int(input('Qual o numero minimo do intervalo?\n'))
numero_maximo = int(input('Qual o numero máximo do intervalo?\n'))
numero_sorteado = random.randint(numero_minimo, numero_maximo)
probabilidade = float(input('digite um número maior que zero (0) e menor que um (1)\n'))


if((probabilidade <= 0) or (probabilidade >= 1)):
    desconto = 0.111111111
    probabilidade = (probabilidade - desconto)
    probabilidade = (1/probabilidade)

tentativa = math.trunc((numero_maximo - numero_minimo)*probabilidade)
       
if (tentativa == int(numero_maximo - numero_minimo)):
    tentativa = math.floor(int(tentativa - probabilidade))

if (tentativa >= (tentativa * 0.9)):
    tentativa = math.floor(tentativa - numero_sorteado)
    if (tentativa <= 0):
        tentativa = 1
    
print(f'você tem {tentativa} tentativas')
print('---------------------')
print(numero_sorteado)
print('=================')
print(probabilidade)

    #tentativa = int(input(f'Digite um numero entre {numero_minimo} e {numero_maximo}.\n'))

""""
while True:
    if tentativa == numero_sorteado:
        print('Parabéns você acertou o numero.')
        break
    else:
        tentativa -= 1
        if tentativa == 0:
            print(f'Você não acertou o número e não tem mais tentativas. O número era {numero_sorteado}')
            break
        else:
            print(f'Número errado. Tente novamente. Você ainda tem {tentativa} tentativas.')
"""
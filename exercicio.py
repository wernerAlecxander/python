import time
import os.path

def geraLog(texto,nome_arquivo):
    if os.path.isfile('log.txt') is False:
        print('Criando arquivo')
    
    arquivo = open(nome_arquivo,'a')
    now = time.localtime()
    # now_formatado = time.strftime('%d/%m/%y as %H:%M:%S', now)
    now_formatado = time.strftime('%x as %X')

    arquivo.write(f'{now_formatado} -> {texto}\n')
    arquivo.close()

geraLog('usuário logou no sistema','log.txt')
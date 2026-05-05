import math
import random
def rolar_dados(x):
    valores=[]
    for i in range(x):
        valores.append(random.randint(1,6))
    return valores
def guardar_dado(r,g,n):
    g.append(r[n])
    r.pop(n)
    return [r,g]
def remover_dado(r,g,n):
    r.append(g[n])
    g.pop(n)
    return [r,g]
def calcula_pontos_regra_simples(f):
    d={1:0,2:0,3:0,4:0,5:0,6:0}
    for i in range(len(f)):
        if f[i]==1:
            d[1]+=1
        elif f[i]==2:
            d[2]+=2
        elif f[i]==3:
            d[3]+=3
        elif f[i]==4:
            d[4]+=4
        elif f[i]==5:
            d[5]+=5
        elif f[i]==6:
            d[6]+=6
    return d
def calcula_pontos_soma(lista):
    valor=0
    for o in range(len(lista)):
        valor+=lista[o]
    return valor
def calcula_pontos_sequencia_baixa(r):
    r = list(set(r))
    r.sort()
    s1 = [1,2,3,4]
    s2 = [2,3,4,5]
    s3 = [3,4,5,6]
    for seq in [s1, s2, s3]:
        ok = True
        for num in seq:
            if num not in r:
                ok = False
                break
        if ok==True:
            return 15
    return 0
def calcula_pontos_sequencia_alta(r):
    r = list(set(r))
    r.sort()
    if len(r)>4:
        for i in range(len(r)-1):
            if r[i+1]!=r[i]+1:
                return 0
        return 30
    else:
        return 0
def calcula_pontos_full_house(r):
    um=r.count(1)
    dois=r.count(2)
    tres=r.count(3)
    quatro=r.count(4)
    cinco=r.count(5)
    seis=r.count(6)
    soma=0
    l=[um,dois,tres,quatro,cinco,seis]
    if 2 in l:
        if 3 in l:
            for i in range(len(r)):
                soma+=r[i]
            return soma
    return 0
def calcula_pontos_quadra(r):
    um=r.count(1)
    dois=r.count(2)
    tres=r.count(3)
    quatro=r.count(4)
    cinco=r.count(5)
    seis=r.count(6)
    soma=0
    l=[um,dois,tres,quatro,cinco,seis]
    for i in range(len(l)):
        if l[i]>3:
            for i in range(len(r)):
                soma+=r[i]
            break
    return soma
def calcula_pontos_quina(r):
    um=r.count(1)
    dois=r.count(2)
    tres=r.count(3)
    quatro=r.count(4)
    cinco=r.count(5)
    seis=r.count(6)
    soma=0
    l=[um,dois,tres,quatro,cinco,seis]
    for i in range(len(l)):
        if l[i]>4:
            return 50
    return 0
def calcula_pontos_regra_avancada(r):
    d={}
    d['cinco_iguais']=calcula_pontos_quina(r)
    d['full_house']=calcula_pontos_full_house(r)
    d['quadra']=calcula_pontos_quadra(r)
    d['sem_combinacao']=calcula_pontos_soma(r)
    d['sequencia_alta']=calcula_pontos_sequencia_alta(r)
    d['sequencia_baixa']=calcula_pontos_sequencia_baixa(r)
    return d
def faz_jogada(r,ctg,car):
    s=calcula_pontos_regra_simples(r)
    a=calcula_pontos_regra_avancada(r)
    if ctg in {'1','2','3','4','5','6'}:
        c=int(ctg)
        car['regra_simples'][c]=s[c]
        return car
    else:
        car['regra_avancada'][ctg]=a[ctg]
        return car
def imprime_cartela(cartela):
    print("Cartela de Pontos:")
    print("-"*25)    
    for i in range(1, 7):
        filler = " " * (15 - len(str(i)))
        if cartela['regra_simples'][i] != -1:
            print(f"| {i}: {filler}| {cartela['regra_simples'][i]:02} |")
        else:
            print(f"| {i}: {filler}|    |")
    for i in cartela['regra_avancada'].keys():
        filler = " " * (15 - len(str(i)))
        if cartela['regra_avancada'][i] != -1:
            print(f"| {i}: {filler}| {cartela['regra_avancada'][i]:02} |")
        else:
            print(f"| {i}: {filler}|    |")
    print("-"*25)

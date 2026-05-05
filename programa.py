from funcoes import rolar_dados, guardar_dado, remover_dado, faz_jogada, imprime_cartela

def nova_cartela():
    return {
        'regra_simples': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1},
        'regra_avancada': {
            'sem_combinacao': -1,
            'quadra': -1,
            'full_house': -1,
            'sequencia_baixa': -1,
            'sequencia_alta': -1,
            'cinco_iguais': -1
        }
    }

def combinacoes_validas(cartela):
    validas = []
    for k in cartela['regra_simples']:
        validas.append(str(k))
    for k in cartela['regra_avancada']:
        validas.append(k)
    return validas

def cartela_cheia(cartela):
    for v in cartela['regra_simples'].values():
        if v == -1:
            return False
    for v in cartela['regra_avancada'].values():
        if v == -1:
            return False
    return True

def pontuacao_final(cartela):
    total = 0
    soma_simples = 0
    for v in cartela['regra_simples'].values():
        if v != -1:
            total += v
            soma_simples += v
    for v in cartela['regra_avancada'].values():
        if v != -1:
            total += v
    if soma_simples >= 63:
        total += 35
    return total

def ler_opcao(dados_rolados, dados_guardados):
    print(f"Dados rolados: {dados_rolados}")
    print(f"Dados guardados: {dados_guardados}")
    print("Digite 1 para guardar um dado, 2 para remover um dado, 3 para rerrolar, 4 para ver a cartela ou 0 para marcar a pontuação:")
    return input(">")

cartela = nova_cartela()
imprime_cartela(cartela)

for rodada in range(12):
    dados_rolados = rolar_dados(5)
    dados_guardados = []
    rerrolagens = 0
    jogada_feita = False

    opcao = ler_opcao(dados_rolados, dados_guardados)

    while not jogada_feita:
        if opcao == "1":
            print("Digite o índice do dado a ser guardado (0 a 4):")
            idx = int(input(">"))
            dados_rolados, dados_guardados = guardar_dado(dados_rolados, dados_guardados, idx)
            opcao = ler_opcao(dados_rolados, dados_guardados)

        elif opcao == "2":
            print("Digite o índice do dado a ser removido (0 a 4):")
            idx = int(input(">"))
            dados_rolados, dados_guardados = remover_dado(dados_rolados, dados_guardados, idx)
            opcao = ler_opcao(dados_rolados, dados_guardados)

        elif opcao == "3":
            if rerrolagens >= 2:
                print("Você já usou todas as rerrolagens.")
            else:
                dados_rolados = rolar_dados(len(dados_rolados))
                rerrolagens += 1
            opcao = ler_opcao(dados_rolados, dados_guardados)

        elif opcao == "4":
            imprime_cartela(cartela)
            opcao = ler_opcao(dados_rolados, dados_guardados)

        elif opcao == "0":
            print("Digite a combinação desejada:")
            todos = dados_rolados + dados_guardados
            validas = combinacoes_validas(cartela)

            while True:
                combinacao = input(">")
                if combinacao not in validas:
                    print("Combinação inválida. Tente novamente.")
                    continue
                if combinacao in [str(k) for k in cartela['regra_simples']]:
                    chave = int(combinacao)
                    if cartela['regra_simples'][chave] != -1:
                        print("Essa combinação já foi utilizada.")
                        continue
                else:
                    if cartela['regra_avancada'][combinacao] != -1:
                        print("Essa combinação já foi utilizada.")
                        continue
                cartela = faz_jogada(todos, combinacao, cartela)
                jogada_feita = True
                break

            if cartela_cheia(cartela):
                break

        else:
            print("Opção inválida. Tente novamente.")
            opcao = input(">")

    if cartela_cheia(cartela):
        break

imprime_cartela(cartela)
total = pontuacao_final(cartela)
print(f"Pontuação total: {total}")
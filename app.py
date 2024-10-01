from flask import Flask, render_template, request
import random

app = Flask(__name__)

# Definindo partidos e candidatos
partidos = {
    "União": 14,
    "PDT": 14,
    "MDB": 14,
    "PC DO B": 6,
    "AVANTE": 14,
    "AGIR": 13,
    "PT": 8,
    "PP": 14,
    "PSD": 11
}

def distribuir_votos_aleatorios(total_votos, num_candidatos):
    if num_candidatos == 0:
        return []
    
    # Gera votos aleatórios, garantindo que a soma seja igual a total_votos
    votos = [random.randint(0, total_votos // num_candidatos) for _ in range(num_candidatos - 1)]
    votos.append(total_votos - sum(votos))  # O último candidato recebe os votos restantes
    
    # Embaralha a lista de votos
    random.shuffle(votos)
    return votos

def calcular_coeficiente_partidario(votos, total_votos, cadeiras):
    coeficientes = {}
    for partido, voto in votos.items():
        # Calcula a porcentagem de votos
        porcentagem = (voto / total_votos) * 100
        # Calcula o número de cadeiras baseadas no quociente
        cadeiras_ocupadas = voto // (total_votos // cadeiras)
        coeficientes[partido] = {
            'porcentagem': porcentagem,
            'cadeiras': cadeiras_ocupadas
        }
    return coeficientes

def calcular_quociente_eleitoral(total_votos, cadeiras):
    return total_votos / cadeiras

def calcular_vereadores(votos):
    total_eleitores = 30001
    cadeiras = 13

    # Calcular o quociente eleitoral
    quociente_eleitoral = calcular_quociente_eleitoral(sum(votos.values()), cadeiras)

    # Cálculo da quantidade de vereadores por partido
    vereadores = {partido: 0 for partido in votos}
    quocientes = {}

    # Cálculo dos quocientes
    for partido, voto in votos.items():
        quocientes[partido] = voto / (vereadores[partido] + 1)

    # Distribuindo as cadeiras
    for _ in range(cadeiras):
        partido_elegido = max(quocientes, key=quocientes.get)
        vereadores[partido_elegido] += 1
        quocientes[partido_elegido] = votos[partido_elegido] / (vereadores[partido_elegido] + 1)

    # Montando a lista de vereadores eleitos
    vereadores_eleitos = []
    for partido, num in vereadores.items():
        # Calcular 10% do quociente eleitoral
        minimo_votos_necessarios = 0.10 * quociente_eleitoral
        
        # Verifica se o partido tem votos suficientes e se tem cadeiras
        if votos[partido] >= minimo_votos_necessarios and num > 0:
            votos_por_candidato = distribuir_votos_aleatorios(votos[partido], num)  # Distribuição aleatória dos votos
            for i in range(num):
                vereadores_eleitos.append({
                    'partido': partido,
                    'candidato': f"Candidato {i + 1} do {partido}",
                    'votos': votos_por_candidato[i],  # Exibe os votos aleatórios
                })

    # Ordenar vereadores_eleitos em ordem decrescente de votos
    vereadores_eleitos.sort(key=lambda x: x['votos'], reverse=True)

    # Agrupando por partido
    resultado_agrupado = {}
    for vereador in vereadores_eleitos:
        if vereador['partido'] not in resultado_agrupado:
            resultado_agrupado[vereador['partido']] = []
        resultado_agrupado[vereador['partido']].append(vereador)

    # Calcular coeficiente partidário
    coeficientes_partidarios = calcular_coeficiente_partidario(votos, sum(votos.values()), cadeiras)

    return resultado_agrupado, coeficientes_partidarios

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        votos = {partido: int(request.form[partido]) for partido in partidos}
        resultados, coeficientes_partidarios = calcular_vereadores(votos)
        return render_template('resultados.html', resultados=resultados, coeficientes=coeficientes_partidarios)

    return render_template('index.html', partidos=partidos)

if __name__ == '__main__':
    app.run(debug=True)

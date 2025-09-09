# CalendarioFinanceiro
O pacote CalendarioFinanceiro fornece funcionalidades para trabalhar com dias úteis, considerando diferentes calendários, como "onshore" (Brasil) e "offshore".

## Instalação
Para utilizar o pacote CalendarioFinanceiro, você precisa instalá-lo primeiro. Isso pode ser feito utilizando o gerenciador de pacotes pip. Execute o seguinte comando no terminal:
```shell
pip install calendariofinanceiro
```

## Uso Básico
```py
from datetime import date
from calendariofinanceiro import CalendarioFinanceiro

# Inicializa o calendário de feriados "onshore"
c_on = CalendarioFinanceiro("onshore")

# Inicializa o calendário de feriados "offshore"
c_off = CalendarioFinanceiro("offshore")

# Calcula a data após adicionar um número de dias úteis
nova_data = c_on.soma_dias_uteis(date(2023, 8, 1), 5)

# Arredonda uma data para o próximo dia útil
data_arredondada = c_off.arredonda_dia_util(date(2023, 8, 10))

# Monta uma lista de dias úteis entre duas datas
lista_dias_uteis = c_on.monta_lista_dias_uteis(date(2023, 8, 1), date(2023, 8, 15))

# Monta uma lista de datas de fechamento retroativas
lista_fechamentos = c_off.monta_lista_fechamentos_anteriores(date(2023, 8, 31), 3)

# Obtém a data de fechamento do mês anterior
fechamento_mes_anterior = c_on.fechamento_mes_anterior(date(2023, 8, 15))
```

## Métodos Disponíveis
### soma_dias_uteis(data_dt: date, dias: int) -> date
Soma um número específico de dias úteis a uma data de referência.

### arredonda_dia_util(data_dt: date, arredonda_pra_cima: bool = True) -> date
Arredonda uma data para o próximo ou último dia útil, dependendo da opção escolhida.

### monta_lista_dias_uteis(data_inicial: date, data_final: date, incluir_primeira: bool = True) -> List[date]
Monta uma lista de dias úteis entre as datas de referência, com a opção de incluir ou não a primeira data.

### monta_lista_fechamentos_anteriores(data_final: date, numero_meses: int) -> List[date]
Monta uma lista de datas de fechamento para um número especificado de meses retroativos a partir da data final.

### fechamento_mes_anterior(data: date) -> date
Retorna a data de fechamento do mês anterior à data fornecida.

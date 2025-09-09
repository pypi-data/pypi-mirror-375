from datetime import date
from typing import Literal, List
import workdays

from calendariofinanceiro.feriados_on import feriados_on
from calendariofinanceiro.feriados_off import feriados_off


class CalendarioFinanceiro:
    def __init__(self, calendario: Literal["onshore", "offshore"]):
        if calendario == "onshore":
            self.feriados = feriados_on
        elif calendario == "offshore":
            self.feriados = feriados_off

    def soma_dias_uteis(self, data_dt: date, dias: int) -> date:
        """
        Soma um número específico de dias úteis a uma data de referência.

        :param data_dt: A data de referência.
        :param dias: O número de dias úteis a serem adicionados
        (pode ser negativo para subtrair dias).
        :return: A nova data após adicionar o número de dias especificado.
        """
        return workdays.workday(data_dt, dias, self.feriados)

    def arredonda_dia_util(
        self, data_dt: date, arredonda_pra_cima: bool = True
    ) -> date:
        """
        Se a data for um dia útil, retorna ela mesma.
        Caso contrário, pega o dia útil anterior ou posterior,
        dependendo da opção escolhida.

        :param data_dt: A data de referência para o arredondamento.
        :param arredonda_pra_cima: Se True, arredonda para o próximo dia útil.
        Caso contrário, arredonda para o último dia útil.
        :return: A nova data após arredondamento
        """
        offset = 1 if arredonda_pra_cima else -1
        return self.soma_dias_uteis(
            self.soma_dias_uteis(data_dt, -offset), offset
        )

    def monta_lista_dias_uteis(
        self,
        data_inicial: date,
        data_final: date,
        incluir_primeira: bool = True,
    ) -> List[date]:
        """
        Monta uma lista de dias úteis entre as datas de referência,
        com a opção de incluir ou não a primeira data.

        :param data_inicial: A data inicial do intervalo.
        :param data_final: A data final do intervalo.
        :param incluir_primeira: Se True, inclui a primeira data na lista.
        :return: Uma lista de datas úteis entre as datas de referência.
        """
        lista_dias_uteis = []
        data_i = data_inicial
        while data_i <= data_final:
            lista_dias_uteis.append(data_i)
            data_i = self.soma_dias_uteis(data_i, 1)
        if not incluir_primeira:
            lista_dias_uteis.pop(0)
        return lista_dias_uteis

    def monta_lista_fechamentos_anteriores(
        self, data_final: date, numero_meses: int
    ) -> List[date]:
        """
        Monta uma lista de datas de fechamento para um número especificado
        de meses retroativos a partir da data final.

        :param data_final: A data final a partir da qual a lista de fechamentos
         será construída.
        :param numero_meses: O número de meses retroativos para os quais
         as datas de fechamento serão geradas.
        :return: Uma lista de datas de fechamento retroativas.
        """
        lista_fechamentos = []
        data_i = data_final
        for i in range(numero_meses):
            lista_fechamentos.append(data_i)
            data_i = self.soma_dias_uteis(
                date(data_i.year, data_i.month, 1), -1
            )
        return lista_fechamentos

    def fechamento_mes_anterior(self, data: date) -> date:
        """
        Retorna a data de fechamento do mês anterior à data fornecida.

        :param data: A data de referência para a qual se deseja obter
        o fechamento do mês anterior.
        :return: A data de fechamento do mês anterior.
        """
        fechamento_m1 = self.soma_dias_uteis(
            date(data.year, data.month, 1), -1
        )
        return fechamento_m1

    def fechamento_ano_anterior(self, data: date) -> date:
        """
        Retorna a data de fechamento do ano anterior à data fornecida.

        :param data: A data de referência para a qual se deseja obter
        o fechamento do ano anterior.
        :return: A data de fechamento do ano anterior.
        """
        fechamento_a1 = self.soma_dias_uteis(date(data.year, 1, 1), -1)
        return fechamento_a1

    def data_12m_anterior(self, data: date) -> date:
        """
        Retorna a data retroagida 12M da data fornecida.

        :param data: A data de referência para a qual se deseja obter
        a data retroagida 12M.
        :return: A data retroagida 12M da data fornecida.
        """

        if data.month != self.soma_dias_uteis(data, 1).month:
            # Cenário 1: A data fornecida é uma data de fechamento.
            # — > Retornamos a data de fechamento do mesmo mês, mas do ano
            # passado.
            data_12m = self.busca_fechamento_mes_ano(data.month, data.year - 1)
        else:
            # Cenário 2: A data fornecida é não é fechamento de mês.
            # — > Retornamos a data retroagida exatamente 1 ano, arredondando
            # para baixo.
            data_12m = self.arredonda_dia_util(
                date(data.year - 1, data.month, data.day),
                arredonda_pra_cima=False,
            )
        return data_12m

    def data_24m_anterior(self, data: date) -> date:
        """
        Retorna a data de fechamento 24M anterior à data fornecida.

        :param data: A data de referência para a qual se deseja obter
        o fechamento 24M anterior.
        :return: A data de fechamento 24M anterior.
        """

        if data.month != self.soma_dias_uteis(data, 1).month:
            # Cenário 1: A data fornecida é uma data de fechamento.
            # — > Retornamos a data de fechamento do mesmo mês, mas do ano
            # retrasado.
            data_24m = self.busca_fechamento_mes_ano(data.month, data.year - 2)
        else:
            # Cenário 2: A data fornecida é não é fechamento de mês.
            # — > Retornamos a data retroagida exatamente 2 ano, arredondando
            # para baixo.
            data_24m = self.arredonda_dia_util(
                date(data.year - 2, data.month, data.day),
                arredonda_pra_cima=False,
            )
        return data_24m

    def busca_fechamento_mes_ano(self, mes: int, ano: int) -> date:
        """
        A partir de um mês e ano, constrói a data de fechamento referente.

        :param mes: Mês de referência do fechamento (Janeiro=1)
        :param ano: Ano de referência do fechamento
        :return: A data de fechamento correspondente ao mês e ano passados.
        """
        proximo_mes = mes + 1 if mes < 12 else 1
        proximo_ano = ano if mes < 12 else ano + 1
        fechamento = self.soma_dias_uteis(
            date(proximo_ano, proximo_mes, 1), -1
        )
        return fechamento

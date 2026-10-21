"""Previsões de geração solar comparadas em scripts/avaliar_previsao.py (README, seção 5.2).

Trabalham sobre o perfil horário do INMET ({hora local: kW/m2}). Cada função recebe o perfil e a hora
a prever e usa apenas dados anteriores a ela."""
from datetime import timedelta

HOUR = timedelta(hours=1)
DAYS = 7


def persistence(profile, hour):
    """Valor da hora anterior (o que o motor usa hoje, com passo de 15 minutos)."""
    return profile.get(hour - HOUR)


def same_hour_average(profile, hour, days=DAYS):
    """Média da mesma hora nos `days` dias anteriores; None se faltar algum."""
    values = [profile.get(hour - timedelta(days=day)) for day in range(1, days + 1)]
    return None if None in values else sum(values) / days

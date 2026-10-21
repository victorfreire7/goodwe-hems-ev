"""Laço do simulador contra a API: envia as leituras de um passo e aplica os comandos da resposta
(README, seção 3.4)."""
import json
import time
import urllib.error
import urllib.request

from simulator.config import DEFAULT_HOUSES, STEPS_PER_DAY
from simulator.house import House

IDLE_COMMAND = {"ev_charge_power_kw": 0.0, "battery_power_kw": 0.0}


def http_sender(url, simulation):
    """Devolve `send(readings) -> lista de comandos`, que chama POST /readings."""
    def send(readings):
        request = urllib.request.Request(
            url.rstrip("/") + "/readings", data=json.dumps(readings).encode(), method="POST",
            headers={"Content-Type": "application/json", "X-Simulation-Id": simulation})
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.loads(response.read())
        except urllib.error.HTTPError as error:
            raise RuntimeError(f"API recusou o passo ({error.code}): {error.read().decode()}") from error
    return send


def simulate(send, *, days, start, seed, weather, houses=DEFAULT_HOUSES,
             seconds_per_step=0.0, on_step=None):
    """Roda `days` dias. `send` recebe as leituras de todas as casas do passo e devolve os comandos.

    O comando de um passo vale para o passo seguinte. `seconds_per_step` > 0 espera esse tempo
    real entre passos (modo acelerado); 0 roda sem espera (modo lote)."""
    simulated = [House(config, start, days, weather, seed) for config in houses]
    commands = {house.config.house_id: IDLE_COMMAND for house in simulated}
    for index in range(days * STEPS_PER_DAY):
        readings = [house.step(index, commands[house.config.house_id]) for house in simulated]
        started = time.monotonic()
        commands = {command["house_id"]: command for command in send(readings)}
        if on_step:
            on_step(index, readings, commands)
        pause = seconds_per_step - (time.monotonic() - started)
        if pause > 0:
            time.sleep(pause)

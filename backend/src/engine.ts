import { ApiError, type Decide } from './types.js';
import { applyTargets, validateEngineResult } from './validation.js';

export const neutralDecide: Decide = async readings => ({
  commands: readings.map(reading => ({ house_id: reading.house_id, timestamp: reading.timestamp,
    ev_charge_power_kw: 0, battery_power_kw: 0, market: { sold_kwh: 0, bought_kwh: 0 },
    reason: 'modo neutro: motor HTTP ainda não integrado' })),
  trades: [], offers: [], orders: [],
});

export function httpDecide(url: string, timeoutMs: number, exportValue: number, optimized: boolean): Decide {
  return async (readings, targets) => {
    try {
      const response = await fetch(new URL('/decide', url), {
        method: 'POST', headers: { 'content-type': 'application/json' },
        signal: AbortSignal.timeout(timeoutMs),
        body: JSON.stringify({ readings: applyTargets(readings, targets), ev_targets: targets,
          export_value_per_kwh: exportValue, optimized }),
      });
      if (!response.ok) throw new ApiError(502, 'Motor recusou o passo.');
      return validateEngineResult(await response.json(), readings);
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError(502, 'Motor indisponível ou tempo de resposta excedido.');
    }
  };
}

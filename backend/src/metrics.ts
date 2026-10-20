import { readFile } from 'node:fs/promises';
import { ApiError, type Step, type Comparison, type Repository } from './types.js';
import { parseTimestamp } from './validation.js';

export type { Comparison } from './types.js';

export async function storedComparison(repository: Repository, path: string, simulation: string): Promise<Comparison> {
  let value: Comparison;
  try { value = await readComparison(path, simulation); }
  catch (error) {
    const saved = await repository.forSimulation(simulation).comparison();
    if (saved) return saved;
    throw error;
  }
  await repository.transaction(simulation, session => session.setComparison(value));
  return value;
}

export async function readComparison(path: string, simulation: string): Promise<Comparison> {
  let comparison: Comparison;
  try { comparison = JSON.parse(await readFile(path, 'utf8')); }
  catch { throw new ApiError(503, 'Comparativo ainda não disponível.'); }
  try {
    if (comparison.simulation_id !== simulation || !comparison.period
      || parseTimestamp(comparison.period.from) >= parseTimestamp(comparison.period.to)
      || ![comparison.baseline, comparison.optimized].every(item => item && Number.isFinite(item.cost)
        && Number.isFinite(item.import_kwh) && item.import_kwh >= 0)) throw new Error();
  } catch { throw new ApiError(503, 'Comparativo inválido ou de outra simulação.'); }
  return comparison;
}

export async function loadTariff(path: string): Promise<Record<string, number>> {
  const [header, ...lines] = (await readFile(path, 'utf8')).trim().split(/\r?\n/).map(line => line.split(';'));
  const prices: Record<string, number> = {};
  for (const fields of lines) {
    const row = Object.fromEntries(header.map((key, index) => [key, fields[index]]));
    if (row.DscDetalhe === 'Não se aplica') prices[row.NomPostoTarifario] = Number(row['TUSD_mais_TE_R$_por_kWh']);
  }
  if (!['Fora ponta', 'Intermediário', 'Ponta'].every(key => Number.isFinite(prices[key]) && prices[key] >= 0))
    throw new Error('Arquivo de tarifa incompleto.');
  return prices;
}

export function localDay(time: number): { date: string; from: number; to: number } {
  const date = new Date(time - 3 * 3600_000).toISOString().slice(0, 10);
  const from = Date.parse(`${date}T00:00:00-03:00`);
  return { date, from, to: from + 86400_000 };
}

export function tariffAt(time: number, prices: Record<string, number>): number {
  const moment = new Date(time - 3 * 3600_000);
  const holiday = ['01-01', '04-21', '05-01', '09-07', '10-12', '11-02', '11-15', '11-20', '12-25']
    .includes(moment.toISOString().slice(5, 10));
  const minutes = moment.getUTCHours() * 60 + moment.getUTCMinutes();
  const period = moment.getUTCDay() % 6 === 0 || holiday ? 'Fora ponta'
    : minutes >= 1050 && minutes < 1230 ? 'Ponta'
    : (minutes >= 990 && minutes < 1050) || (minutes >= 1230 && minutes < 1290) ? 'Intermediário' : 'Fora ponta';
  return prices[period];
}

export function summarize(steps: Step[], prices: Record<string, number>, exportValue: number | null,
                          emissionFactor: number | null) {
  let imported = 0, exported = 0, importCost = 0, marketGain = 0;
  for (const step of steps) {
    const price = tariffAt(step.time, prices);
    for (const reading of step.readings) {
      const quantity = reading.grid_power_kw * 0.25;
      imported += Math.max(quantity, 0);
      exported += Math.max(-quantity, 0);
      importCost += Math.max(quantity, 0) * price;
    }
    if (exportValue !== null) {
      // Mesmo acerto financeiro usado por HouseMetrics.record_trade.
      for (const trade of step.result.trades) marketGain += trade.quantity_kwh * (price - exportValue);
    }
  }
  return { import_kwh: imported, export_kwh: exported, import_cost: importCost,
    cost: exportValue === null ? null : importCost - exported * exportValue - marketGain,
    market_gain: exportValue === null ? null : marketGain,
    emissions_kg: emissionFactor === null ? null : imported * emissionFactor };
}

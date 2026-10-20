import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtemp, writeFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { loadTariff, localDay, readComparison, storedComparison, summarize, tariffAt } from '../src/metrics.js';
import { configuration } from '../src/config.js';
import { neutralDecide } from '../src/engine.js';
import { MemoryRepository, readings, fixture } from './support.js';

const prices = { 'Fora ponta': 0.6692, 'Intermediário': 0.9845, 'Ponta': 1.4803 };
test('tarifa oficial: fronteiras dos postos, feriado e fim de semana', async () => {
  assert.deepEqual(await loadTariff('../dados/processados/tarifa_enel_sp_branca.csv'), prices);
  for (const [time, price] of [['16:29', 0.6692], ['16:30', 0.9845], ['17:30', 1.4803],
    ['20:30', 0.9845], ['21:30', 0.6692]] as const)
    assert.equal(tariffAt(Date.parse(`2026-10-20T${time}:00-03:00`), prices), price);
  for (const day of ['2026-10-12', '2026-10-18'])
    assert.equal(tariffAt(Date.parse(`${day}T18:00:00-03:00`), prices), 0.6692);
  assert.equal(localDay(Date.parse('2026-10-21T02:45:00Z')).date, '2026-10-20');
});

test('acerto financeiro mantém energia física e desconta ganho uma vez', async () => {
  const batch = readings();
  batch[0].grid_power_kw = 4;
  batch[2].grid_power_kw = -2;
  const result = await neutralDecide(batch, {});
  result.trades.push({ seller_id: 'casa-03', buyer_id: 'casa-01', quantity_kwh: 0.5, price_per_kwh: 0.3 });
  const steps = [{ time: Date.parse(batch[0].timestamp), hash: 'test', readings: batch, result }];
  const totals = summarize(steps, prices, 0.1, 0.03);
  assert.equal(totals.import_kwh, 1);
  assert.equal(totals.export_kwh, 0.5);
  assert.ok(Math.abs(totals.cost! - (0.6692 - 0.05 - 0.5 * (0.6692 - 0.1))) < 1e-9);
  assert.equal(totals.emissions_kg, 0.03);
  assert.equal(summarize(steps, prices, null, null).cost, null);
});

test('resumo só usa economia do mesmo dia simulado', async t => {
  const comparison = { simulation_id: 'default',
    period: { from: '2026-10-20T00:00:00-03:00', to: '2026-10-21T00:00:00-03:00' },
    baseline: { cost: 20, import_kwh: 30 }, optimized: { cost: 15, import_kwh: 20 } };
  const { app } = fixture({ comparison: async () => comparison, emissionFactor: 0.03 });
  t.after(() => app.close());
  await app.inject({ method: 'POST', url: '/readings', payload: readings() });
  let summary = (await app.inject('/summary/today')).json();
  assert.equal(summary.savings, 5);
  assert.equal(summary.co2_avoided_kg, 0.3);
  comparison.period.to = '2026-10-22T00:00:00-03:00';
  summary = (await app.inject('/summary/today')).json();
  assert.equal(summary.savings, null);
  assert.equal(summary.co2_avoided_kg, null);
});

test('comparativo ausente, nulo, sem fuso ou de outra simulação é indisponível', async t => {
  const directory = await mkdtemp(join(tmpdir(), 'hems-comparison-'));
  t.after(() => rm(directory, { recursive: true }));
  const path = join(directory, 'comparison.json');
  await assert.rejects(readComparison(path, 'default'), { statusCode: 503 });
  const valid = { simulation_id: 'default',
    period: { from: '2026-10-20T00:00:00-03:00', to: '2026-10-21T00:00:00-03:00' },
    baseline: { cost: 20, import_kwh: 30 }, optimized: { cost: 15, import_kwh: 20 } };
  for (const value of [null, {}, { ...valid, simulation_id: 'outra' },
    { ...valid, period: { from: '2026-10-20', to: '2026-10-21' } }]) {
    await writeFile(path, JSON.stringify(value));
    await assert.rejects(readComparison(path, 'default'), { statusCode: 503 });
  }
  await writeFile(path, JSON.stringify(valid));
  assert.deepEqual(await readComparison(path, 'default'), valid);
  const repository = new MemoryRepository();
  assert.deepEqual(await storedComparison(repository, path, 'default'), valid);
  await rm(path);
  assert.deepEqual(await storedComparison(repository, path, 'default'), valid);
  await assert.rejects(storedComparison(repository, path, 'outra'), { statusCode: 503 });
});

test('configuração exige premissas apenas quando usadas', () => {
  const env = { MYSQL_PASSWORD: 'test' };
  assert.equal(configuration(env).exportValue, null);
  assert.throws(() => configuration({ ...env, ENGINE_MODE: 'http' }), /EXPORT_VALUE/);
  assert.equal(configuration({ ...env, ENGINE_MODE: 'http', EXPORT_VALUE_PER_KWH: '0' }).exportValue, 0);
  assert.throws(() => configuration({ ...env, GRID_EMISSION_FACTOR_KG_PER_KWH: '-1' }), /GRID_EMISSION/);
});

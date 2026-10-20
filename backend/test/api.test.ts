import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fixture, readings } from './support.js';
import { neutralDecide } from '../src/engine.js';
import { ApiError } from '../src/types.js';

test('recebe leituras, devolve comandos neutros e consulta todas as rotas', async t => {
  const { app } = fixture(); t.after(() => app.close());
  assert.equal((await app.inject('/health')).statusCode, 200);
  const response = await app.inject({ method: 'POST', url: '/readings', payload: readings() });
  assert.equal(response.statusCode, 200);
  assert.equal(response.json().length, 3);
  assert.equal(response.json()[0].ev_charge_power_kw, 0);
  assert.match(response.json()[0].reason, /neutro/);
  for (const route of ['/houses/casa-01/state', '/houses/casa-01/history', '/houses/casa-01/decision',
    '/market/offers', '/market/orders', '/market/trades', '/summary/today']) {
    assert.equal((await app.inject(route)).statusCode, 200, route);
  }
  assert.equal((await app.inject('/comparison')).statusCode, 503);
  const summary = (await app.inject('/summary/today')).json();
  assert.equal(summary.date, '2026-10-20');
  for (const key of ['savings', 'cost', 'emissions_kg', 'co2_avoided_kg']) assert.equal(summary[key], null);
});

test('reenvio concorrente não repete o motor nem duplica leituras', async t => {
  let calls = 0;
  const { app, repository } = fixture({ decide: async batch => { calls++; return neutralDecide(batch, {}); } });
  t.after(() => app.close());
  const request = { method: 'POST' as const, url: '/readings', payload: readings() };
  const responses = await Promise.all([app.inject(request), app.inject(request), app.inject(request)]);
  assert.ok(responses.every(response => response.statusCode === 200));
  assert.deepEqual(responses[0].json(), responses[1].json());
  assert.equal(calls, 1);
  assert.equal(repository.data.get('default')!.steps.size, 1);
  assert.equal((await app.inject('/houses/casa-01/history')).json().length, 1);
});

test('conflito, salto de tempo e lote incompleto são rejeitados', async t => {
  const { app } = fixture(); t.after(() => app.close());
  await app.inject({ method: 'POST', url: '/readings', payload: readings() });
  const changed = readings(); changed[0].load_power_kw = 2;
  for (const payload of [changed, readings('2026-10-20T10:30:00-03:00'), readings('2026-10-20T09:45:00-03:00'),
    readings('2026-10-20T10:15:00-03:00').slice(0, 2)]) {
    assert.equal((await app.inject({ method: 'POST', url: '/readings', payload })).statusCode, 409);
  }
  assert.equal((await app.inject({ method: 'POST', url: '/readings', payload: readings('2026-10-20T10:15:00-03:00') })).statusCode, 200);
});

test('valida schema, casas duplicadas, horários e EV sem veículo', async t => {
  const { app } = fixture(); t.after(() => app.close());
  const invalid: unknown[] = [[], {}, [readings()[0], readings()[0]], readings('2026-02-30T10:00:00-03:00'), readings('2026-10-20T10:00:00')];
  const negative = readings(); negative[0].pv_power_kw = -1; invalid.push(negative);
  const strings = readings() as any; strings[0].ev.soc_percent = '35'; invalid.push(strings);
  const missing = readings() as any; delete missing[0].battery; invalid.push(missing);
  const unknown = readings() as any; unknown[0].extra = 1; invalid.push(unknown);
  const mixed = readings(); mixed[1].timestamp = '2026-10-20T10:15:00-03:00'; invalid.push(mixed);
  const noEv = readings(); noEv[2].ev.connected = true; invalid.push(noEv);
  for (const payload of invalid) assert.equal((await app.inject({ method: 'POST', url: '/readings', payload: payload as any })).statusCode, 400);
});

test('meta persiste e chega ao motor no próximo passo', async t => {
  const targets: unknown[] = [];
  const { app } = fixture({ decide: async (batch, settings) => { targets.push(settings); return neutralDecide(batch, settings); } });
  t.after(() => app.close());
  await app.inject({ method: 'POST', url: '/readings', payload: readings() });
  const payload = { target_soc_percent: 90, departure_time: '07:30' };
  assert.equal((await app.inject({ method: 'PUT', url: '/houses/casa-01/ev', payload })).statusCode, 200);
  assert.equal((await app.inject({ method: 'PUT', url: '/houses/casa-03/ev', payload })).statusCode, 409);
  assert.equal((await app.inject({ method: 'PUT', url: '/houses/unknown/ev', payload })).statusCode, 404);
  assert.equal((await app.inject({ method: 'PUT', url: '/houses/casa-01/ev', payload: { ...payload, target_soc_percent: 101 } })).statusCode, 400);
  assert.equal((await app.inject({ method: 'PUT', url: '/houses/casa-01/ev', payload: { ...payload, departure_time: '24:00' } })).statusCode, 400);
  await app.inject({ method: 'POST', url: '/readings', payload: readings('2026-10-20T10:15:00-03:00') });
  assert.deepEqual(targets[1], { 'casa-01': payload });
});

test('simulações não misturam estado, metas ou passos', async t => {
  const { app } = fixture(); t.after(() => app.close());
  assert.equal((await app.inject({ method: 'POST', url: '/readings', headers: { 'x-simulation-id': 'baseline' }, payload: readings() })).statusCode, 200);
  assert.equal((await app.inject('/houses/casa-01/state')).statusCode, 404);
  assert.equal((await app.inject({ method: 'POST', url: '/readings', headers: { 'x-simulation-id': 'optimized' }, payload: readings() })).statusCode, 200);
  assert.equal((await app.inject({ method: 'POST', url: '/readings', headers: { 'x-simulation-id': '../invalid' }, payload: readings() })).statusCode, 400);
});

test('Redis indisponível não perde passo nem retorna estado velho', async t => {
  const { app, cache } = fixture(); t.after(() => app.close());
  await app.inject({ method: 'POST', url: '/readings', payload: readings() });
  cache.fail = true;
  const payload = readings('2026-10-20T10:15:00-03:00'); payload[0].pv_power_kw = 5;
  assert.equal((await app.inject({ method: 'POST', url: '/readings', payload })).statusCode, 200);
  assert.equal((await app.inject('/houses/casa-01/state')).json().pv_power_kw, 5);
  assert.equal((await app.inject('/health')).statusCode, 503);
  cache.fail = false;
  assert.equal((await app.inject('/houses/casa-01/state')).json().pv_power_kw, 5);
});

test('falha do motor desfaz a transação e permite nova tentativa', async t => {
  let failed = true;
  const { app, repository } = fixture({ decide: async batch => {
    if (failed) throw new ApiError(502, 'Motor indisponível');
    return neutralDecide(batch, {});
  } });
  t.after(() => app.close());
  const request = { method: 'POST' as const, url: '/readings', payload: readings() };
  assert.equal((await app.inject(request)).statusCode, 502);
  assert.equal(repository.data.get('default')!.steps.size, 0);
  failed = false;
  assert.equal((await app.inject(request)).statusCode, 200);
});

test('histórico filtra intervalo e valida limites', async t => {
  const { app } = fixture(); t.after(() => app.close());
  for (const timestamp of ['2026-10-20T10:00:00-03:00', '2026-10-20T10:15:00-03:00'])
    await app.inject({ method: 'POST', url: '/readings', payload: readings(timestamp) });
  const from = encodeURIComponent('2026-10-20T10:15:00-03:00');
  assert.equal((await app.inject(`/houses/casa-01/history?from=${from}`)).json().length, 1);
  for (const suffix of ['?limit=0', '?limit=1001', '?from=bad', '?oops=1'])
    assert.equal((await app.inject(`/houses/casa-01/history${suffix}`)).statusCode, 400);
});
test('ordem do lote e capitalização dos IDs não alteram o conjunto de casas', async t => {
  const { app } = fixture();
  t.after(() => app.close());
  const batch = readings();
  batch[0].house_id = 'A';
  batch[1].house_id = 'a';
  assert.equal((await app.inject({ method: 'POST', url: '/readings', payload: batch })).statusCode, 200);
  batch.reverse();
  assert.equal((await app.inject({ method: 'POST', url: '/readings', payload: batch })).statusCode, 200);
  for (const reading of batch) reading.timestamp = '2026-10-20T10:15:00-03:00';
  assert.equal((await app.inject({ method: 'POST', url: '/readings', payload: batch })).statusCode, 200);
});

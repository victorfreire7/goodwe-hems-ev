import test from 'node:test';
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { httpDecide, neutralDecide } from '../src/engine.js';
import { validateEngineResult } from '../src/validation.js';
import { readings } from './support.js';

test('cliente HTTP envia metas, premissas e recebe comandos e negociações', async t => {
  const batch = readings();
  const result = await neutralDecide(batch, {});
  result.trades = [{ seller_id: 'casa-03', buyer_id: 'casa-01', quantity_kwh: 0.2, price_per_kwh: 0.3 }];
  result.commands[0].market.bought_kwh = 0.2;
  result.commands[2].market.sold_kwh = 0.2;
  let received: any;
  const server = createServer(async (req, res) => {
    assert.equal(req.url, '/decide');
    assert.equal(req.method, 'POST');
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    received = JSON.parse(Buffer.concat(chunks).toString());
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify(result));
  });
  await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => { server.closeAllConnections(); server.close(); });
  const address = server.address() as { port: number };
  const decide = httpDecide(`http://127.0.0.1:${address.port}`, 1000, 0, true);
  const targets = { 'casa-01': { target_soc_percent: 90, departure_time: '08:00' } };
  assert.deepEqual(await decide(batch, targets), result);
  assert.equal(received.readings[0].ev.target_soc_percent, 90);
  assert.deepEqual(received.ev_targets, targets);
  assert.equal(received.export_value_per_kwh, 0);
  assert.equal(received.optimized, true);
  assert.equal(batch[0].ev.target_soc_percent, 80);
});

test('motor com erro, JSON inválido ou timeout produz 502', async t => {
  let mode = 'error';
  const server = createServer((_req, res) => {
    if (mode === 'timeout') return;
    res.statusCode = mode === 'error' ? 500 : 200;
    res.end(mode === 'json' ? '{' : '{}');
  });
  await new Promise<void>(resolve => server.listen(0, '127.0.0.1', resolve));
  t.after(() => { server.closeAllConnections(); server.close(); });
  const address = server.address() as { port: number };
  const decide = httpDecide(`http://127.0.0.1:${address.port}`, 100, 0, true);
  for (mode of ['error', 'json', 'schema', 'timeout'])
    await assert.rejects(decide(readings(), {}), { statusCode: 502 });
});

test('rejeita comandos duplicados, casa desconhecida e acerto inconsistente', async () => {
  const batch = readings(), valid = await neutralDecide(batch, {});
  for (const mutate of [
    (value: typeof valid) => { value.commands[1] = value.commands[0]; },
    (value: typeof valid) => { value.commands[0].house_id = 'outra'; },
    (value: typeof valid) => { value.commands[0].timestamp = '2026-10-20T10:15:00-03:00'; },
    (value: typeof valid) => { value.commands[0].market.bought_kwh = 1; },
    (value: typeof valid) => { value.orders.push({ house_id: 'outra', quantity_kwh: 1, grid_price_per_kwh: 1 }); },
  ]) {
    const value = structuredClone(valid);
    mutate(value);
    assert.throws(() => validateEngineResult(value, batch), { statusCode: 502 });
  }
});

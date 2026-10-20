import test from 'node:test';
import assert from 'node:assert/strict';
import { randomUUID } from 'node:crypto';
import { createPool } from 'mysql2/promise';
import { createClient } from 'redis';
import { MySqlRepository, RedisStateCache } from '../../src/storage.js';
import { neutralDecide } from '../../src/engine.js';
import { fixture, readings } from '../support.js';

test('MySQL e Redis: concorrência, rollback, histórico, metas e recuperação após reinício', async () => {
  const id = `test-${randomUUID()}`;
  const headers = { 'x-simulation-id': id };
  let calls = 0;
  const open = async () => {
    const pool = createPool({ host: process.env.MYSQL_HOST ?? '127.0.0.1',
      port: Number(process.env.MYSQL_PORT ?? 3306), user: process.env.MYSQL_USER ?? 'hems',
      password: process.env.MYSQL_PASSWORD, database: process.env.MYSQL_DATABASE ?? 'hems', connectionLimit: 5 });
    const repository = new MySqlRepository(pool);
    const redis = createClient({ socket: { host: process.env.REDIS_HOST ?? '127.0.0.1',
      port: Number(process.env.REDIS_PORT ?? 6379), reconnectStrategy: false } });
    redis.on('error', () => {});
    await repository.initialize();
    await redis.connect();
    const cache = new RedisStateCache(redis);
    const { app } = fixture({ repository, cache, decide: async (batch, targets) => {
      calls++;
      const result = await neutralDecide(batch, targets);
      result.commands[0].market.bought_kwh = 0.2;
      result.commands[2].market.sold_kwh = 0.2;
      result.trades = [{ seller_id: 'casa-03', buyer_id: 'casa-01', quantity_kwh: 0.2, price_per_kwh: 0.3 }];
      return result;
    } });
    return { pool, repository, redis, cache, app };
  };
  let current = await open();
  try {
    const first = readings();
    const responses = await Promise.all(Array.from({ length: 10 }, () => current.app.inject({
      method: 'POST', url: '/readings', headers, payload: first })));
    for (const response of responses) assert.equal(response.statusCode, 200, response.body);
    assert.equal(calls, 1);
    const initial = (await current.repository.forSimulation(id).latest())!;
    const comparison = { simulation_id: id,
      period: { from: '2026-10-20T00:00:00-03:00', to: '2026-10-21T00:00:00-03:00' },
      baseline: { cost: 20, import_kwh: 30 }, optimized: { cost: 15, import_kwh: 20 } };
    await current.repository.transaction(id, session => session.setComparison(comparison));
    assert.equal((await current.app.inject({ method: 'PUT', url: '/houses/casa-01/ev', headers,
      payload: { target_soc_percent: 90, departure_time: '08:00' } })).statusCode, 200);
    assert.equal((await current.app.inject({ method: 'POST', url: '/readings', headers,
      payload: readings('2026-10-20T10:15:00-03:00') })).statusCode, 200);
    await current.cache.put(id, initial);
    assert.equal((await current.cache.get(id, 'casa-01'))!.timestamp, '2026-10-20T10:15:00-03:00');
    // A escrita de leituras e negociações também deve ser desfeita.
    const failed = structuredClone(initial);
    failed.time += 30 * 60_000;
    failed.readings = readings('2026-10-20T10:30:00-03:00');
    await assert.rejects(current.repository.transaction(id, async session => {
      await session.save(failed);
      await session.setTarget('casa-01', { target_soc_percent: 50, departure_time: '12:00' });
      throw new Error('falha após escrita');
    }), /falha após escrita/);
    assert.equal(await current.repository.forSimulation(id).step(failed.time), null);
    assert.equal((await current.repository.forSimulation(id).targets())['casa-01'].target_soc_percent, 90);
    assert.equal((await current.repository.history(id, 'casa-01', initial.time, failed.time, 100)).length, 2);
    const [rows] = await current.pool.query<any[]>('SELECT COUNT(*) AS n FROM trades WHERE simulation_id = ?', [id]);
    assert.equal(rows[0].n, 2);
    for (const reading of first) await current.redis.del(`hems:${id}:house:${reading.house_id}:state`);
    await current.app.close();
    current = await open();
    assert.deepEqual(await current.repository.forSimulation(id).comparison(), comparison);
    const state = await current.app.inject({ url: '/houses/casa-01/state', headers });
    assert.equal(state.statusCode, 200, state.body);
    assert.equal(state.json().timestamp, '2026-10-20T10:15:00-03:00');
    assert.equal((await current.cache.get(id, 'casa-01'))!.timestamp, state.json().timestamp);
    assert.equal((await current.repository.forSimulation(id).targets())['casa-01'].target_soc_percent, 90);
    const retry = await current.app.inject({ method: 'POST', url: '/readings', headers, payload: first });
    assert.equal(retry.statusCode, 200, retry.body);
    assert.equal(calls, 2);
    assert.equal((await current.app.inject({ url: '/market/trades', headers })).json().length, 2);
    assert.equal((await current.app.inject('/health')).statusCode, 200);
  } finally {
    for (const table of ['trades', 'readings', 'ev_targets', 'comparisons', 'steps', 'simulations'])
      await current.pool.execute(`DELETE FROM ${table} WHERE simulation_id = ?`, [id]);
    for (const reading of readings()) await current.redis.del(`hems:${id}:house:${reading.house_id}:state`);
    await current.app.close();
  }
});

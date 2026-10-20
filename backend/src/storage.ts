import { readFile } from 'node:fs/promises';
import type { Pool, PoolConnection, RowDataPacket } from 'mysql2/promise';
import type { Comparison, EvTarget, Reading, Repository, Session, StateCache, Step } from './types.js';

const decode = <T>(value: string | T): T => typeof value === 'string' ? JSON.parse(value) : value;
type Sql = Pool | PoolConnection;

class SqlSession implements Session {
  constructor(private sql: Sql, private simulation: string) {}
  async comparison(): Promise<Comparison | null> {
    const [rows] = await this.sql.execute<RowDataPacket[]>(
      'SELECT payload FROM comparisons WHERE simulation_id = ?', [this.simulation]);
    return rows.length ? decode(rows[0].payload) : null;
  }
  async setComparison(value: Comparison): Promise<void> {
    await this.sql.execute(
      'INSERT INTO comparisons (simulation_id, payload) VALUES (?, ?) ON DUPLICATE KEY UPDATE payload = ?',
      [this.simulation, JSON.stringify(value), JSON.stringify(value)]);
  }
  async step(time: number): Promise<Step | null> {
    const [rows] = await this.sql.execute<RowDataPacket[]>(
      'SELECT payload FROM steps WHERE simulation_id = ? AND time_ms = ?', [this.simulation, time]);
    return rows.length ? decode(rows[0].payload) : null;
  }
  async latest(): Promise<Step | null> {
    const [rows] = await this.sql.execute<RowDataPacket[]>(
      'SELECT payload FROM steps WHERE simulation_id = ? ORDER BY time_ms DESC LIMIT 1', [this.simulation]);
    return rows.length ? decode(rows[0].payload) : null;
  }
  async targets(): Promise<Record<string, EvTarget>> {
    const [rows] = await this.sql.execute<RowDataPacket[]>(
      'SELECT house_id, payload FROM ev_targets WHERE simulation_id = ?', [this.simulation]);
    return Object.fromEntries(rows.map(row => [row.house_id, decode<EvTarget>(row.payload)]));
  }
  async setTarget(house: string, target: EvTarget): Promise<void> {
    await this.sql.execute(
      'INSERT INTO ev_targets (simulation_id, house_id, payload) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE payload = ?',
      [this.simulation, house, JSON.stringify(target), JSON.stringify(target)]);
  }
  async save(step: Step): Promise<void> {
    await this.sql.execute('INSERT INTO steps (simulation_id, time_ms, request_hash, payload) VALUES (?, ?, ?, ?)',
      [this.simulation, step.time, step.hash, JSON.stringify(step)]);
    for (const reading of step.readings) {
      await this.sql.execute('INSERT INTO readings (simulation_id, house_id, time_ms, payload) VALUES (?, ?, ?, ?)',
        [this.simulation, reading.house_id, step.time, JSON.stringify(reading)]);
    }
    for (const [index, trade] of step.result.trades.entries()) {
      await this.sql.execute('INSERT INTO trades (simulation_id, time_ms, trade_index, payload) VALUES (?, ?, ?, ?)',
        [this.simulation, step.time, index, JSON.stringify(trade)]);
    }
  }
}

export class MySqlRepository implements Repository {
  constructor(private pool: Pool) {}
  async initialize(): Promise<void> {
    const source = await readFile(new URL('../schema.sql', import.meta.url), 'utf8');
    for (const statement of source.split(';').filter(part => part.trim())) await this.pool.query(statement);
  }
  forSimulation(simulation: string): Session { return new SqlSession(this.pool, simulation); }
  async transaction<T>(simulation: string, work: (session: Session) => Promise<T>): Promise<T> {
    const connection = await this.pool.getConnection();
    try {
      await connection.beginTransaction();
      // Serializa leituras e alterações de meta da mesma simulação.
      await connection.execute(
        'INSERT INTO simulations (simulation_id) VALUES (?) ON DUPLICATE KEY UPDATE simulation_id = ?',
        [simulation, simulation]);
      const result = await work(new SqlSession(connection, simulation));
      await connection.commit();
      return result;
    } catch (error) {
      await connection.rollback();
      throw error;
    } finally { connection.release(); }
  }
  async history(simulation: string, house: string, from: number, to: number, limit: number): Promise<Reading[]> {
    const [rows] = await this.pool.query<RowDataPacket[]>(
      'SELECT payload FROM readings WHERE simulation_id = ? AND house_id = ? AND time_ms >= ? AND time_ms <= ? ORDER BY time_ms LIMIT ?',
      [simulation, house, from, to, limit]);
    return rows.map(row => decode<Reading>(row.payload));
  }
  async steps(simulation: string, from: number, to: number): Promise<Step[]> {
    const [rows] = await this.pool.execute<RowDataPacket[]>(
      'SELECT payload FROM steps WHERE simulation_id = ? AND time_ms >= ? AND time_ms < ? ORDER BY time_ms',
      [simulation, from, to]);
    return rows.map(row => decode<Step>(row.payload));
  }
  async health(): Promise<void> { await this.pool.query('SELECT 1'); }
  async close(): Promise<void> { await this.pool.end(); }
}

const updateState = `
local old = redis.call('HGET', KEYS[1], 'time')
if not old or tonumber(old) <= tonumber(ARGV[1]) then
  redis.call('HSET', KEYS[1], 'time', ARGV[1], 'reading', ARGV[2])
end
return 1`;

export class RedisStateCache implements StateCache {
  constructor(private client: {
    hGet(key: string, field: string): Promise<string | null | undefined>;
    eval(script: string, options: { keys: string[]; arguments: string[] }): Promise<unknown>;
    ping(): Promise<unknown>;
    quit(): Promise<unknown>;
    isOpen: boolean;
  }) {}
  private key(simulation: string, house: string): string { return `hems:${simulation}:house:${house}:state`; }
  async get(simulation: string, house: string): Promise<Reading | null> {
    const value = await this.client.hGet(this.key(simulation, house), 'reading');
    return value ? JSON.parse(value) : null;
  }
  async put(simulation: string, step: Step): Promise<void> {
    await Promise.all(step.readings.map(reading => this.client.eval(updateState, {
      keys: [this.key(simulation, reading.house_id)],
      arguments: [String(step.time), JSON.stringify(reading)],
    })));
  }
  async health(): Promise<void> { await this.client.ping(); }
  async close(): Promise<void> { if (this.client.isOpen) await this.client.quit(); }
}

import type { Comparison, EvTarget, Reading, Repository, Session, StateCache, Step } from '../src/types.js';
import { buildApp } from '../src/app.js';
import { neutralDecide } from '../src/engine.js';
import { ApiError } from '../src/types.js';

export class MemoryRepository implements Repository {
  data = new Map<string, { steps: Map<number, Step>; targets: Record<string, EvTarget>; comparison?: Comparison }>();
  private queue = Promise.resolve();
  private dataFor(id: string) {
    if (!this.data.has(id)) this.data.set(id, { steps: new Map(), targets: {} });
    return this.data.get(id)!;
  }
  forSimulation(id: string): Session {
    return {
      comparison: async () => this.dataFor(id).comparison ?? null,
      setComparison: async value => { this.dataFor(id).comparison = structuredClone(value); },
      step: async time => this.dataFor(id).steps.get(time) ?? null,
      latest: async () => [...this.dataFor(id).steps.values()].sort((a, b) => b.time - a.time)[0] ?? null,
      targets: async () => structuredClone(this.dataFor(id).targets),
      setTarget: async (house, target) => { this.dataFor(id).targets[house] = structuredClone(target); },
      save: async step => { this.dataFor(id).steps.set(step.time, structuredClone(step)); },
    };
  }
  async transaction<T>(id: string, work: (session: Session) => Promise<T>): Promise<T> {
    const previous = this.queue;
    let release!: () => void;
    this.queue = new Promise(resolve => { release = resolve; });
    await previous;
    const before = structuredClone(this.dataFor(id));
    try { return await work(this.forSimulation(id)); }
    catch (error) { this.data.set(id, before); throw error; }
    finally { release(); }
  }
  async history(id: string, house: string, from: number, to: number, limit: number): Promise<Reading[]> {
    return (await this.steps(id, from, to + 1)).flatMap(step => step.readings)
      .filter(reading => reading.house_id === house).slice(0, limit);
  }
  async steps(id: string, from: number, to: number): Promise<Step[]> {
    return [...this.dataFor(id).steps.values()].filter(step => step.time >= from && step.time < to).sort((a, b) => a.time - b.time);
  }
  async health() {}
  async close() {}
}

export class MemoryCache implements StateCache {
  data = new Map<string, Reading>();
  fail = false;
  async get(id: string, house: string) {
    if (this.fail) throw new Error('Redis indisponível');
    return this.data.get(`${id}:${house}`) ?? null;
  }
  async put(id: string, step: Step) {
    if (this.fail) throw new Error('Redis indisponível');
    for (const reading of step.readings) this.data.set(`${id}:${reading.house_id}`, structuredClone(reading));
  }
  async health() { if (this.fail) throw new Error('Redis indisponível'); }
  async close() {}
}

export function readings(timestamp = '2026-10-20T10:00:00-03:00'): Reading[] {
  return ['casa-01', 'casa-02', 'casa-03'].map((house_id, index) => ({
    house_id, timestamp, pv_power_kw: 4.2, load_power_kw: 0.9,
    battery: { soc_percent: 62, power_kw: -1.5 },
    ev: { connected: index !== 2, soc_percent: index === 2 ? 0 : 35,
      capacity_kwh: index === 2 ? 0 : 60, target_soc_percent: index === 2 ? 0 : 80,
      departure_time: index === 2 ? null : '17:00', charge_power_kw: index === 2 ? 0 : 1.8 },
    grid_power_kw: index === 2 ? -1.8 : 0,
  }));
}

export function fixture(overrides: Partial<Parameters<typeof buildApp>[0]> = {}) {
  const repository = new MemoryRepository(), cache = new MemoryCache();
  const app = buildApp({ repository, cache, decide: neutralDecide, engineMode: 'neutral',
    prices: { 'Fora ponta': 0.6692, 'Intermediário': 0.9845, 'Ponta': 1.4803 },
    exportValue: null, emissionFactor: null,
    comparison: async () => { throw new ApiError(503, 'Comparativo pendente'); }, ...overrides });
  return { app, repository, cache };
}

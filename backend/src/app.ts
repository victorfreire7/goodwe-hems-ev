import Fastify from 'fastify';
import { createHash } from 'node:crypto';
import { ApiError, type Decide, type EvTarget, type Reading, type Repository, type StateCache, type Step } from './types.js';
import { readingsSchema, targetSchema, validateBatch, validateEngineResult, parseTimestamp } from './validation.js';
import { localDay, summarize, type Comparison } from './metrics.js';

interface Options {
  repository: Repository;
  cache: StateCache;
  decide: Decide;
  engineMode: string;
  prices: Record<string, number>;
  exportValue: number | null;
  emissionFactor: number | null;
  comparison: (simulation: string) => Promise<Comparison>;
  logger?: boolean;
}

const canonical = (value: unknown): string => {
  if (Array.isArray(value)) return `[${value.map(canonical).join(',')}]`;
  if (value && typeof value === 'object') return `{${Object.entries(value).sort(([a], [b]) => a.localeCompare(b))
    .map(([key, item]) => `${JSON.stringify(key)}:${canonical(item)}`).join(',')}}`;
  return JSON.stringify(value);
};

export function buildApp(options: Options) {
  const { repository, cache } = options;
  const app = Fastify({ logger: options.logger ?? false, bodyLimit: 256 * 1024,
    ajv: { customOptions: { coerceTypes: false, removeAdditional: false } } });
  const simulation = (headers: Record<string, unknown>): string => {
    const id = headers['x-simulation-id'] ?? 'default';
    if (typeof id !== 'string' || !/^[A-Za-z0-9_-]{1,64}$/.test(id)) throw new ApiError(400, 'X-Simulation-Id inválido.');
    return id;
  };
  const latest = async (id: string): Promise<Step> => {
    const step = await repository.forSimulation(id).latest();
    if (!step) throw new ApiError(404, 'Simulação sem leituras.');
    return step;
  };
  const houseReading = (step: Step, house: string): Reading => {
    const reading = step.readings.find(item => item.house_id === house);
    if (!reading) throw new ApiError(404, 'Casa não encontrada.');
    return reading;
  };
  const range = (query: Record<string, string>, time: number) => {
    if (Object.keys(query).some(key => !['from', 'to', 'limit'].includes(key))) throw new ApiError(400, 'Parâmetro de consulta desconhecido.');
    const from = query.from ? parseTimestamp(query.from) : time - 86400_000;
    const to = query.to ? parseTimestamp(query.to) : time;
    const limit = query.limit === undefined ? 1000 : Number(query.limit);
    if (from > to || to - from > 31 * 86400_000 || !Number.isInteger(limit) || limit < 1 || limit > 1000)
      throw new ApiError(400, 'Intervalo máximo de 31 dias e limit entre 1 e 1000.');
    return { from, to, limit };
  };

  app.setErrorHandler<Error & { statusCode?: number }>((error, request, reply) => {
    const status = error.statusCode && error.statusCode >= 400 && error.statusCode < 600 ? error.statusCode : 503;
    if (status >= 500) request.log.error(error);
    reply.code(status).send({ error: status === 503 ? 'Serviço indisponível.' : error.message });
  });

  app.get('/health', async () => {
    await Promise.all([repository.health(), cache.health()]);
    return { status: 'ok', engine_mode: options.engineMode };
  });

  app.post<{ Body: Reading[] }>('/readings', { schema: { body: readingsSchema } }, async request => {
    const id = simulation(request.headers);
    const time = validateBatch(request.body);
    const readings = [...request.body].sort((a, b) => a.house_id.localeCompare(b.house_id));
    const hash = createHash('sha256').update(canonical(readings)).digest('hex');
    const step = await repository.transaction(id, async session => {
      const previous = await session.step(time);
      if (previous) {
        if (previous.hash !== hash) throw new ApiError(409, 'Passo já recebido com outras leituras.');
        return previous;
      }
      const last = await session.latest();
      if (last && time !== last.time + 15 * 60_000) throw new ApiError(409, 'Esperado o próximo passo de 15 minutos.');
      if (last && canonical(last.readings.map(item => item.house_id).sort()) !== canonical(readings.map(item => item.house_id).sort()))
        throw new ApiError(409, 'Todas as casas da simulação devem estar presentes.');
      const result = validateEngineResult(await options.decide(readings, await session.targets()), readings);
      const saved = { time, hash, readings, result };
      await session.save(saved);
      return saved;
    });
    // O MySQL é a fonte durável; cache pode ser reconstruído sem repetir o motor.
    try { await cache.put(id, step); } catch (error) { request.log.warn(error, 'Falha ao atualizar Redis'); }
    return step.result.commands;
  });

  app.get<{ Params: { id: string } }>('/houses/:id/state', async request => {
    const id = simulation(request.headers), step = await latest(id);
    const fallback = houseReading(step, request.params.id);
    let state = fallback;
    try {
      const cached = await cache.get(id, request.params.id);
      if (cached && parseTimestamp(cached.timestamp) === step.time) state = cached;
      else await cache.put(id, step);
    } catch (error) { request.log.warn(error, 'Estado recuperado do MySQL'); }
    return state;
  });

  app.get<{ Params: { id: string }; Querystring: Record<string, string> }>('/houses/:id/history', async request => {
    const id = simulation(request.headers), step = await latest(id);
    houseReading(step, request.params.id);
    const { from, to, limit } = range(request.query, step.time);
    return repository.history(id, request.params.id, from, to, limit);
  });

  app.get<{ Params: { id: string } }>('/houses/:id/decision', async request => {
    const step = await latest(simulation(request.headers));
    houseReading(step, request.params.id);
    return step.result.commands.find(command => command.house_id === request.params.id);
  });

  app.put<{ Params: { id: string }; Body: EvTarget }>('/houses/:id/ev',
    { schema: { body: targetSchema } }, async request => {
      const id = simulation(request.headers);
      await repository.transaction(id, async session => {
        const step = await session.latest();
        if (!step) throw new ApiError(404, 'Simulação sem leituras.');
        if (houseReading(step, request.params.id).ev.capacity_kwh === 0) throw new ApiError(409, 'Casa sem veículo.');
        await session.setTarget(request.params.id, request.body);
      });
      return { house_id: request.params.id, ...request.body };
    });

  for (const side of ['offers', 'orders'] as const) {
    app.get(`/market/${side}`, async request => (await latest(simulation(request.headers))).result[side]);
  }
  app.get<{ Querystring: Record<string, string> }>('/market/trades', async request => {
    const id = simulation(request.headers), step = await latest(id);
    const { from, to, limit } = range(request.query, step.time);
    const steps = await repository.steps(id, from, to + 1);
    return steps.flatMap(item => item.result.trades.map(trade => ({ ...trade, timestamp: item.readings[0].timestamp }))).slice(0, limit);
  });

  app.get('/comparison', async request => options.comparison(simulation(request.headers)));
  app.get('/summary/today', async request => {
    const id = simulation(request.headers), step = await latest(id), day = localDay(step.time);
    const totals = summarize(await repository.steps(id, day.from, day.to), options.prices, options.exportValue, options.emissionFactor);
    let savings: number | null = null, co2: number | null = null;
    try {
      const comparison = await options.comparison(id);
      if (parseTimestamp(comparison.period.from) === day.from && parseTimestamp(comparison.period.to) === day.to) {
        savings = comparison.baseline.cost - comparison.optimized.cost;
        if (options.emissionFactor !== null) co2 = (comparison.baseline.import_kwh - comparison.optimized.import_kwh) * options.emissionFactor;
      }
    } catch (error) { if (!(error instanceof ApiError && error.statusCode === 503)) throw error; }
    return { date: day.date, ...totals, savings, co2_avoided_kg: co2 };
  });
  app.addHook('onClose', async () => { await Promise.all([repository.close(), cache.close()]); });
  return app;
}

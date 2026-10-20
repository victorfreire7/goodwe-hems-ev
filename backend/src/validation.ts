import { Ajv } from 'ajv';
import { ApiError, type EngineResult, type EvTarget, type Reading } from './types.js';

const number = { type: 'number', minimum: 0 };
const soc = { ...number, maximum: 100 };
const id = { type: 'string', pattern: '^[A-Za-z0-9_-]{1,64}$' };
const time = { type: 'string', pattern: '^([01][0-9]|2[0-3]):[0-5][0-9]$' };
const timestamp = { type: 'string', maxLength: 35 };
const object = (properties: Record<string, unknown>, required = Object.keys(properties)) =>
  ({ type: 'object', properties, required, additionalProperties: false });

export const targetSchema = object({ target_soc_percent: soc, departure_time: time });
export const readingSchema = object({
  house_id: id, timestamp, pv_power_kw: number, load_power_kw: number,
  battery: object({ soc_percent: { ...soc, minimum: 10 }, power_kw: { type: 'number' } }),
  ev: object({ connected: { type: 'boolean' }, soc_percent: soc, capacity_kwh: number,
    target_soc_percent: soc, departure_time: { anyOf: [time, { type: 'null' }] },
    charge_power_kw: { ...number, maximum: 7 } }),
  grid_power_kw: { type: 'number' },
});
export const readingsSchema = { type: 'array', minItems: 1, maxItems: 10, items: readingSchema };
const commandSchema = object({
  house_id: id, timestamp, ev_charge_power_kw: { ...number, maximum: 7 },
  battery_power_kw: { type: 'number' },
  market: object({ sold_kwh: number, bought_kwh: number }),
  reason: { type: 'string', minLength: 1, maxLength: 1000 },
});
const engineSchema = object({
  commands: { type: 'array', minItems: 1, maxItems: 10, items: commandSchema },
  trades: { type: 'array', maxItems: 100, items: object({ seller_id: id, buyer_id: id,
    quantity_kwh: { type: 'number', exclusiveMinimum: 0 }, price_per_kwh: number }) },
  offers: { type: 'array', maxItems: 10, items: object({ house_id: id,
    quantity_kwh: number, export_value_per_kwh: number }) },
  orders: { type: 'array', maxItems: 10, items: object({ house_id: id,
    quantity_kwh: number, grid_price_per_kwh: number }) },
});
const validateEngine = new Ajv().compile(engineSchema);

export function parseTimestamp(value: string): number {
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(?:\.\d{1,3})?(Z|[+-](?:0\d|1[0-4]):[0-5]\d)$/.exec(value);
  const milliseconds = Date.parse(value);
  if (!match || !Number.isFinite(milliseconds)) throw new ApiError(400, 'Timestamp ISO com fuso obrigatório.');
  const [, year, month, day, hour, minute, second] = match;
  const calendar = new Date(Date.UTC(+year, +month - 1, +day));
  if (+year < 2000 || +month !== calendar.getUTCMonth() + 1 || +day !== calendar.getUTCDate()
    || +hour > 23 || +minute > 59 || +second > 59) throw new ApiError(400, 'Data ou hora inválida.');
  return milliseconds;
}

export function validateBatch(readings: Reading[]): number {
  const instant = parseTimestamp(readings[0].timestamp);
  const ids = new Set<string>();
  for (const reading of readings) {
    if (parseTimestamp(reading.timestamp) !== instant) throw new ApiError(400, 'As casas devem ter o mesmo timestamp.');
    if (ids.has(reading.house_id)) throw new ApiError(400, 'Casa duplicada no passo.');
    ids.add(reading.house_id);
    if (reading.ev.capacity_kwh === 0) {
      if (reading.ev.connected || reading.ev.charge_power_kw !== 0 || reading.ev.departure_time !== null)
        throw new ApiError(400, 'Casa sem EV deve informar capacidade e carga zero e saída nula.');
    } else if (reading.ev.departure_time === null) throw new ApiError(400, 'Horário de saída do EV obrigatório.');
    if (!reading.ev.connected && reading.ev.charge_power_kw !== 0) throw new ApiError(400, 'EV desconectado não pode carregar.');
  }
  return instant;
}

export function validateEngineResult(value: unknown, readings: Reading[]): EngineResult {
  const fail = () => { throw new ApiError(502, 'Resposta inválida do motor.'); };
  if (!validateEngine(value)) fail();
  const result = value as EngineResult;
  const byId = new Map(readings.map(reading => [reading.house_id, reading]));
  const commands = new Map(result.commands.map(command => [command.house_id, command]));
  if (commands.size !== readings.length || result.commands.length !== readings.length) fail();
  for (const command of result.commands) {
    const reading = byId.get(command.house_id);
    if (!reading || command.timestamp !== reading.timestamp
      || (command.market.sold_kwh > 0 && command.market.bought_kwh > 0)) fail();
  }
  const sold = new Map<string, number>(), bought = new Map<string, number>();
  for (const trade of result.trades) {
    if (!byId.has(trade.seller_id) || !byId.has(trade.buyer_id) || trade.seller_id === trade.buyer_id) fail();
    sold.set(trade.seller_id, (sold.get(trade.seller_id) ?? 0) + trade.quantity_kwh);
    bought.set(trade.buyer_id, (bought.get(trade.buyer_id) ?? 0) + trade.quantity_kwh);
  }
  for (const command of result.commands) {
    if (Math.abs(command.market.sold_kwh - (sold.get(command.house_id) ?? 0)) > 1e-6
      || Math.abs(command.market.bought_kwh - (bought.get(command.house_id) ?? 0)) > 1e-6) fail();
  }
  for (const entry of [...result.offers, ...result.orders]) if (!byId.has(entry.house_id)) fail();
  return result;
}

export function applyTargets(readings: Reading[], targets: Record<string, EvTarget>): Reading[] {
  return readings.map(reading => ({ ...reading, ev: { ...reading.ev, ...targets[reading.house_id] } }));
}

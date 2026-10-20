import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('../../', import.meta.url));

export function configuration(env = process.env) {
  const integer = (key: string, fallback: number) => {
    const value = Number(env[key] ?? fallback);
    if (!Number.isInteger(value) || value < 1 || value > 65535) throw new Error(`${key} inválido.`);
    return value;
  };
  const optionalNumber = (key: string): number | null => {
    const raw = env[key]?.trim();
    if (!raw) return null;
    const value = Number(raw);
    if (!Number.isFinite(value) || value < 0) throw new Error(`${key} deve ser não negativo.`);
    return value;
  };
  const mode = env.ENGINE_MODE ?? 'neutral';
  if (!['neutral', 'http'].includes(mode)) throw new Error('ENGINE_MODE deve ser neutral ou http.');
  const exportValue = optionalNumber('EXPORT_VALUE_PER_KWH');
  if (mode === 'http' && exportValue === null) throw new Error('Defina EXPORT_VALUE_PER_KWH para integrar o motor.');
  const engineUrl = env.ENGINE_URL ?? 'http://localhost:8000';
  if (!['http:', 'https:'].includes(new URL(engineUrl).protocol)) throw new Error('ENGINE_URL deve usar HTTP.');
  if (!env.MYSQL_PASSWORD) throw new Error('Defina MYSQL_PASSWORD.');
  return {
    mode, exportValue, engineUrl,
    emissionFactor: optionalNumber('GRID_EMISSION_FACTOR_KG_PER_KWH'),
    engineTimeout: integer('ENGINE_TIMEOUT_MS', 5000),
    port: integer('BACKEND_PORT', 3000), host: env.BACKEND_HOST ?? '127.0.0.1',
    mysql: { host: env.MYSQL_HOST ?? 'localhost', port: integer('MYSQL_PORT', 3306),
      database: env.MYSQL_DATABASE ?? 'hems', user: env.MYSQL_USER ?? 'hems', password: env.MYSQL_PASSWORD,
      connectionLimit: 5, connectTimeout: 5000, charset: 'utf8mb4' },
    redis: { socket: { host: env.REDIS_HOST ?? 'localhost', port: integer('REDIS_PORT', 6379),
      connectTimeout: 3000, reconnectStrategy: (retries: number) => Math.min(250 * (retries + 1), 3000) },
      disableOfflineQueue: true },
    tariffFile: resolve(root, env.TARIFF_FILE ?? 'dados/processados/tarifa_enel_sp_branca.csv'),
    comparisonFile: resolve(root, env.COMPARISON_FILE ?? 'dados/processados/comparison.json'),
    optimized: env.SIM_OPTIMIZATION !== 'false',
  };
}

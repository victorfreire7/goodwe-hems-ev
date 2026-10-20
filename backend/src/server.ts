import { createPool } from 'mysql2/promise';
import { createClient } from 'redis';
import { buildApp } from './app.js';
import { configuration } from './config.js';
import { neutralDecide, httpDecide } from './engine.js';
import { loadTariff, storedComparison } from './metrics.js';
import { MySqlRepository, RedisStateCache } from './storage.js';

async function main() {
  const config = configuration();
  const repository = new MySqlRepository(createPool(config.mysql));
  const redis = createClient(config.redis);
  redis.on('error', error => console.error('Redis:', error.message));
  try {
    await repository.initialize();
    await redis.connect();
    const app = buildApp({ repository, cache: new RedisStateCache(redis), logger: true,
      engineMode: config.mode, exportValue: config.exportValue, emissionFactor: config.emissionFactor,
      prices: await loadTariff(config.tariffFile),
      comparison: simulation => storedComparison(repository, config.comparisonFile, simulation),
      decide: config.mode === 'neutral' ? neutralDecide
        : httpDecide(config.engineUrl, config.engineTimeout, config.exportValue!, config.optimized) });
    for (const signal of ['SIGINT', 'SIGTERM'] as const) process.once(signal, () => {
      app.close().catch(error => { console.error(error.message); process.exitCode = 1; });
    });
    await app.listen({ port: config.port, host: config.host });
  } catch (error) {
    await Promise.allSettled([repository.close(), redis.isOpen ? redis.quit() : Promise.resolve()]);
    throw error;
  }
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });

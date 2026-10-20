export interface EvTarget {
  target_soc_percent: number;
  departure_time: string;
}

export interface Reading {
  house_id: string;
  timestamp: string;
  pv_power_kw: number;
  load_power_kw: number;
  battery: { soc_percent: number; power_kw: number };
  ev: {
    connected: boolean;
    soc_percent: number;
    capacity_kwh: number;
    target_soc_percent: number;
    departure_time: string | null;
    charge_power_kw: number;
  };
  grid_power_kw: number;
}

export interface Command {
  house_id: string;
  timestamp: string;
  ev_charge_power_kw: number;
  battery_power_kw: number;
  market: { sold_kwh: number; bought_kwh: number };
  reason: string;
}

export interface Trade {
  seller_id: string;
  buyer_id: string;
  quantity_kwh: number;
  price_per_kwh: number;
}

export interface EngineResult {
  commands: Command[];
  trades: Trade[];
  offers: { house_id: string; quantity_kwh: number; export_value_per_kwh: number }[];
  orders: { house_id: string; quantity_kwh: number; grid_price_per_kwh: number }[];
}

export interface Step {
  time: number;
  hash: string;
  readings: Reading[];
  result: EngineResult;
}

export interface Comparison {
  simulation_id: string;
  period: { from: string; to: string };
  baseline: { cost: number; import_kwh: number };
  optimized: { cost: number; import_kwh: number };
}

export interface Session {
  step(time: number): Promise<Step | null>;
  latest(): Promise<Step | null>;
  targets(): Promise<Record<string, EvTarget>>;
  setTarget(house: string, target: EvTarget): Promise<void>;
  save(step: Step): Promise<void>;
  comparison(): Promise<Comparison | null>;
  setComparison(value: Comparison): Promise<void>;
}

export interface Repository {
  transaction<T>(simulation: string, work: (session: Session) => Promise<T>): Promise<T>;
  history(simulation: string, house: string, from: number, to: number, limit: number): Promise<Reading[]>;
  steps(simulation: string, from: number, to: number): Promise<Step[]>;
  forSimulation(simulation: string): Session;
  health(): Promise<void>;
  close(): Promise<void>;
}

export interface StateCache {
  get(simulation: string, house: string): Promise<Reading | null>;
  put(simulation: string, step: Step): Promise<void>;
  health(): Promise<void>;
  close(): Promise<void>;
}

export type Decide = (readings: Reading[], targets: Record<string, EvTarget>) => Promise<EngineResult>;

export class ApiError extends Error {
  constructor(public statusCode: number, message: string) { super(message); }
}

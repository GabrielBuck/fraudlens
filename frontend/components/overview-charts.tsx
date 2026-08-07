"use client";

import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const colors: Record<string, string> = {
  baixa: "#48d7a0",
  média: "#f6c85f",
  alta: "#ff8f5c",
  crítica: "#ff5570",
};

export function TimelineChart({
  data,
}: {
  data: Array<{ date: string; volume: number; alerts: number }>;
}) {
  return (
    <div
      className="chart-wrap"
      role="img"
      aria-label="Série temporal de volume monitorado e alertas"
    >
      <ResponsiveContainer width="100%" height={270}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="volumeGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#38d9f2" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#38d9f2" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#203142" vertical={false} />
          <XAxis
            dataKey="date"
            stroke="#73879a"
            tickLine={false}
            axisLine={false}
            minTickGap={28}
          />
          <YAxis
            stroke="#73879a"
            tickLine={false}
            axisLine={false}
            width={48}
          />
          <Tooltip
            contentStyle={{
              background: "#102131",
              border: "1px solid #2b4255",
              borderRadius: 12,
            }}
          />
          <Area
            type="monotone"
            dataKey="volume"
            name="Volume (R$)"
            stroke="#38d9f2"
            strokeWidth={2.5}
            fill="url(#volumeGradient)"
          />
          <Area
            type="monotone"
            dataKey="alerts"
            name="Alertas"
            stroke="#ff8f5c"
            strokeWidth={2}
            fill="none"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

export function SeverityChart({
  data,
}: {
  data: Array<{ severity: string; count: number }>;
}) {
  return (
    <div
      className="chart-wrap"
      role="img"
      aria-label="Distribuição dos alertas por severidade"
    >
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={data}
            dataKey="count"
            nameKey="severity"
            innerRadius={66}
            outerRadius={92}
            paddingAngle={4}
          >
            {data.map((entry) => (
              <Cell
                key={entry.severity}
                fill={colors[entry.severity] ?? "#38d9f2"}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "#102131",
              border: "1px solid #2b4255",
              borderRadius: 12,
            }}
          />
          <Legend iconType="circle" />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

export function PaymentChart({
  data,
}: {
  data: Array<{ method: string; alerts: number }>;
}) {
  return (
    <div
      className="chart-wrap"
      role="img"
      aria-label="Alertas por meio de pagamento"
    >
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data} layout="vertical" margin={{ left: 12 }}>
          <CartesianGrid stroke="#203142" horizontal={false} />
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="method"
            stroke="#93a7b9"
            width={100}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            contentStyle={{
              background: "#102131",
              border: "1px solid #2b4255",
              borderRadius: 12,
            }}
          />
          <Bar
            dataKey="alerts"
            name="Alertas"
            fill="#38d9f2"
            radius={[0, 6, 6, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ScoreHistogram({
  data,
}: {
  data: Array<{ bucket: string; count: number }>;
}) {
  return (
    <div
      className="chart-wrap"
      role="img"
      aria-label="Histograma dos scores de risco"
    >
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={data}>
          <CartesianGrid stroke="#203142" vertical={false} />
          <XAxis
            dataKey="bucket"
            stroke="#73879a"
            tickLine={false}
            axisLine={false}
          />
          <YAxis stroke="#73879a" tickLine={false} axisLine={false} />
          <Tooltip
            contentStyle={{
              background: "#102131",
              border: "1px solid #2b4255",
              borderRadius: 12,
            }}
          />
          <Bar
            dataKey="count"
            name="Transações"
            fill="#7c6cf2"
            radius={[5, 5, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

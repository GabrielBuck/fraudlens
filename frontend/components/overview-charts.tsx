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
  baixa: "#5f9677",
  média: "#c89b3c",
  alta: "#c9763f",
  crítica: "#df5b57",
};

const compactNumber = new Intl.NumberFormat("pt-BR", {
  notation: "compact",
  maximumFractionDigits: 1,
});

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
              <stop offset="0%" stopColor="#7894a6" stopOpacity={0.28} />
              <stop offset="100%" stopColor="#7894a6" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="#30353a" vertical={false} />
          <XAxis
            dataKey="date"
            stroke="#81878c"
            tickLine={false}
            axisLine={false}
            minTickGap={28}
          />
          <YAxis
            yAxisId="volume"
            stroke="#81878c"
            tickLine={false}
            axisLine={false}
            tickFormatter={(value: number) => compactNumber.format(value)}
            width={54}
          />
          <YAxis
            yAxisId="alerts"
            orientation="right"
            stroke="#81878c"
            tickLine={false}
            axisLine={false}
            allowDecimals={false}
            width={36}
          />
          <Tooltip
            contentStyle={{
              background: "#202326",
              border: "1px solid #3b4045",
              borderRadius: 6,
            }}
          />
          <Area
            yAxisId="volume"
            type="monotone"
            dataKey="volume"
            name="Volume (R$)"
            stroke="#89a6b8"
            strokeWidth={2.5}
            fill="url(#volumeGradient)"
          />
          <Area
            yAxisId="alerts"
            type="monotone"
            dataKey="alerts"
            name="Alertas"
            stroke="#d58a45"
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
                fill={colors[entry.severity] ?? "#7894a6"}
              />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "#202326",
              border: "1px solid #3b4045",
              borderRadius: 6,
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
        <BarChart data={data} layout="vertical" margin={{ left: 16 }}>
          <CartesianGrid stroke="#30353a" horizontal={false} />
          <XAxis type="number" hide />
          <YAxis
            type="category"
            dataKey="method"
            stroke="#9da2a7"
            width={116}
            tickLine={false}
            axisLine={false}
          />
          <Tooltip
            contentStyle={{
              background: "#202326",
              border: "1px solid #3b4045",
              borderRadius: 6,
            }}
          />
          <Bar
            dataKey="alerts"
            name="Alertas"
            fill="#7894a6"
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
          <CartesianGrid stroke="#30353a" vertical={false} />
          <XAxis
            dataKey="bucket"
            stroke="#81878c"
            tickLine={false}
            axisLine={false}
          />
          <YAxis stroke="#81878c" tickLine={false} axisLine={false} />
          <Tooltip
            contentStyle={{
              background: "#202326",
              border: "1px solid #3b4045",
              borderRadius: 6,
            }}
          />
          <Bar
            dataKey="count"
            name="Transações"
            fill="#8b7347"
            radius={[5, 5, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

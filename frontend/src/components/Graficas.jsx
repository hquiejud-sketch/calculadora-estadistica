import { useMemo } from 'react';
import { Chart as ChartJS, registerables } from 'chart.js';
import { Bar, Line, Doughnut } from 'react-chartjs-2';
import DiagramaCaja from './DiagramaCaja.jsx';
import { num } from '../formato.js';

ChartJS.register(...registerables);

const C = {
  barra: 'rgba(15, 118, 110, 0.55)',
  borde: '#0f766e',
  linea: '#ea580c',
  linea2: '#7c3aed',
  pastel: ['#0f766e', '#ea580c', '#7c3aed', '#0284c7', '#ca8a04', '#db2777', '#16a34a', '#64748b', '#9333ea', '#0891b2', '#dc2626', '#65a30d'],
};

function colorTexto() {
  const css = getComputedStyle(document.documentElement);
  return { texto: css.getPropertyValue('--texto-suave').trim() || '#555', grid: css.getPropertyValue('--linea').trim() || '#ddd' };
}

function base(tituloX, tituloY) {
  const { texto, grid } = colorTexto();
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { labels: { color: texto } } },
    scales: {
      x: { title: { display: !!tituloX, text: tituloX, color: texto }, ticks: { color: texto }, grid: { color: grid } },
      y: { title: { display: !!tituloY, text: tituloY, color: texto }, ticks: { color: texto }, grid: { color: grid }, beginAtZero: true },
    },
  };
}

export default function Graficas({ resultado: r }) {
  return r.tipo === 'agrupados' ? <GraficasAgrupados r={r} /> : <GraficasNoAgrupados r={r} />;
}

function GraficasAgrupados({ r }) {
  const filas = r.filas;
  const A = filas[0].A;

  const histograma = useMemo(() => {
    // Se agrega una clase vacía a cada lado para cerrar el polígono en el eje.
    const etiquetas = ['', ...filas.map((f) => `${num(f.lri)}–${num(f.lrs)}`), ''];
    const fi = [0, ...filas.map((f) => f.fi), 0];
    return {
      labels: etiquetas,
      datasets: [
        { type: 'line', label: 'Polígono de frecuencias', data: fi, borderColor: C.linea, backgroundColor: C.linea, tension: 0, pointRadius: 4 },
        { type: 'bar', label: 'Histograma (fi)', data: fi, backgroundColor: C.barra, borderColor: C.borde, borderWidth: 1, barPercentage: 1, categoryPercentage: 1 },
      ],
    };
  }, [filas]);

  const ojiva = useMemo(() => ({
    datasets: [
      {
        label: 'Ojiva "menor que"',
        data: [{ x: filas[0].lri, y: 0 }, ...filas.map((f) => ({ x: f.lrs, y: f.Fi }))],
        borderColor: C.borde, backgroundColor: C.borde, pointRadius: 4,
      },
      {
        label: 'Ojiva "mayor que"',
        data: [...filas.map((f) => ({ x: f.lri, y: f.Fi_desc })), { x: filas[filas.length - 1].lrs, y: 0 }],
        borderColor: C.linea2, backgroundColor: C.linea2, pointRadius: 4, borderDash: [6, 4],
      },
    ],
  }), [filas]);

  const pastel = {
    labels: filas.map((f) => f.intervalo),
    datasets: [{ data: filas.map((f) => f.pct), backgroundColor: filas.map((_, i) => C.pastel[i % C.pastel.length]) }],
  };

  const optOjiva = base('Límites reales', 'Frecuencia acumulada');
  optOjiva.scales.x.type = 'linear';
  optOjiva.scales.x.ticks.stepSize = A;
  const { texto } = colorTexto();

  const q = r.posicion.cuartiles;
  return (
    <div className="grid-graficas">
      <Tarjeta titulo="Histograma y polígono de frecuencias" ancho>
        <Bar data={histograma} options={base('Clases (límites reales)', 'fi')} />
      </Tarjeta>
      <Tarjeta titulo="Ojivas (frecuencia acumulada)">
        <Line data={ojiva} options={optOjiva} />
      </Tarjeta>
      <Tarjeta titulo="Distribución porcentual">
        <Doughnut data={pastel} options={{ responsive: true, maintainAspectRatio: false,
          plugins: { legend: { position: 'right', labels: { color: texto } },
            tooltip: { callbacks: { label: (c) => ` ${c.label}: ${num(c.raw, 2)} %` } } } }} />
      </Tarjeta>
      <Tarjeta titulo="Diagrama de caja" ancho>
        <DiagramaCaja minimo={r.ordenados ? r.ordenados[0] : filas[0].lri}
          maximo={r.ordenados ? r.ordenados[r.ordenados.length - 1] : filas[filas.length - 1].lrs}
          q1={q[0].valor} me={q[1].valor} q3={q[2].valor} media={r.tendencia_central.media.valor} />
      </Tarjeta>
    </div>
  );
}

function GraficasNoAgrupados({ r }) {
  const filas = r.tabla_simple;
  const { texto } = colorTexto();
  const barras = {
    labels: filas.map((f) => num(f.valor)),
    datasets: [{ label: 'Frecuencia (fi)', data: filas.map((f) => f.fi), backgroundColor: C.barra, borderColor: C.borde, borderWidth: 1 }],
  };
  const acumulada = {
    datasets: [{
      label: 'Frecuencia acumulada (Fi)',
      data: filas.map((f) => ({ x: f.valor, y: f.Fi })),
      borderColor: C.linea, backgroundColor: C.linea, stepped: true, pointRadius: 3,
    }],
  };
  const optAcum = base('Valor', 'Fi');
  optAcum.scales.x.type = 'linear';
  const optBarras = base('Valor', 'fi');
  optBarras.scales.y.ticks.precision = 0;

  const c = r.caja;
  return (
    <div className="grid-graficas">
      <Tarjeta titulo="Gráfica de barras (frecuencia por valor)" ancho>
        <Bar data={barras} options={optBarras} />
      </Tarjeta>
      <Tarjeta titulo="Frecuencia acumulada">
        <Line data={acumulada} options={optAcum} />
      </Tarjeta>
      {filas.length <= 12 ? (
        <Tarjeta titulo="Distribución porcentual">
          <Doughnut data={{ labels: filas.map((f) => num(f.valor)), datasets: [{ data: filas.map((f) => f.pct), backgroundColor: C.pastel }] }}
            options={{ responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'right', labels: { color: texto } } } }} />
        </Tarjeta>
      ) : (
        <Tarjeta titulo="Resumen de cinco números">
          <div className="cinco">
            {[['Mín', c.minimo], ['Q1', c.q1], ['Me', c.mediana], ['Q3', c.q3], ['Máx', c.maximo]].map(([e, v]) => (
              <div key={e}><small>{e}</small><strong>{num(v)}</strong></div>
            ))}
          </div>
        </Tarjeta>
      )}
      <Tarjeta titulo="Diagrama de caja y bigotes" ancho>
        <DiagramaCaja minimo={c.minimo} maximo={c.maximo} q1={c.q1} me={c.mediana} q3={c.q3}
          media={r.tendencia_central.media.valor} limInf={c.limite_inferior} limSup={c.limite_superior} atipicos={c.atipicos} datos={r.resumen.ordenados} />
      </Tarjeta>
    </div>
  );
}

function Tarjeta({ titulo, ancho, children }) {
  return (
    <div className={`tarjeta grafica ${ancho ? 'ancho' : ''}`}>
      <h3>{titulo}</h3>
      <div className="lienzo">{children}</div>
    </div>
  );
}

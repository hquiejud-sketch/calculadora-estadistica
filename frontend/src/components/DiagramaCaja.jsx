import { num } from '../formato.js';

// Diagrama de caja dibujado a mano en SVG (Chart.js no lo trae de fábrica).
export default function DiagramaCaja({ minimo, maximo, q1, me, q3, media, limInf, limSup, atipicos = [], datos = null }) {
  const W = 700, H = 200, M = 50;
  // Con atípicos, los bigotes llegan al último dato que queda dentro de las cercas.
  const internos = atipicos.length && datos ? datos.filter((v) => v >= limInf && v <= limSup) : null;
  const bigoteInf = internos?.length ? Math.min(...internos) : minimo;
  const bigoteSup = internos?.length ? Math.max(...internos) : maximo;
  const lo = Math.min(minimo, ...atipicos);
  const hi = Math.max(maximo, ...atipicos);
  const pad = (hi - lo) * 0.05 || 1;
  const x = (v) => M + ((v - (lo - pad)) / (hi - lo + 2 * pad)) * (W - 2 * M);
  const y = 70;

  // Q1 y Q3 se rotulan arriba de la caja para que no se encimen con Me.
  const abajo = escalonar([[bigoteInf, 'Mín'], [me, 'Me'], [bigoteSup, 'Máx']], x, 160, 16);
  const arriba = escalonar([[q1, 'Q1'], [q3, 'Q3']], x, y - 38, -16);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="caja-svg" role="img" aria-label="Diagrama de caja">
      <line x1={M} x2={W - M} y1={140} y2={140} className="eje" />
      <line x1={x(bigoteInf)} x2={x(q1)} y1={y} y2={y} className="bigote" />
      <line x1={x(q3)} x2={x(bigoteSup)} y1={y} y2={y} className="bigote" />
      <line x1={x(bigoteInf)} x2={x(bigoteInf)} y1={y - 15} y2={y + 15} className="bigote" />
      <line x1={x(bigoteSup)} x2={x(bigoteSup)} y1={y - 15} y2={y + 15} className="bigote" />
      <rect x={x(q1)} y={y - 30} width={Math.max(1, x(q3) - x(q1))} height={60} className="caja" />
      <line x1={x(me)} x2={x(me)} y1={y - 30} y2={y + 30} className="mediana" />
      <g transform={`translate(${x(media)},${y})`}>
        <path d="M0,-6 L6,0 L0,6 L-6,0 Z" className="media" />
      </g>
      {atipicos.map((a, i) => (
        <circle key={i} cx={x(a)} cy={y} r={5} className="atipico" />
      ))}
      {abajo.map(([v, e, fy]) => (
        <g key={e}>
          <line x1={x(v)} x2={x(v)} y1={136} y2={144} className="eje" />
          <text x={x(v)} y={fy} textAnchor="middle" className="etq">{e} {num(v, 2)}</text>
        </g>
      ))}
      {arriba.map(([v, e, fy]) => (
        <text key={e} x={x(v)} y={fy} textAnchor="middle" className="etq">{e} {num(v, 2)}</text>
      ))}
      <text x={x(media)} y={y + 48} textAnchor="middle" className="etq media-txt">x̄ {num(media, 2)}</text>
    </svg>
  );
}

// Si dos etiquetas quedan muy cerca, la segunda baja (o sube) una línea.
function escalonar(marcas, x, yBase, salto) {
  let anterior = -Infinity;
  let nivel = 0;
  return marcas.map(([v, e]) => {
    const px = x(v);
    nivel = px - anterior < 80 ? nivel + 1 : 0;
    anterior = px;
    return [v, e, yBase + (nivel % 2) * salto];
  });
}

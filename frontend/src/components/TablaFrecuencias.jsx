import { num } from '../formato.js';

export default function TablaFrecuencias({ resultado }) {
  const agrupados = resultado.tipo === 'agrupados';
  const ordenados = agrupados ? resultado.ordenados : resultado.resumen.ordenados;

  return (
    <div className="tarjeta">
      <h3>Tabla de distribución de frecuencias</h3>
      {agrupados ? <TablaAgrupada r={resultado} /> : <TablaSimple filas={resultado.tabla_simple} />}

      {ordenados && (
        <details className="ordenados">
          <summary>Datos ordenados ({ordenados.length})</summary>
          <div className="lista-datos">
            {ordenados.map((x, i) => <span key={i}>{num(x)}</span>)}
          </div>
        </details>
      )}
    </div>
  );
}

function TablaAgrupada({ r }) {
  const { filas, totales, parametros: p, pasos_construccion } = r;
  const discreto = p.modo === 'discreto';
  return (
    <>
      <div className="construccion">
        {pasos_construccion.map((s, i) => (
          <div key={i} className="mini-paso">
            <small>{s.titulo}</small>
            <code>{s.sustitucion || s.formula}</code>
            <strong>{s.resultado}</strong>
          </div>
        ))}
      </div>
      <div className="tabla-scroll">
        <table>
          <thead>
            <tr>
              <th>#</th>
              <th>{discreto ? 'Lím. aparentes' : 'Intervalo'}</th>
              {discreto && <th>Lím. reales</th>}
              <th>xi</th><th>fi</th><th>Fi</th><th>fr</th><th>Fr</th><th>%</th>
              <th>xi·fi</th><th>xi²·fi</th>
            </tr>
          </thead>
          <tbody>
            {filas.map((f) => (
              <tr key={f.clase}>
                <td>{f.clase}</td>
                <td className="izq">{f.intervalo}</td>
                {discreto && <td className="izq">{num(f.lri)} – {num(f.lrs)}</td>}
                <td>{num(f.xi)}</td>
                <td className="fuerte">{f.fi}</td>
                <td>{f.Fi}</td>
                <td>{num(f.fr)}</td>
                <td>{num(f.Fr)}</td>
                <td>{num(f.pct, 2)}</td>
                <td>{num(f.xi_fi)}</td>
                <td>{num(f.xi2_fi)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr>
              <td colSpan={discreto ? 4 : 3} className="izq">Σ</td>
              <td className="fuerte">{totales.fi}</td>
              <td /><td>{num(totales.fr)}</td><td /><td>{num(totales.pct, 2)}</td>
              <td>{num(totales.xi_fi)}</td><td>{num(totales.xi2_fi)}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </>
  );
}

function TablaSimple({ filas }) {
  return (
    <div className="tabla-scroll">
      <table>
        <thead>
          <tr><th>Valor xi</th><th>fi</th><th>Fi</th><th>fr</th><th>Fr</th><th>%</th><th>% acum.</th></tr>
        </thead>
        <tbody>
          {filas.map((f) => (
            <tr key={f.valor}>
              <td className="fuerte">{num(f.valor)}</td>
              <td>{f.fi}</td><td>{f.Fi}</td>
              <td>{num(f.fr)}</td><td>{num(f.Fr)}</td>
              <td>{num(f.pct, 2)}</td><td>{num(f.Pct, 2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

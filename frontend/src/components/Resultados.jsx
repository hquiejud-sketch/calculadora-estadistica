import { useState } from 'react';
import TablaFrecuencias from './TablaFrecuencias.jsx';
import Medidas from './Medidas.jsx';
import Graficas from './Graficas.jsx';
import Procedimiento from './Procedimiento.jsx';
import Tutor from './Tutor.jsx';
import { num } from '../formato.js';

const PESTANAS = [
  ['tabla', 'Tabla'],
  ['medidas', 'Medidas'],
  ['graficas', 'Gráficas'],
  ['pasos', 'Paso a paso'],
  ['tutor', 'Tutor IA'],
];

export default function Resultados(props) {
  const { resultado, contexto, analisisId, onGuardar } = props;
  const [pestana, setPestana] = useState('tabla');
  const [titulo, setTitulo] = useState('');
  const [msgGuardar, setMsgGuardar] = useState('');

  const agrupados = resultado.tipo === 'agrupados';
  const n = agrupados ? resultado.parametros.n : resultado.resumen.n;
  const tc = resultado.tendencia_central;
  const disp = resultado.dispersion;

  async function guardar() {
    try {
      const id = await onGuardar(titulo || contexto.variable || `Análisis de ${n} datos`);
      setMsgGuardar(`Guardado como #${id}`);
    } catch (e) {
      setMsgGuardar(e.message);
    }
  }

  return (
    <section className="resultados">
      <div className="tarjeta resumen">
        <div className="resumen-titulo">
          <h2 className="titulo-seccion"><span>02</span> Resultados</h2>
          <span className="chip">{agrupados ? 'Datos agrupados' : 'Datos no agrupados'}</span>
        </div>
        <div className="kpis">
          <Kpi etiqueta="n" valor={n} />
          <Kpi etiqueta="Media x̄" valor={num(tc.media.valor)} />
          <Kpi etiqueta="Mediana" valor={num(tc.mediana.valor)} />
          <Kpi etiqueta="Desv. s" valor={num(disp.desviacion.valor)} />
          <Kpi etiqueta="CV" valor={disp.coeficiente_variacion.valor === null ? '—' : `${num(disp.coeficiente_variacion.valor, 2)}%`} />
        </div>
        <div className="guardar no-imprimir">
          {analisisId ? (
            <span className="ok">✓ Guardado en la base de datos (#{analisisId})</span>
          ) : (
            <>
              <input value={titulo} onChange={(e) => setTitulo(e.target.value)} placeholder="Nombre para guardar (opcional)" />
              <button className="btn secundario" onClick={guardar}>Guardar</button>
              {msgGuardar && <span className="ok">{msgGuardar}</span>}
            </>
          )}
          <button className="btn secundario" onClick={() => window.print()}>Exportar PDF</button>
        </div>
      </div>

      <div className="pestanas no-imprimir">
        {PESTANAS.map(([id, txt]) => (
          <button key={id} className={pestana === id ? 'activo' : ''} onClick={() => setPestana(id)}>{txt}</button>
        ))}
      </div>

      {/* Al imprimir se muestran todas las secciones. */}
      <div className={`panel ${pestana === 'tabla' ? 'visible' : ''}`}><TablaFrecuencias resultado={resultado} /></div>
      <div className={`panel ${pestana === 'medidas' ? 'visible' : ''}`}><Medidas resultado={resultado} /></div>
      <div className={`panel ${pestana === 'graficas' ? 'visible' : ''}`}><Graficas resultado={resultado} /></div>
      <div className={`panel ${pestana === 'pasos' ? 'visible' : ''}`}><Procedimiento resultado={resultado} /></div>
      <div className={`panel ${pestana === 'tutor' ? 'visible' : ''}`}><Tutor {...props} /></div>
    </section>
  );
}

function Kpi({ etiqueta, valor }) {
  return (
    <div className="kpi">
      <small>{etiqueta}</small>
      <strong>{valor}</strong>
    </div>
  );
}

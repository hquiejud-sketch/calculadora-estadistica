import { useEffect, useState } from 'react';
import { api } from './api/cliente.js';
import { parsearDatos } from './formato.js';
import Encabezado from './components/Encabezado.jsx';
import PanelEntrada from './components/PanelEntrada.jsx';
import Resultados from './components/Resultados.jsx';
import Guardados from './components/Guardados.jsx';
import Historial from './components/Historial.jsx';

const OPCIONES_INICIALES = {
  metodo_k: 'sturges',
  k: '',
  amplitud: '',
  limite_inicial: '',
  modo: 'continuo',
  percentiles: '10, 90',
  deciles: '',
};

const listaEnteros = (t) => (t.match(/\d+/g) || []).map(Number);

export default function App() {
  const [vista, setVista] = useState('calculadora');
  const [salud, setSalud] = useState(null);

  // Entrada
  const [tipo, setTipo] = useState('agrupados');
  const [fuente, setFuente] = useState('datos');
  const [textoDatos, setTextoDatos] = useState('');
  const [intervalos, setIntervalos] = useState([
    { li: '', ls: '', fi: '' },
    { li: '', ls: '', fi: '' },
    { li: '', ls: '', fi: '' },
  ]);
  const [opciones, setOpciones] = useState(OPCIONES_INICIALES);
  const [contexto, setContexto] = useState({ variable: '', unidad: '', descripcion: '' });

  // Resultado
  const [resultado, setResultado] = useState(null);
  const [version, setVersion] = useState(0); // reinicia la vista de resultados en cada cálculo
  const [solicitud, setSolicitud] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState('');
  const [analisisId, setAnalisisId] = useState(null);
  const [interpretacion, setInterpretacion] = useState(null);
  const [mensajes, setMensajes] = useState([]);

  useEffect(() => {
    api.salud().then(setSalud).catch(() => setSalud({ ok: false }));
  }, []);

  function armarSolicitud() {
    const op = {
      metodo_k: opciones.metodo_k,
      k: opciones.metodo_k === 'manual' && opciones.k ? Number(opciones.k) : null,
      amplitud: opciones.amplitud ? Number(opciones.amplitud) : null,
      limite_inicial: opciones.limite_inicial !== '' ? Number(opciones.limite_inicial) : null,
      modo: opciones.modo,
      percentiles: listaEnteros(opciones.percentiles).filter((p) => p > 0 && p < 100),
      deciles: listaEnteros(opciones.deciles).filter((d) => d > 0 && d < 10),
    };
    if (tipo === 'agrupados' && fuente === 'intervalos') {
      const ints = intervalos
        .filter((i) => i.li !== '' && i.ls !== '' && i.fi !== '')
        .map((i) => ({ li: Number(i.li), ls: Number(i.ls), fi: Number(i.fi) }));
      return { tipo, intervalos: ints, opciones: op };
    }
    return { tipo, datos: parsearDatos(textoDatos), opciones: op };
  }

  async function calcular() {
    setError('');
    setCargando(true);
    try {
      const sol = armarSolicitud();
      const res = await api.analizar(sol);
      setResultado(res);
      setVersion((v) => v + 1);
      setSolicitud(sol);
      setAnalisisId(null);
      setInterpretacion(null);
      setMensajes([]);
    } catch (e) {
      setError(e.message);
    } finally {
      setCargando(false);
    }
  }

  async function cargarEjemplo() {
    const ej = await api.ejemplo();
    setTextoDatos(ej.datos.join(', '));
    setFuente('datos');
    setContexto((c) => ({ ...c, variable: ej.variable, unidad: ej.unidad }));
  }

  async function guardar(titulo) {
    const r = await api.guardarAnalisis({
      titulo,
      solicitud,
      contexto,
      interpretacion: interpretacion?.texto ?? null,
    });
    setAnalisisId(r.id);
    return r.id;
  }

  async function abrirGuardado(id) {
    const a = await api.obtenerAnalisis(id);
    const ent = a.entrada;
    setTipo(a.tipo);
    if (ent.intervalos?.length) {
      setFuente('intervalos');
      setIntervalos(ent.intervalos.map((i) => ({ li: i.li, ls: i.ls, fi: i.fi })));
    } else {
      setFuente('datos');
      setTextoDatos((ent.datos || []).join(', '));
    }
    setContexto({ variable: '', unidad: '', descripcion: '', ...ent.contexto });
    setOpciones({
      ...OPCIONES_INICIALES,
      ...a.opciones,
      k: a.opciones.k ?? '',
      amplitud: a.opciones.amplitud ?? '',
      limite_inicial: a.opciones.limite_inicial ?? '',
      percentiles: (a.opciones.percentiles || []).join(', '),
      deciles: (a.opciones.deciles || []).join(', '),
    });
    setResultado(a.resultado);
    setVersion((v) => v + 1);
    setSolicitud({
      tipo: a.tipo,
      datos: ent.intervalos?.length ? undefined : ent.datos,
      intervalos: ent.intervalos?.length ? ent.intervalos : undefined,
      opciones: a.opciones,
    });
    setAnalisisId(a.id);
    setInterpretacion(a.interpretacion ? { texto: a.interpretacion, fuente: 'guardada' } : null);
    setMensajes(a.mensajes.map((m) => ({ rol: m.rol, contenido: m.contenido })));
    setVista('calculadora');
  }

  return (
    <div className="app">
      <Encabezado vista={vista} setVista={setVista} salud={salud} />

      {vista === 'calculadora' && (
        <main className="contenido">
          <PanelEntrada
            tipo={tipo} setTipo={setTipo}
            fuente={fuente} setFuente={setFuente}
            textoDatos={textoDatos} setTextoDatos={setTextoDatos}
            intervalos={intervalos} setIntervalos={setIntervalos}
            opciones={opciones} setOpciones={setOpciones}
            contexto={contexto} setContexto={setContexto}
            onCalcular={calcular} onEjemplo={cargarEjemplo}
            cargando={cargando} error={error} setError={setError}
          />
          {resultado ? (
            <Resultados
              key={version}
              resultado={resultado}
              contexto={contexto}
              analisisId={analisisId}
              onGuardar={guardar}
              interpretacion={interpretacion} setInterpretacion={setInterpretacion}
              mensajes={mensajes} setMensajes={setMensajes}
            />
          ) : (
            <section className="vacio tarjeta">
              <div className="vacio-sigma">Σ</div>
              <h2>Mete tus datos y dale a <em>Calcular</em></h2>
              <p>Puedes pegarlos, subir un CSV/Excel o escribir la tabla de intervalos de tu ejercicio.</p>
              <button className="btn secundario" onClick={cargarEjemplo}>Probar con datos de ejemplo</button>
            </section>
          )}
        </main>
      )}

      {vista === 'guardados' && <Guardados onAbrir={abrirGuardado} />}
      {vista === 'historial' && <Historial />}

      <footer className="pie">Σstadi · FastAPI + SQLite + React + Gemini</footer>
    </div>
  );
}

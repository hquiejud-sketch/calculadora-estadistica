import { useRef, useState } from 'react';
import { api } from '../api/cliente.js';
import { parsearDatos } from '../formato.js';

export default function PanelEntrada(props) {
  const {
    tipo, setTipo, fuente, setFuente, textoDatos, setTextoDatos,
    intervalos, setIntervalos, opciones, setOpciones, contexto, setContexto,
    onCalcular, onEjemplo, cargando, error, setError,
  } = props;
  const archivoRef = useRef(null);
  const [verOpciones, setVerOpciones] = useState(false);
  const n = parsearDatos(textoDatos).length;

  const op = (campo) => (e) => setOpciones({ ...opciones, [campo]: e.target.value });
  const ctx = (campo) => (e) => setContexto({ ...contexto, [campo]: e.target.value });

  async function subirArchivo(e) {
    const archivo = e.target.files?.[0];
    if (!archivo) return;
    try {
      const r = await api.importar(archivo);
      setTextoDatos(r.datos.join(', '));
      setFuente('datos');
      setError('');
    } catch (err) {
      setError(err.message);
    }
    e.target.value = '';
  }

  function cambiarIntervalo(i, campo, valor) {
    setIntervalos(intervalos.map((fila, j) => (j === i ? { ...fila, [campo]: valor } : fila)));
  }

  function agregarFila() {
    const ult = intervalos[intervalos.length - 1];
    const prev = intervalos[intervalos.length - 2];
    let nueva = { li: '', ls: '', fi: '' };
    if (ult?.li !== '' && ult?.ls !== '' && prev?.li !== '') {
      const paso = Number(ult.li) - Number(prev.li);
      nueva = { li: Number(ult.li) + paso, ls: Number(ult.ls) + paso, fi: '' };
    }
    setIntervalos([...intervalos, nueva]);
  }

  const nIntervalos = intervalos.reduce((s, i) => s + (Number(i.fi) || 0), 0);

  return (
    <section className="tarjeta entrada">
      <h2 className="titulo-seccion"><span>01</span> Datos</h2>

      <div className="segmentado">
        <button className={tipo === 'no_agrupados' ? 'activo' : ''} onClick={() => setTipo('no_agrupados')}>
          No agrupados
        </button>
        <button className={tipo === 'agrupados' ? 'activo' : ''} onClick={() => setTipo('agrupados')}>
          Agrupados (tabla)
        </button>
      </div>

      {tipo === 'agrupados' && (
        <div className="segmentado chico">
          <button className={fuente === 'datos' ? 'activo' : ''} onClick={() => setFuente('datos')}>
            Desde datos sueltos
          </button>
          <button className={fuente === 'intervalos' ? 'activo' : ''} onClick={() => setFuente('intervalos')}>
            Tabla ya hecha
          </button>
        </div>
      )}

      {tipo === 'agrupados' && fuente === 'intervalos' ? (
        <div className="intervalos">
          <div className="fila-int cabecera">
            <span>Lím. inf.</span><span>Lím. sup.</span><span>fi</span><span />
          </div>
          {intervalos.map((fila, i) => (
            <div className="fila-int" key={i}>
              <input type="number" value={fila.li} onChange={(e) => cambiarIntervalo(i, 'li', e.target.value)} />
              <input type="number" value={fila.ls} onChange={(e) => cambiarIntervalo(i, 'ls', e.target.value)} />
              <input type="number" min="0" value={fila.fi} onChange={(e) => cambiarIntervalo(i, 'fi', e.target.value)} />
              <button className="btn-icono" title="Quitar"
                onClick={() => setIntervalos(intervalos.filter((_, j) => j !== i))}>×</button>
            </div>
          ))}
          <div className="acciones-fila">
            <button className="btn texto" onClick={agregarFila}>+ Agregar clase</button>
            <span className="contador">n = {nIntervalos}</span>
          </div>
          <p className="ayuda">Si tus clases son tipo 20–24, 25–29 la app calcula sola los límites reales (19.5–24.5).</p>
        </div>
      ) : (
        <>
          <textarea
            value={textoDatos}
            onChange={(e) => setTextoDatos(e.target.value)}
            placeholder="Pega tus datos separados por coma, espacio o salto de línea&#10;Ej: 45, 52, 38, 61, 47…"
            rows={7}
          />
          <div className="acciones-fila">
            <button className="btn texto" onClick={() => archivoRef.current?.click()}>⬆ Subir CSV / Excel</button>
            <button className="btn texto" onClick={onEjemplo}>Ejemplo</button>
            <button className="btn texto" onClick={() => setTextoDatos('')}>Limpiar</button>
            <span className="contador">n = {n}</span>
            <input ref={archivoRef} type="file" accept=".csv,.txt,.xlsx" hidden onChange={subirArchivo} />
          </div>
        </>
      )}

      <div className="contexto">
        <label>Variable<input value={contexto.variable} onChange={ctx('variable')} placeholder="Ej: estatura de alumnos" /></label>
        <label>Unidad<input value={contexto.unidad} onChange={ctx('unidad')} placeholder="cm, Q, pts…" /></label>
      </div>

      <button className="btn texto desplegar" onClick={() => setVerOpciones(!verOpciones)}>
        {verOpciones ? '▾' : '▸'} Opciones avanzadas
      </button>
      {verOpciones && (
        <div className="opciones">
          {tipo === 'agrupados' && fuente === 'datos' && (
            <>
              <label>Número de clases
                <select value={opciones.metodo_k} onChange={op('metodo_k')}>
                  <option value="sturges">Sturges (1 + 3.322 log n)</option>
                  <option value="raiz">Raíz de n</option>
                  <option value="manual">Manual</option>
                </select>
              </label>
              {opciones.metodo_k === 'manual' && (
                <label>k<input type="number" min="1" value={opciones.k} onChange={op('k')} /></label>
              )}
              <label>Tipo de límites
                <select value={opciones.modo} onChange={op('modo')}>
                  <option value="continuo">Continuos [Li, Ls)</option>
                  <option value="discreto">Aparentes (20–24) + reales</option>
                </select>
              </label>
              <label>Amplitud (opcional)<input type="number" value={opciones.amplitud} onChange={op('amplitud')} placeholder="auto" /></label>
              <label>Límite inicial (opcional)<input type="number" value={opciones.limite_inicial} onChange={op('limite_inicial')} placeholder="Xmin" /></label>
            </>
          )}
          <label>Percentiles<input value={opciones.percentiles} onChange={op('percentiles')} placeholder="10, 90" /></label>
          <label>Deciles<input value={opciones.deciles} onChange={op('deciles')} placeholder="3, 7" /></label>
        </div>
      )}

      {error && <div className="alerta">{error}</div>}

      <button className="btn primario grande" onClick={onCalcular} disabled={cargando}>
        {cargando ? 'Calculando…' : 'Calcular'}
      </button>
    </section>
  );
}

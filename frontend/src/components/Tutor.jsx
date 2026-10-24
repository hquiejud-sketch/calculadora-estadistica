import { useEffect, useRef, useState } from 'react';
import Markdown from 'react-markdown';
import { api } from '../api/cliente.js';

const SUGERENCIAS = [
  '¿Mis datos son homogéneos?',
  '¿Por qué la media y la mediana son diferentes?',
  'Explícame cómo se calculó Q1',
  '¿Qué significa la asimetría que salió?',
];

export default function Tutor({ resultado, contexto, analisisId, interpretacion, setInterpretacion, mensajes, setMensajes }) {
  const [cargandoInt, setCargandoInt] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [texto, setTexto] = useState('');
  const [aviso, setAviso] = useState('');
  const finRef = useRef(null);

  useEffect(() => {
    finRef.current?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [mensajes, enviando]);

  async function interpretar() {
    setCargandoInt(true);
    try {
      const r = await api.interpretar({ resultado, contexto, analisis_id: analisisId });
      setInterpretacion(r);
      setAviso(r.aviso || '');
    } catch (e) {
      setAviso(e.message);
    } finally {
      setCargandoInt(false);
    }
  }

  async function enviar(mensaje) {
    const m = (mensaje ?? texto).trim();
    if (!m || enviando) return;
    const nuevos = [...mensajes, { rol: 'usuario', contenido: m }];
    setMensajes(nuevos);
    setTexto('');
    setEnviando(true);
    try {
      const r = await api.chat({ mensaje: m, historial: mensajes, resultado, contexto, analisis_id: analisisId });
      setMensajes([...nuevos, { rol: 'ia', contenido: r.texto }]);
      setAviso(r.aviso || '');
    } catch (e) {
      setMensajes([...nuevos, { rol: 'ia', contenido: `⚠ ${e.message}` }]);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="tutor">
      <div className="tarjeta interpretacion">
        <div className="cabecera-tutor">
          <h3>Interpretación para tu reporte</h3>
          <button className="btn primario" onClick={interpretar} disabled={cargandoInt}>
            {cargandoInt ? 'Pensando…' : interpretacion ? 'Volver a generar' : 'Interpretar con IA'}
          </button>
        </div>
        {aviso && <div className="alerta suave">{aviso}</div>}
        {interpretacion ? (
          <div className="markdown">
            <span className={`chip ${interpretacion.fuente}`}>{interpretacion.fuente === 'gemini' ? 'Gemini' : interpretacion.fuente === 'local' ? 'Modo local' : 'Guardada'}</span>
            <Markdown>{interpretacion.texto}</Markdown>
          </div>
        ) : (
          <p className="ayuda">La IA redacta qué significan tus resultados, listo para pegar en el reporte. No recalcula: usa los números de la calculadora.</p>
        )}
      </div>

      <div className="tarjeta chat no-imprimir">
        <h3>Pregúntale al tutor</h3>
        <div className="mensajes">
          {mensajes.length === 0 && (
            <div className="sugerencias">
              {SUGERENCIAS.map((s) => (
                <button key={s} className="sugerencia" onClick={() => enviar(s)}>{s}</button>
              ))}
            </div>
          )}
          {mensajes.map((m, i) => (
            <div key={i} className={`burbuja ${m.rol}`}>
              {m.rol === 'ia' ? <Markdown>{m.contenido}</Markdown> : m.contenido}
            </div>
          ))}
          {enviando && <div className="burbuja ia escribiendo"><span /><span /><span /></div>}
          <div ref={finRef} />
        </div>
        <form className="caja-chat" onSubmit={(e) => { e.preventDefault(); enviar(); }}>
          <input value={texto} onChange={(e) => setTexto(e.target.value)} placeholder="Escribe tu duda de estadística…" />
          <button className="btn primario" disabled={enviando || !texto.trim()}>Enviar</button>
        </form>
        {!analisisId && <p className="ayuda">Guarda el análisis para que la conversación quede en la base de datos.</p>}
      </div>
    </div>
  );
}

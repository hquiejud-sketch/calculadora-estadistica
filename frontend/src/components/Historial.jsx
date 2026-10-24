import { useEffect, useState } from 'react';
import { api } from '../api/cliente.js';

const ETIQUETAS = {
  ANALIZAR: 'Cálculo',
  GUARDAR: 'Guardado',
  ELIMINAR: 'Eliminado',
  IMPORTAR: 'Importación',
  IA_INTERPRETAR: 'IA · interpretación',
  IA_CHAT: 'IA · pregunta',
};

export default function Historial() {
  const [lista, setLista] = useState(null);

  const cargar = () => api.historial().then(setLista).catch(() => setLista([]));
  useEffect(() => { cargar(); }, []);

  async function borrar() {
    if (!confirm('¿Borrar todo el historial?')) return;
    await api.borrarHistorial();
    cargar();
  }

  return (
    <main className="contenido una-columna">
      <section className="tarjeta">
        <div className="resumen-titulo">
          <h2 className="titulo-seccion"><span>LOG</span> Historial de operaciones</h2>
          {lista?.length > 0 && <button className="btn texto peligro" onClick={borrar}>Borrar historial</button>}
        </div>
        {lista === null ? <p>Cargando…</p> : lista.length === 0 ? (
          <p className="ayuda">Sin operaciones todavía.</p>
        ) : (
          <ul className="linea-tiempo">
            {lista.map((h) => (
              <li key={h.id}>
                <span className={`chip ${h.accion.toLowerCase()}`}>{ETIQUETAS[h.accion] || h.accion}</span>
                <span className="detalle">{h.detalle}</span>
                <time>{h.fecha}</time>
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}

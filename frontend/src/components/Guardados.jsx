import { useEffect, useState } from 'react';
import { api } from '../api/cliente.js';
import { num } from '../formato.js';

export default function Guardados({ onAbrir }) {
  const [lista, setLista] = useState(null);
  const [error, setError] = useState('');

  const cargar = () => api.listarAnalisis().then(setLista).catch((e) => setError(e.message));
  useEffect(() => { cargar(); }, []);

  async function eliminar(id) {
    if (!confirm('¿Eliminar este análisis?')) return;
    await api.eliminarAnalisis(id);
    cargar();
  }

  return (
    <main className="contenido una-columna">
      <section className="tarjeta">
        <h2 className="titulo-seccion"><span>DB</span> Análisis guardados</h2>
        {error && <div className="alerta">{error}</div>}
        {lista === null ? <p>Cargando…</p> : lista.length === 0 ? (
          <p className="ayuda">Todavía no guardas nada. Calcula algo y dale a “Guardar”.</p>
        ) : (
          <div className="tabla-scroll">
            <table>
              <thead>
                <tr><th>#</th><th className="izq">Nombre</th><th>Tipo</th><th>n</th><th>x̄</th><th>Me</th><th>s</th><th>CV %</th><th className="izq">Fecha</th><th /></tr>
              </thead>
              <tbody>
                {lista.map((a) => (
                  <tr key={a.id}>
                    <td>{a.id}</td>
                    <td className="izq fuerte">{a.titulo}</td>
                    <td>{a.tipo === 'agrupados' ? 'Agrupados' : 'No agrupados'}</td>
                    <td>{a.n}</td>
                    <td>{num(a.media)}</td>
                    <td>{num(a.mediana)}</td>
                    <td>{num(a.desviacion)}</td>
                    <td>{num(a.cv, 2)}</td>
                    <td className="izq">{a.creado_en}</td>
                    <td className="acciones-tabla">
                      <button className="btn texto" onClick={() => onAbrir(a.id)}>Abrir</button>
                      <button className="btn texto peligro" onClick={() => eliminar(a.id)}>Eliminar</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}

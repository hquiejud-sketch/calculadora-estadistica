// Funciones para hablar con el backend (FastAPI).

async function pedir(ruta, opciones = {}) {
  const resp = await fetch(`/api${ruta}`, {
    headers: opciones.body instanceof FormData ? {} : { 'Content-Type': 'application/json' },
    ...opciones,
  });
  if (resp.status === 204) return null;
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) {
    const det = data.detail;
    const msg = Array.isArray(det) ? det.map((d) => d.msg).join('; ') : det;
    throw new Error(msg || `Error ${resp.status}`);
  }
  return data;
}

const post = (ruta, cuerpo) => pedir(ruta, { method: 'POST', body: JSON.stringify(cuerpo) });

export const api = {
  salud: () => pedir('/salud'),
  ejemplo: () => pedir('/ejemplo'),
  analizar: (sol) => post('/analizar', sol),
  importar: (archivo) => {
    const fd = new FormData();
    fd.append('archivo', archivo);
    return pedir('/importar', { method: 'POST', body: fd });
  },
  listarAnalisis: () => pedir('/analisis'),
  obtenerAnalisis: (id) => pedir(`/analisis/${id}`),
  guardarAnalisis: (cuerpo) => post('/analisis', cuerpo),
  eliminarAnalisis: (id) => pedir(`/analisis/${id}`, { method: 'DELETE' }),
  interpretar: (cuerpo) => post('/ia/interpretar', cuerpo),
  chat: (cuerpo) => post('/ia/chat', cuerpo),
  historial: () => pedir('/historial'),
  borrarHistorial: () => pedir('/historial', { method: 'DELETE' }),
};

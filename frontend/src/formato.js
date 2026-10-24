// Formatea números para mostrarlos (máx. 4 decimales, sin ceros de más).
export function num(x, d = 4) {
  if (x === null || x === undefined || Number.isNaN(x)) return '—';
  const r = Number(x).toFixed(d);
  return r.includes('.') ? r.replace(/0+$/, '').replace(/\.$/, '') : r;
}

// Convierte texto pegado ("45, 52 38;61\n47") en lista de números.
export function parsearDatos(texto) {
  let t = texto;
  if (t.includes(';') && /\d,\d/.test(t)) t = t.replace(/,/g, '.');
  return (t.match(/-?\d+(?:\.\d+)?/g) || []).map(Number);
}

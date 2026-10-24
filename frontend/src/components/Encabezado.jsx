const VISTAS = [
  ['calculadora', 'Calculadora'],
  ['guardados', 'Guardados'],
  ['historial', 'Historial'],
];

export default function Encabezado({ vista, setVista, salud }) {
  let estado = { clase: 'gris', texto: 'Conectando…' };
  if (salud?.ok === false) estado = { clase: 'rojo', texto: 'Backend apagado' };
  else if (salud?.ia === 'gemini') estado = { clase: 'verde', texto: 'IA: Gemini' };
  else if (salud?.ia === 'local') estado = { clase: 'ambar', texto: 'IA: modo local' };

  return (
    <header className="encabezado">
      <div className="marca">
        <span className="logo">Σ</span>
        <div>
          <strong>Σstadi</strong>
          <small>Calculadora estadística con tutor IA</small>
        </div>
      </div>
      <nav className="nav">
        {VISTAS.map(([id, txt]) => (
          <button key={id} className={vista === id ? 'activo' : ''} onClick={() => setVista(id)}>
            {txt}
          </button>
        ))}
      </nav>
      <span className={`estado ${estado.clase}`} title={salud?.modelo || ''}>
        <i /> {estado.texto}
      </span>
    </header>
  );
}

// Muestra el procedimiento de cada medida: fórmula → sustitución → resultado.

function juntarSecciones(r) {
  const tc = r.tendencia_central;
  const d = r.dispersion;
  const p = r.posicion;
  const f = r.forma;
  const secciones = [];

  if (r.tipo === 'agrupados') {
    secciones.push(['Construcción de la tabla', r.pasos_construccion]);
  }
  secciones.push(['Media', tc.media.pasos]);
  secciones.push(['Mediana', tc.mediana.pasos]);
  if (r.tipo === 'agrupados') {
    tc.moda.valores.forEach((m, i) => secciones.push([`Moda${tc.moda.valores.length > 1 ? ` ${i + 1}` : ''}`, m.pasos]));
  } else {
    secciones.push(['Moda', tc.moda.pasos]);
    secciones.push(['Media geométrica', tc.media_geometrica.pasos]);
    secciones.push(['Media armónica', tc.media_armonica.pasos]);
  }
  secciones.push(['Varianza', d.varianza.pasos]);
  secciones.push(['Desviación estándar', d.desviacion.pasos]);
  secciones.push(['Coeficiente de variación', d.coeficiente_variacion.pasos]);
  secciones.push(['Desviación media', d.desviacion_media.pasos]);
  if (d.error_estandar) secciones.push(['Error estándar', d.error_estandar.pasos]);
  p.cuartiles.forEach((q) => secciones.push([`Cuartil Q${q.k}`, q.pasos]));
  p.deciles.forEach((q) => secciones.push([`Decil D${q.k}`, q.pasos]));
  p.percentiles.forEach((q) => secciones.push([`Percentil P${q.k}`, q.pasos]));
  secciones.push(['Rango intercuartil', d.rango_intercuartil.pasos]);
  Object.values(f).forEach((m) => secciones.push([m.pasos[0].titulo, m.pasos]));
  return secciones;
}

export default function Procedimiento({ resultado }) {
  const secciones = juntarSecciones(resultado);
  return (
    <div className="tarjeta procedimiento">
      <h3>Procedimiento paso a paso</h3>
      <p className="ayuda">Así lo resolverías a mano en el examen. Toca cada medida para ver el desarrollo.</p>
      {secciones.map(([titulo, pasos], i) => (
        <details key={i} open={i < 2}>
          <summary>{titulo}</summary>
          <ol>
            {pasos.map((s, j) => (
              <li key={j}>
                {pasos.length > 1 && <span className="paso-titulo">{s.titulo}</span>}
                <code className="formula">{s.formula}</code>
                {s.sustitucion && <code className="sustitucion">{s.sustitucion}</code>}
                {s.resultado && <strong className="res">{s.resultado}</strong>}
              </li>
            ))}
          </ol>
        </details>
      ))}
    </div>
  );
}

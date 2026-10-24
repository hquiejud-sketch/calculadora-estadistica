import { num } from '../formato.js';

export default function Medidas({ resultado: r }) {
  const agrupados = r.tipo === 'agrupados';
  const tc = r.tendencia_central;
  const d = r.dispersion;
  const p = r.posicion;
  const f = r.forma;

  const modas = agrupados
    ? tc.moda.valores.map((m) => num(m.valor)).join(' / ')
    : tc.moda.valores.length ? tc.moda.valores.map((m) => num(m)).join(' / ') : 'No hay';

  return (
    <div className="grid-medidas">
      <Grupo titulo="Tendencia central" color="c1">
        <Fila n="Media (x̄)" v={tc.media.valor} />
        <Fila n="Mediana (Me)" v={tc.mediana.valor} />
        <Fila n={`Moda (${tc.moda.tipo})`} texto={modas} />
        {!agrupados && <Fila n="Media geométrica" v={tc.media_geometrica.valor} />}
        {!agrupados && <Fila n="Media armónica" v={tc.media_armonica.valor} />}
      </Grupo>

      <Grupo titulo="Dispersión" color="c2">
        <Fila n="Rango (R)" v={d.rango.valor} />
        <Fila n="Varianza muestral (s²)" v={d.varianza.valor} />
        <Fila n="Varianza poblacional (σ²)" v={d.varianza.poblacional} />
        <Fila n="Desviación muestral (s)" v={d.desviacion.valor} />
        <Fila n="Desviación poblacional (σ)" v={d.desviacion.poblacional} />
        <Fila n="Desviación media (DM)" v={d.desviacion_media.valor} />
        <Fila n="Coef. de variación (CV)" texto={d.coeficiente_variacion.valor === null ? '—' : `${num(d.coeficiente_variacion.valor, 2)} %`}
          nota={d.coeficiente_variacion.interpretacion} />
        <Fila n="Rango intercuartil (RIC)" v={d.rango_intercuartil.valor} />
        {!agrupados && <Fila n="Error estándar (EE)" v={d.error_estandar.valor} />}
      </Grupo>

      <Grupo titulo="Posición" color="c3">
        {p.cuartiles.map((q) => <Fila key={`q${q.k}`} n={`Cuartil Q${q.k}`} v={q.valor} />)}
        {p.deciles.map((q) => <Fila key={`d${q.k}`} n={`Decil D${q.k}`} v={q.valor} />)}
        {p.percentiles.map((q) => <Fila key={`p${q.k}`} n={`Percentil P${q.k}`} v={q.valor} />)}
      </Grupo>

      <Grupo titulo="Forma" color="c4">
        <Fila n="Asimetría de Pearson" v={f.asimetria_pearson.valor} nota={f.asimetria_pearson.interpretacion} />
        {f.asimetria_bowley && <Fila n="Asimetría de Bowley" v={f.asimetria_bowley.valor} nota={f.asimetria_bowley.interpretacion} />}
        <Fila n="Asimetría de Fisher (g1)" v={f.asimetria_fisher.valor} nota={f.asimetria_fisher.interpretacion} />
        <Fila n="Curtosis (g2)" v={f.curtosis.valor} nota={f.curtosis.interpretacion} />
        {f.curtosis_percentilica && <Fila n="Curtosis percentílica (K)" v={f.curtosis_percentilica.valor} nota={f.curtosis_percentilica.interpretacion} />}
      </Grupo>

      {!agrupados && (
        <Grupo titulo="Datos atípicos (criterio 1.5·RIC)" color="c5">
          <Fila n="Cerca inferior" v={r.caja.limite_inferior} />
          <Fila n="Cerca superior" v={r.caja.limite_superior} />
          <Fila n="Atípicos" texto={r.caja.atipicos.length ? r.caja.atipicos.map((x) => num(x)).join(', ') : 'Ninguno'} />
        </Grupo>
      )}
    </div>
  );
}

function Grupo({ titulo, color, children }) {
  return (
    <div className={`tarjeta grupo ${color}`}>
      <h3>{titulo}</h3>
      <dl>{children}</dl>
    </div>
  );
}

function Fila({ n, v, texto, nota }) {
  return (
    <div className="fila-medida">
      <dt>{n}{nota && <small>{nota}</small>}</dt>
      <dd>{texto ?? num(v)}</dd>
    </div>
  );
}

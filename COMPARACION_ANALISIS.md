# COMPARACIÓN: Análisis Completo vs DTE >= 10 días

## Resumen Ejecutivo

Se realizaron dos análisis predictivos del CSV de Calendar Spreads:
1. **Análisis Completo**: 20,745 registros (todos los spreads)
2. **Análisis DTE >= 10**: 6,719 registros (solo spreads con diferencia temporal >= 10 días)

## 📊 Tamaño de Muestra

| Métrica | Completo | DTE >= 10 | Diferencia |
|---------|----------|-----------|------------|
| **N total** | 20,745 | 6,719 | -67.6% |
| **N válido (50%)** | 20,408 | 6,624 | -67.5% |
| **N válido (90%)** | 20,408 | 6,624 | -67.5% |
| **Período** | 2019-2025 | 2019-2025 | Mismo |

## 🎯 Target: PnL_fwd_pts_50_mediana

### Correlaciones Top 3 (Spearman)

| Ranking | Completo | r | DTE >= 10 | r | Mejora |
|---------|----------|---|-----------|---|--------|
| 1 | SPX_BB_Width | 0.139 | **SPX_SMA50_200_Diff** | **-0.179** | ✅ +29% |
| 2 | theta_total | 0.136 | **SPX_minus_SMA200** | **-0.176** | ✅ +29% |
| 3 | PnLPICO | 0.120 | **SPX_BB_Width** | **0.159** | ✅ +15% |

**🔥 Hallazgo clave**: Con DTE >= 10, las correlaciones mejoran y emergen nuevas features relacionadas con SMAs del SPX.

### Reglas por Quintiles - Mejores Δ Mediana

| Análisis | Feature | Δ Mediana | Cliff's δ |
|----------|---------|-----------|-----------|
| Completo | SPX_SMA100 | 1.70 pts | 0.305 |
| **DTE >= 10** | **SPX_BB_Upper** | **3.42 pts** | **0.232** |

**Interpretación**: Spreads con DTE >= 10 muestran mayor sensibilidad al nivel del SPX (bandas de Bollinger, SMAs).

### Feature Engineering - Top Ratios

| Análisis | Feature Derivada | r_Spearman |
|----------|------------------|------------|
| Completo | (transformaciones) | ~0.14 |
| **DTE >= 10** | **SPX_SMA50_200_Diff / SPX_EMA200** | **-0.239** |
| **DTE >= 10** | **SPX_SMA50_200_Diff / SPX_BB_Upper** | **-0.231** |

**🚀 Hallazgo**: Los ratios entre diferencial de SMAs y niveles de precio muestran correlaciones más fuertes (+71%).

### VIX

| Análisis | VIX Cliff's δ | p-value | Conclusión |
|----------|---------------|---------|------------|
| Completo | 0.099 | 0.0000 | Señal débil |
| DTE >= 10 | 0.044 | 0.0534 | **No significativo** |

**Interpretación**: VIX pierde poder predictivo para el target de 50% con spreads largos.

### Validación OOS

| Análisis | Modelo | Spearman OOS | Conclusión |
|----------|--------|--------------|------------|
| Completo | Ridge | 0.028 ± 0.109 | ❌ No predictivo |
| Completo | Lasso | -0.010 ± 0.124 | ❌ No predictivo |
| DTE >= 10 | Ridge | -0.058 ± 0.225 | ❌ No predictivo |
| DTE >= 10 | Lasso | **0.005 ± 0.234** | ❌ No predictivo |

**⚠️ Conclusión crítica**: Aunque las correlaciones in-sample mejoran, **NO se traduce en poder predictivo OOS**.

---

## 🎯 Target: PnL_fwd_pts_90_mediana

### Correlaciones Top 3 (Spearman)

| Ranking | Completo | r | DTE >= 10 | r | Mejora |
|---------|----------|---|-----------|---|--------|
| 1 | SPX_minus_SMA100 | 0.182 | **SPX_HV20** | **-0.191** | ✅ +5% |
| 2 | SPX_HV20 | -0.170 | **SPX_BB_Middle** | **0.142** | - |
| 3 | SPX_minus_SMA50 | 0.166 | **SPX_SMA20** | **0.142** | - |

**Cambio clave**: Con DTE >= 10, la volatilidad histórica (HV20) se vuelve el predictor #1.

### Reglas por Quintiles - Mejores Δ Mediana

| Análisis | Feature | Δ Mediana | Cliff's δ | Impacto |
|----------|---------|-----------|-----------|---------|
| Completo | iv_k2 | -3.54 pts | -0.306 | - |
| **DTE >= 10** | **SPX_BB_Upper** | **+14.43 pts** | **0.380** | 🔥 **+308%** |
| **DTE >= 10** | **SPX_MACD_Signal** | **+8.75 pts** | **0.315** | 🔥 **+147%** |

**🔥🔥🔥 HALLAZGO CRÍTICO**:

Con spreads DTE >= 10, el quintil superior de SPX_BB_Upper vs el inferior muestra una diferencia de **14.43 puntos** en la mediana del PnL a 90% DTE (Cliff's δ = 0.38 = efecto GRANDE).

**Interpretación práctica**:
- Cuando SPX está en el quintil superior de su Banda de Bollinger superior → PnL mediano = **+7.60 pts**
- Cuando SPX está en el quintil inferior → PnL mediano = **-6.83 pts**
- **Diferencia = 14.43 pts** (efecto muy fuerte in-sample)

### VIX

| Análisis | Δ Mediana (Q5 vs Q1) | Cliff's δ | p-value |
|----------|----------------------|-----------|---------|
| Completo | -3.51 pts | -0.280 | 0.0000 |
| **DTE >= 10** | **-7.38 pts** | **-0.202** | **0.0000** |

**Interpretación**: Con DTE >= 10, VIX alto (Q5) produce peores resultados (-7.38 pts vs -3.51 pts). El efecto se duplica.

### Feature Engineering - Top Ratios

| Análisis | Feature Derivada | r_Spearman |
|----------|------------------|------------|
| Completo | SPX_minus_SMA100 / SPX_minus_SMA50 | 0.201 |
| **DTE >= 10** | **SPX_HV20 / SPX_EMA12** | **-0.210** |
| **DTE >= 10** | **SPX_HV20 / SPX_BB_Middle** | **-0.209** |

**Hallazgo**: El ratio de volatilidad histórica vs nivel de precio es el predictor derivado más fuerte.

### Validación OOS

| Análisis | Modelo | Spearman OOS | Conclusión |
|----------|--------|--------------|------------|
| Completo | Ridge | -0.054 ± 0.183 | ❌ No predictivo |
| Completo | Lasso | -0.043 ± 0.198 | ❌ No predictivo |
| DTE >= 10 | Ridge | -0.000 ± 0.194 | ❌ No predictivo |
| DTE >= 10 | Lasso | **0.036 ± 0.258** | ❌ No predictivo |

**⚠️ Conclusión crítica**: A pesar de los efectos in-sample muy fuertes (Cliff's δ = 0.38), **NO hay poder predictivo OOS consistente**.

---

## 🎓 CONCLUSIONES FINALES

### ✅ Lo que MEJORÓ con filtro DTE >= 10:

1. **Correlaciones in-sample más fuertes**: +5% a +29% dependiendo del target
2. **Tamaños de efecto mayores**:
   - PnL_50: Δ mediana de 3.42 pts (vs 1.70)
   - PnL_90: Δ mediana de 14.43 pts (vs 3.54) → **+308%**
3. **Features más relevantes**:
   - Nivel de SPX (BB_Upper, SMAs) se vuelve crítico
   - Volatilidad histórica (HV20, HV50) muestra relaciones más claras
4. **Feature engineering más efectivo**: Ratios llegan a -0.239 (vs -0.20 antes)

### ❌ Lo que NO cambió (problemas persistentes):

1. **Validación OOS sigue fallando**: Spearman ≈ 0 en todos los modelos
2. **Inestabilidad temporal**: Alta varianza en folds (±0.23 a ±0.26)
3. **Sobreajuste evidente**: Brecha enorme entre in-sample y OOS

### 🤔 Interpretación Honesta

**In-sample (dentro de la muestra)**:
- ✅ Existen relaciones estadísticas significativas y de efecto grande
- ✅ SPX_BB_Upper con Cliff's δ = 0.38 es un efecto "grande" según estándares
- ✅ Las reglas por quintiles son robustas estadísticamente (p < 0.0001)

**Out-of-sample (lo que importa para trading)**:
- ❌ Las relaciones NO generalizan a datos nuevos
- ❌ Los modelos NO pueden predecir mejor que azar
- ❌ NO hay "edge" explotable estadísticamente

### 🔍 Posibles Explicaciones

1. **No-estacionariedad**: Las relaciones cambian en el tiempo (régimen-dependiente)
2. **Muestra insuficiente**: 6,624 registros puede ser poco para capturar complejidad
3. **Features ruidosas**: Señal débil enterrada en ruido de mercado
4. **Horizonte temporal**: 90% DTE puede ser demasiado lejano para predecir con datos T+0
5. **Información ya incorporada**: El mercado ya precio estas relaciones (eficiencia)

### 💡 Recomendaciones para Próximos Pasos

Si deseas continuar explorando:

1. **Segmentación por régimen**:
   - Separar análisis por VIX alto/bajo
   - Por tendencia de SPX (alcista/bajista)
   - Por volatilidad histórica

2. **Horizontes más cortos**:
   - Analizar PnL a 25% DTE en vez de 50%/90%
   - Targets de 1-3 días en vez de medianas

3. **Análisis condicional**:
   - "Si SPX_BB_Upper > percentil 80 Y VIX < 15 → entonces..."
   - Reglas compuestas en vez de features individuales

4. **Walk-forward más estricto**:
   - Ventanas móviles de 6 meses
   - Re-calibración constante

5. **Factores macro**:
   - Añadir tasas de interés, curva de rendimientos
   - Eventos de Fed, earnings season

---

## 📝 Resumen Ultra-Breve

**¿Encontramos algo con DTE >= 10?**

✅ **Sí, in-sample**: Relaciones más fuertes (hasta Cliff's δ = 0.38)
❌ **No, OOS**: No se puede predecir mejor que azar

**¿Vale la pena?**

Para **investigación académica**: Interesante, hay patrones robustos
Para **trading sistemático**: No hay edge explotable con estos datos

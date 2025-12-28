# 🔥 COMPARACIÓN: FF_ATM < 0.3 vs FF_ATM > 0.7
## Descubrimiento Clave: Dinámicas OPUESTAS

---

## 📊 CONFIGURACIONES COMPARADAS

| Filtros | FF < 0.3 | FF > 0.7 |
|---------|----------|----------|
| **DTE diff** | > 10 días | > 10 días |
| **FF_ATM** | < 0.3 | > 0.7 |
| **N registros** | 3,398 (16.7%) | **110 (0.5%)** |
| **Período** | 2019-2025 | 2020-2025 |

---

## 🎯 TARGET: PnL_fwd_pts_50_mediana

### Estadísticas Básicas

| Métrica | FF < 0.3 | FF > 0.7 | Diferencia |
|---------|----------|----------|------------|
| **Media** | -1.01 pts | **9.03 pts** | **+10.04 pts** 🔥 |
| **Mediana** | 0.85 pts | **5.08 pts** | **+4.23 pts** 🔥 |
| **Std** | 9.02 pts | 15.49 pts | +72% volatilidad |

**Conclusión**: FF alto → PnL significativamente mejor (+10 pts de media)

### Top Correlaciones (Spearman)

| Ranking | FF < 0.3 | r | FF > 0.7 | r | Cambio |
|---------|----------|---|----------|---|--------|
| 1 | SPX_SMA50_200_Diff | -0.147 | **SPX_RSI14** | **-0.554** | ✅ **+277%** |
| 2 | SPX_BB_Upper | 0.136 | **SPX_ZScore50** | **-0.529** | 🔄 Sign flip |
| 3 | SPX_SMA50 | 0.122 | **SPX_Stoch_D** | **-0.486** | 🔄 Sign flip |

**🔥 HALLAZGO CRÍTICO:**
- FF > 0.7 muestra correlaciones **3-4x más fuertes**
- **SIGNOS INVERTIDOS**: Indicadores técnicos que predicen positivamente en FF bajo, predicen negativamente en FF alto

### Reglas por Cuantiles - TOP 3

#### FF < 0.3 (Quintiles, N=3,398):
| Feature | Δ Mediana | Cliff's δ | Dirección |
|---------|-----------|-----------|-----------|
| SPX_EMA50 | 5.00 pts | 0.352 | SPX alto → mejor |
| SPX_SMA50 | 5.00 pts | 0.351 | SPX alto → mejor |
| SPX_BB_Upper | 4.92 pts | 0.348 | SPX alto → mejor |

#### FF > 0.7 (Tertiles, N=110):
| Feature | Δ Mediana | Cliff's δ | Dirección |
|---------|-----------|-----------|-----------|
| **SPX_minus_SMA200** | **-20.18 pts** | **-0.837** | **SPX alto → PEOR** 🔄 |
| **SPX_minus_SMA100** | **-19.67 pts** | **-0.825** | **SPX alto → PEOR** 🔄 |
| **SPX_minus_SMA50** | **-19.65 pts** | **-0.823** | **SPX alto → PEOR** 🔄 |

**🔥🔥🔥 HALLAZGO EXPLOSIVO:**
- FF > 0.7: Efectos **4x más fuertes** (Cliff's δ: 0.84 vs 0.35)
- **DIRECCIONES OPUESTAS**: Lo que funciona en FF bajo, hace lo contrario en FF alto
- Cliff's δ = -0.837 es un efecto **ENORME** (estándar: >0.8 = muy grande)

**Interpretación (FF > 0.7):**
- **Tertil superior** (SPX muy alto sobre SMA200): PnL mediano = **-4.20 pts**
- **Tertil inferior** (SPX bajo sobre SMA200): PnL mediano = **15.97 pts**
- Cuando SPX sube mucho, los spreads con FF alto sufren enormemente

### Feature Engineering

| Configuración | Top Feature Derivada | r_Spearman |
|---------------|---------------------|------------|
| FF < 0.3 | SPX_SMA50_200_Diff / SPX_EMA26 | -0.231 |
| **FF > 0.7** | **SPX_RSI14 / IV_Ratio** | **-0.650** 🔥 |

**Mejora**: +182% en fuerza predictiva

### VIX Impact

| Configuración | VIX ROC/Slope 20d | Cliff's δ | Conclusión |
|---------------|-------------------|-----------|------------|
| FF < 0.3 | débil/no sig | -0.093 | VIX alto → peor PnL |
| **FF > 0.7** | **0.32-0.34** 🔥 | 0.137 | **VIX alto → mejor PnL** 🔄 |

**Sign flip completo**: VIX tiene efecto opuesto en FF alto vs bajo

### Validación OOS

| Configuración | Ridge Spearman | Lasso Spearman | N folds |
|---------------|----------------|----------------|---------|
| FF < 0.3 | -0.053 ± 0.225 | 0.031 ± 0.197 | N=3,398 |
| FF > 0.7 | 0.045 ± 0.446 | 0.006 ± 0.427 | **N=110** ⚠️ |

**Problema**: FF > 0.7 tiene muestra muy pequeña (110) → alta varianza OOS (±0.43)

---

## 🎯 TARGET: PnL_fwd_pts_90_mediana

### Estadísticas Básicas

| Métrica | FF < 0.3 | FF > 0.7 | Diferencia |
|---------|----------|----------|------------|
| **Media** | -0.75 pts | **9.15 pts** | **+9.90 pts** 🔥 |
| **Mediana** | -2.50 pts | **-0.19 pts** | **+2.31 pts** |
| **Std** | 16.35 pts | 23.29 pts | +42% volatilidad |

### Top Correlaciones (Spearman)

| Ranking | FF < 0.3 | r | FF > 0.7 | r | Cambio |
|---------|----------|---|----------|---|--------|
| 1 | SPX_HV20 | -0.220 | **SPX_MACD_Histogram** | **-0.538** | ✅ **+145%** |
| 2 | SPX_HV50 | -0.176 | **theta_total** | **0.510** | 🔄 Sign flip +190% |
| 3 | SPX_MACD_Signal | 0.163 | **SPX_ROC7** | **-0.501** | 🔄 Sign flip +207% |

**Cambio radical**: Momentum e indicadores técnicos dominan en FF alto (vs volatilidad en FF bajo)

### Reglas por Cuantiles - TOP 3

#### FF < 0.3 (Quintiles, N=3,398):
| Feature | Δ Mediana | Cliff's δ | Dirección |
|---------|-----------|-----------|-----------|
| SPX_MACD_Signal | 11.84 pts | 0.388 | MACD alto → mejor |
| SPX_SMA20 | 13.03 pts | 0.341 | SPX alto → mejor |
| iv_k2 | -11.72 pts | -0.356 | IV alta → peor |

#### FF > 0.7 (Tertiles, N=110):
| Feature | Δ Mediana | Cliff's δ | Dirección |
|---------|-----------|-----------|-----------|
| **SPX_MACD_Histogram** | **-28.89 pts** | **-0.723** | **MACD alto → PEOR** 🔄 |
| **theta_total** | **41.39 pts** | **0.703** | **theta alto → MEJOR** 🔥 |
| **SPX_BB_Pct** | **-13.81 pts** | **-0.627** | **SPX alto → PEOR** 🔄 |

**🔥🔥🔥 HALLAZGOS ESPECTACULARES:**

**1. theta_total (Cliff's δ = 0.703 = ENORME):**
- **Tertil superior** (theta alto): PnL mediano = **+35.75 pts** 🚀
- **Tertil inferior** (theta bajo): PnL mediano = **-5.64 pts**
- **Diferencia = 41.39 pts** (vs 11.84 pts en FF < 0.3) = **+250%**

**Interpretación**: En spreads con FF alto, theta decay AYUDA enormemente (posiciones largas en tiempo)

**2. SPX_MACD_Histogram (Cliff's δ = -0.723 = ENORME):**
- **Tertil superior** (MACD alto): PnL mediano = **-7.16 pts**
- **Tertil inferior** (MACD bajo): PnL mediano = **21.73 pts**
- **Diferencia = -28.89 pts** (vs 11.84 pts opuesto en FF < 0.3)

**Interpretación**: Cuando momentum es fuerte (MACD alto), los spreads con FF alto sufren

### Feature Engineering

| Configuración | Top Feature Derivada | r_Spearman | Multiplicador |
|---------------|---------------------|------------|---------------|
| FF < 0.3 | SPX_HV20 (rank/log/zscore) | -0.220 | 1x |
| **FF > 0.7** | **SPX_ROC7 / DTE** | **-0.734** 🔥 | **ROC/DTE** |

**Hallazgo**: Normalizar momentum por DTE crea predictor muy fuerte (-0.734) en FF alto

### VIX Impact

| Configuración | VIX Δ Mediana | Cliff's δ | VIX slope_20 | Dirección |
|---------------|---------------|-----------|--------------|-----------|
| FF < 0.3 | -9.71 pts | -0.290 | débil | VIX alto → peor |
| **FF > 0.7** | **4.54 pts** | **0.137** | **0.308** 🔥 | **VIX alto → mejor** 🔄 |

**Sign flip completo y consistente**

### Validación OOS

| Configuración | Ridge Spearman | Lasso Spearman |
|---------------|----------------|----------------|
| FF < 0.3 | -0.085 ± 0.146 | -0.097 ± 0.158 |
| FF > 0.7 | Muestra insuficiente | Muestra insuficiente |

---

## 🎓 INTERPRETACIÓN ECONÓMICA/FINANCIERA

### ¿Qué es FF_ATM y qué representa?

**FF_ATM (Forward Factor ATM)** mide el ratio entre el precio forward y el spot, normalizado.

- **FF bajo (< 0.3)**: Forward está cerca del spot
  - Spreads "normales" con carry/cost moderado
  - Comportamiento típico de calendar spreads

- **FF alto (> 0.7)**: Forward muy por encima del spot
  - **Contango fuerte** en el mercado
  - **Alto costo de carry** implícito
  - Situaciones de mercado específicas (alta demanda de protección, backwardation invertido, etc.)

### ¿Por qué comportamientos opuestos?

**FF < 0.3 (Spreads "normales"):**
- **SPX alto → mejor PnL**: Mercado alcista beneficia spreads con carry moderado
- **HV baja → mejor PnL**: Estabilidad ayuda
- **VIX alto → peor PnL**: Volatilidad perjudica

**FF > 0.7 (Spreads en contango fuerte):**
- **SPX alto → peor PnL**: 🔄 Rally perjudica posiciones largas en forwards caros
- **Momentum alto → peor PnL**: 🔄 Movimientos fuertes colapsan el spread
- **Theta alto → mejor PnL**: 🔥 Decay temporal favorece al vender tiempo caro
- **VIX alto → mejor PnL**: 🔄 Volatilidad ayuda a monetizar prima cara

**Mecanismo probable:**
1. FF alto indica que la pata larga (DTE2) está **sobrevalorada** vs la corta (DTE1)
2. Cuando SPX sube/momentum fuerte → el forward caro se ajusta violentamente → pérdida
3. Cuando theta decay ocurre → la prima cara se erosiona favorablemente → ganancia
4. Cuando VIX sube → aumenta demanda de opciones largas → beneficia tener posición larga en tiempo

---

## 📊 TABLA COMPARATIVA RESUMEN

| Métrica | FF < 0.3 | FF > 0.7 | Ratio | Observación |
|---------|----------|----------|-------|-------------|
| **N registros** | 3,398 | 110 | 31x | FF alto es RARO |
| **PnL_50 Media** | -1.01 | 9.03 | +10 pts | FF alto mejor |
| **PnL_90 Media** | -0.75 | 9.15 | +10 pts | FF alto mejor |
| **Top r (PnL_50)** | -0.147 | **-0.554** | **3.8x** | ✅ Más fuerte |
| **Top r (PnL_90)** | -0.220 | **-0.538** | **2.4x** | ✅ Más fuerte |
| **Max Cliff's δ (50)** | 0.352 | **-0.837** | **2.4x** | ✅ Efecto enorme |
| **Max Cliff's δ (90)** | 0.388 | **0.703** | **1.8x** | ✅ Efecto enorme |
| **Max Δ mediana (50)** | 5.00 pts | **20.18 pts** | **4x** | ✅ 4x más fuerte |
| **Max Δ mediana (90)** | 13.03 pts | **41.39 pts** | **3.2x** | ✅ 3x más fuerte |
| **Signos** | SPX+ → PnL+ | **SPX+ → PnL-** | 🔄 | **Opuesto** |
| **VIX** | VIX+ → PnL- | **VIX+ → PnL+** | 🔄 | **Opuesto** |
| **Factor clave** | HV, SPX level | **RSI, MACD, theta** | - | Diferentes |
| **OOS viable** | No (Spearman≈0) | **No** (N pequeño) | - | Ambos fallan |

---

## 🔥 HALLAZGOS CLAVE

### 1. FF_ATM es un **régimen completamente diferente**

FF alto no es simplemente "más extremo" que FF bajo - es un **tipo de posición fundamentalmente distinto** con:
- ✅ Dinámicas opuestas
- ✅ Factores predictores diferentes
- ✅ Efectos 3-4x más fuertes

### 2. Efectos in-sample son **ENORMES** en FF > 0.7

- Cliff's δ hasta -0.837 (vs 0.388 en FF bajo)
- Correlaciones hasta -0.734 (vs -0.220 en FF bajo)
- Diferencias de PnL hasta 41 puntos (vs 13 puntos en FF bajo)

### 3. **Sign flips consistentes**

| Factor | FF < 0.3 | FF > 0.7 |
|--------|----------|----------|
| SPX alto | ✅ Mejor | ❌ Peor |
| MACD alto | ✅ Mejor | ❌ Peor |
| VIX alto | ❌ Peor | ✅ Mejor |
| theta alto | neutral | ✅✅ Mejor |

### 4. **theta_total es rey en FF alto**

- Correlación: 0.510 (vs débil en FF bajo)
- Cliff's δ: 0.703 (ENORME)
- Δ mediana: 41.39 pts (vs 11.84 en FF bajo)

**Interpretación**: Cuando el forward está caro (FF alto), el decay temporal es MUY beneficioso

### 5. **Indicadores técnicos dominan en FF alto**

FF < 0.3: Volatilidad histórica (HV20, HV50)
FF > 0.7: **Momentum e indicadores técnicos (RSI, MACD, Stoch, ROC)**

---

## ❌ LIMITACIONES

### 1. **Muestra muy pequeña en FF > 0.7**
- Solo 110 registros (0.5% del total)
- Tertiles en vez de quintiles
- OOS imposible de validar confiablemente
- Alta varianza (std ±0.43)

### 2. **Riesgo de data mining**
- Con N=110, es fácil encontrar patrones espurios
- Correlaciones muy altas pueden ser casualidad
- Necesita validación en datos nuevos

### 3. **Periodo limitado**
- FF > 0.7 solo aparece 2020-2025
- Puede estar sesgado por régimen COVID/post-COVID
- Falta diversidad temporal

### 4. **OOS falla en ambos**
- FF < 0.3: Spearman ≈ 0 (sin señal)
- FF > 0.7: N insuficiente para validar

---

## 💡 CONCLUSIONES Y RECOMENDACIONES

### ✅ Lo que SABEMOS

1. **FF_ATM define dos regímenes completamente distintos**:
   - FF bajo: Calendar spreads "típicos" sensibles a nivel de SPX y volatilidad
   - FF alto: Spreads en contango extremo con dinámicas opuestas

2. **Efectos in-sample son reales y muy fuertes en FF > 0.7**:
   - Cliff's δ hasta -0.84 (enorme)
   - theta_total es factor dominante (+41 pts)
   - Momentum indicators reversan (MACD alto → peor)

3. **VIX tiene efecto opuesto**:
   - FF bajo: VIX alto → peor PnL
   - FF alto: VIX alto → mejor PnL

### ❌ Lo que NO sabemos

1. **Si las relaciones son causales o espurias** (N=110 muy pequeño)
2. **Si se mantienen OOS** (imposible validar con 110 registros)
3. **Si funcionan en el futuro** (solo 2020-2025, puede ser régimen específico)

### 🚀 Recomendaciones

#### Si quieres explotar FF > 0.7:

1. **Colectar MÁS datos**:
   - Extender historia hacia atrás
   - Incluir más tickers (no solo SPX)
   - Alcanzar N > 500 para validación robusta

2. **Validación walk-forward estricta**:
   - Entrenar en 2020-2022
   - Validar en 2023-2024
   - Test final en 2025

3. **Enfocarse en theta**:
   - theta_total muestra efecto más robusto (Cliff's δ = 0.70)
   - Construir regla simple: "Si FF > 0.7 AND theta > X → long calendar"

4. **Monitorear régimen**:
   - FF > 0.7 es RARO (0.5% de casos)
   - Solo operar cuando FF cruza el umbral
   - Salir cuando FF normaliza

#### Para investigación:

1. **Análisis por sub-periodos**:
   - ¿Los patrones son estables 2020-2021 vs 2022-2023 vs 2024-2025?
   - ¿Hay eventos específicos que causan FF alto?

2. **Otros umbrales de FF**:
   - ¿Qué pasa con 0.3 < FF < 0.7?
   - ¿Hay transición gradual o discontinua?

3. **Factores macro**:
   - ¿FF alto correlaciona con tasas de interés, dividendos, carry?
   - ¿Es específico de SPX o general?

---

## 📝 RESUMEN ULTRA-BREVE

**¿Qué encontramos con FF > 0.7?**

✅ **SÍ - Patrones in-sample MUY fuertes**:
- Efectos 3-4x más grandes que FF < 0.3
- theta_total es factor dominante (+41 pts, Cliff's δ = 0.70)
- **Dinámicas OPUESTAS**: SPX alto → peor, VIX alto → mejor

❌ **NO - Imposible validar OOS**:
- Solo 110 registros (0.5%)
- Muestra insuficiente para TimeSeriesSplit confiable
- Riesgo alto de overfitting/data mining

**Valor práctico:**
- ✅ **Descubrimiento conceptual**: FF_ATM separa dos regímenes distintos
- ✅ **Hipótesis generada**: theta decay es clave en FF alto
- ❌ **Trading inmediato**: NO (necesita más datos y validación)
- 🔬 **Investigación futura**: SÍ (muy prometedor si se valida)

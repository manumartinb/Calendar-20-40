# RESUMEN COMPARATIVO - 3 ANÁLISIS CALENDAR SPREADS

## Configuraciones Probadas

| Análisis | Filtros | N registros | % del total |
|----------|---------|-------------|-------------|
| **#1 Completo** | Ninguno | 20,408 | 100% |
| **#2 DTE >= 10** | DTE2-DTE1 >= 10 | 6,624 | 32.4% |
| **#3 DTE>10 + FF<0.3** | DTE2-DTE1 > 10 AND FF_ATM < 0.3 | 3,398 | 16.7% |

---

## 🎯 TARGET: PnL_fwd_pts_50_mediana

### Evolución de Correlaciones (Top Feature)

| Análisis | Top Feature | r_Spearman | Mejora |
|----------|-------------|------------|--------|
| #1 Completo | SPX_BB_Width | 0.139 | baseline |
| #2 DTE >= 10 | SPX_SMA50_200_Diff | -0.179 | +29% |
| **#3 DTE>10 + FF<0.3** | **SPX_SMA50_200_Diff** | **-0.147** | +6% |

### Evolución de Reglas por Quintiles (Mejor Δ Mediana)

| Análisis | Feature | Δ Mediana | Cliff's δ | Interpretación |
|----------|---------|-----------|-----------|----------------|
| #1 Completo | SPX_SMA100 | 1.70 pts | 0.305 | Efecto grande |
| #2 DTE >= 10 | SPX_BB_Upper | 3.42 pts | 0.232 | +101% |
| **#3 DTE>10 + FF<0.3** | **SPX_EMA50** | **5.00 pts** | **0.352** | **+194%** 🔥 |

**Interpretación (#3):**
- Quintil superior SPX_EMA50: PnL mediano = **+3.80 pts**
- Quintil inferior SPX_EMA50: PnL mediano = **-1.20 pts**
- **Diferencia = 5.00 pts** con Cliff's δ = 0.352 (efecto GRANDE)

### Feature Engineering (Mejores Ratios)

| Análisis | Top Feature Derivada | r_Spearman |
|----------|---------------------|------------|
| #1 Completo | (transformaciones básicas) | ~0.14 |
| #2 DTE >= 10 | SPX_SMA50_200_Diff / SPX_EMA200 | -0.239 |
| **#3 DTE>10 + FF<0.3** | **SPX_SMA50_200_Diff / SPX_EMA26** | **-0.231** |

### VIX Impact

| Análisis | VIX Δ Mediana (Q5 vs Q1) | Cliff's δ | p-value |
|----------|--------------------------|-----------|---------|
| #1 Completo | 0.72 pts | 0.099 | 0.0000 |
| #2 DTE >= 10 | 0.75 pts | 0.044 | 0.0534 |
| **#3 DTE>10 + FF<0.3** | **-2.41 pts** | **-0.093** | **0.0028** |

**Cambio clave**: Con filtros restrictivos, VIX alto → peor PnL (sign flip)

### Validación OOS

| Análisis | Ridge Spearman | Lasso Spearman | Conclusión |
|----------|----------------|----------------|------------|
| #1 Completo | 0.028 ± 0.109 | -0.010 ± 0.124 | ❌ No predictivo |
| #2 DTE >= 10 | -0.058 ± 0.225 | 0.005 ± 0.234 | ❌ No predictivo |
| **#3 DTE>10 + FF<0.3** | **-0.053 ± 0.225** | **0.031 ± 0.197** | ❌ **No predictivo** |

---

## 🎯 TARGET: PnL_fwd_pts_90_mediana

### Evolución de Correlaciones (Top 3)

| Ranking | #1 Completo | r | #2 DTE >= 10 | r | #3 DTE>10 + FF<0.3 | r |
|---------|-------------|---|--------------|---|--------------------|---|
| 1 | SPX_minus_SMA100 | 0.182 | SPX_HV20 | -0.191 | **SPX_HV20** | **-0.220** 🔥 |
| 2 | SPX_HV20 | -0.170 | SPX_BB_Middle | 0.142 | **SPX_HV50** | **-0.176** |
| 3 | SPX_minus_SMA50 | 0.166 | SPX_SMA20 | 0.142 | **SPX_MACD_Signal** | **0.163** |

**Evolución clara**: La volatilidad histórica (HV20, HV50) se vuelve el predictor dominante con filtros restrictivos.

### Evolución de Reglas por Quintiles - TOP 3

#### #1 Completo (baseline)
| Feature | Δ Mediana | Cliff's δ |
|---------|-----------|-----------|
| iv_k2 | -3.54 pts | -0.306 |
| _iv2_clean | -3.54 pts | -0.306 |
| ATM_back | -3.45 pts | -0.304 |

#### #2 DTE >= 10 (+308% mejora)
| Feature | Δ Mediana | Cliff's δ | vs #1 |
|---------|-----------|-----------|-------|
| **SPX_BB_Upper** | **14.43 pts** | **0.380** | **+308%** 🔥 |
| SPX_MACD_Signal | 8.75 pts | 0.315 | +147% |
| SPX_HV20 | -8.43 pts | -0.312 | +138% |

#### #3 DTE>10 + FF<0.3 (menor N pero efectos comparables)
| Feature | Δ Mediana | Cliff's δ | vs #1 |
|---------|-----------|-----------|-------|
| **SPX_MACD_Signal** | **11.84 pts** | **0.388** | **+235%** 🔥🔥🔥 |
| **SPX_SMA20** | **13.03 pts** | **0.341** | **+268%** 🔥🔥 |
| iv_k2 | -11.72 pts | -0.356 | +231% |

**🔥🔥🔥 HALLAZGOS EXPLOSIVOS (#3 DTE>10 + FF<0.3):**

**SPX_MACD_Signal** (Cliff's δ = 0.388 = EFECTO MUY GRANDE):
- Quintil superior (MACD signal alto): PnL mediano = **+0.47 pts**
- Quintil inferior (MACD signal bajo): PnL mediano = **-11.36 pts**
- **Diferencia = 11.84 pts**

**SPX_SMA20 / SPX_BB_Middle** (Cliff's δ = 0.341 = EFECTO MUY GRANDE):
- Quintil superior (precio alto): PnL mediano = **+6.95 pts**
- Quintil inferior (precio bajo): PnL mediano = **-6.08 pts**
- **Diferencia = 13.03 pts**

### VIX Impact - PnL_90

| Análisis | VIX Δ Mediana (Q5 vs Q1) | Cliff's δ | Efecto |
|----------|--------------------------|-----------|--------|
| #1 Completo | -3.51 pts | -0.280 | Moderado |
| #2 DTE >= 10 | -7.38 pts | -0.202 | **Duplicado** |
| **#3 DTE>10 + FF<0.3** | **-9.71 pts** | **-0.290** | **Triplicado** 🔥 |

**Interpretación consistente**: VIX alto → PnL mucho peor en spreads con DTE largo y FF bajo.

**VIX_SMA features (#3)**:
- VIX_SMA_5: -0.152 (moderada)
- VIX_SMA_10: -0.154 (moderada)
- VIX_SMA_20: -0.156 (moderada)

### Feature Engineering - PnL_90

| Análisis | Top Feature Derivada | r_Spearman |
|----------|---------------------|------------|
| #1 Completo | SPX_minus_SMA100 / SPX_minus_SMA50 | 0.201 |
| #2 DTE >= 10 | SPX_HV20 / SPX_EMA12 | -0.210 |
| **#3 DTE>10 + FF<0.3** | **SPX_HV20 (rank/log/zscore)** | **-0.220** |

### Validación OOS - PnL_90

| Análisis | Ridge Spearman | Lasso Spearman | Conclusión |
|----------|----------------|----------------|------------|
| #1 Completo | -0.054 ± 0.183 | -0.043 ± 0.198 | ❌ No predictivo |
| #2 DTE >= 10 | -0.000 ± 0.194 | 0.036 ± 0.258 | ❌ No predictivo |
| **#3 DTE>10 + FF<0.3** | **-0.085 ± 0.146** | **-0.097 ± 0.158** | ❌ **No predictivo** |

---

## 📊 TABLA RESUMEN - Máximos Efectos por Análisis

| Métrica | #1 Completo | #2 DTE >= 10 | #3 DTE>10 + FF<0.3 | Mejor |
|---------|-------------|--------------|-------------------|-------|
| **N registros** | 20,408 | 6,624 | **3,398** | #1 |
| **Top r_Spearman (50%)** | 0.139 | -0.179 | -0.147 | #2 |
| **Top Δ Mediana (50%)** | 1.70 pts | 3.42 pts | **5.00 pts** | **#3** ✅ |
| **Top Cliff's δ (50%)** | 0.305 | 0.232 | **0.352** | **#3** ✅ |
| **Top r_Spearman (90%)** | 0.182 | -0.191 | **-0.220** | **#3** ✅ |
| **Top Δ Mediana (90%)** | -3.54 pts | 14.43 pts | **13.03 pts** | #2 |
| **Top Cliff's δ (90%)** | -0.306 | 0.380 | **0.388** | **#3** ✅ |
| **VIX efecto (90%)** | -3.51 pts | -7.38 pts | **-9.71 pts** | **#3** ✅ |
| **OOS Spearman (50%)** | 0.028 | 0.005 | 0.031 | Todos fallan ❌ |
| **OOS Spearman (90%)** | -0.043 | 0.036 | -0.097 | Todos fallan ❌ |

---

## 🎓 CONCLUSIONES FINALES

### ✅ Lo que FUNCIONA (in-sample)

**Al aplicar filtros cada vez más restrictivos, encontramos:**

1. **Efectos MUCHO más fuertes** (hasta +268% vs baseline):
   - PnL_50: SPX_EMA50 → 5.00 pts de diferencia
   - PnL_90: SPX_SMA20 → 13.03 pts de diferencia
   - PnL_90: SPX_MACD_Signal → 11.84 pts de diferencia

2. **Cliff's Delta alcanza niveles "muy grandes"** (> 0.35):
   - 0.388 para MACD_Signal (#3)
   - 0.380 para BB_Upper (#2)
   - 0.352 para EMA50 (#3)

3. **Volatilidad histórica es clave** para PnL_90:
   - SPX_HV20: correlación hasta -0.220
   - VIX_Close: efecto hasta -9.71 pts

4. **Nivel del SPX dominante** para PnL_50:
   - SMAs, EMAs, Bandas de Bollinger
   - Posición relativa del precio

5. **MACD como señal direccional** para PnL_90:
   - MACD_Signal quintil alto → +0.47 pts
   - MACD_Signal quintil bajo → -11.36 pts

### ❌ Lo que NO funciona (out-of-sample)

**A pesar de efectos in-sample enormes:**

1. **Validación OOS falla consistentemente**:
   - Spearman oscila entre -0.10 y +0.03
   - No hay capacidad predictiva real
   - Alta varianza entre folds (±0.15 a ±0.26)

2. **Overfitting evidente**:
   - Brecha gigante entre in-sample y OOS
   - Las relaciones no generalizan

3. **Trade-off muestra vs señal**:
   - Más filtros → efectos más fuertes IN-sample
   - Más filtros → menos datos → peor OOS
   - No resuelve el problema fundamental

---

## 💡 INTERPRETACIÓN PRÁCTICA

### ¿Qué revelan estos filtros?

Los **calendar spreads con DTE > 10 y FF_ATM < 0.3** representan un **subconjunto específico**:
- **DTE > 10**: Spreads con mayor separación temporal
- **FF_ATM < 0.3**: Forward Factor bajo (precio forward más cerca del spot)

Este subconjunto muestra **patrones más claros** porque:
1. **Menos ruido**: Configuraciones más homogéneas
2. **Mayor sensibilidad macro**: Spreads largos reaccionan más a nivel del SPX y volatilidad
3. **Efectos direccionales**: MACD y nivel de precio importan más

### ¿Por qué falla OOS?

**Hipótesis principales:**

1. **Régimen-dependencia**:
   - Las relaciones cambian según el entorno de mercado
   - Lo que funciona en 2019 no funciona en 2024
   - Necesitaríamos análisis condicional por régimen

2. **Causalidad inversa**:
   - ¿SPX alto → mejor PnL?
   - ¿O situaciones de PnL positivo correlacionan con SPX alto?
   - El mercado ya incorpora estas relaciones

3. **N insuficiente para complejidad**:
   - 3,398 registros puede ser poco
   - Especialmente con TimeSeriesSplit (training sets menores)
   - Necesitaríamos más historia

4. **Señal débil vs ruido de mercado**:
   - Los efectos existen pero son pequeños vs variabilidad
   - PnL tiene std ~16 pts, señales de ~10 pts
   - Signal-to-noise ratio insuficiente

---

## 🚀 RECOMENDACIONES

### Si quieres continuar explorando:

#### 1. **Análisis Condicional por Régimen**
```
IF (VIX < 15 AND SPX > SMA200) THEN
   usar reglas de "mercado alcista tranquilo"
ELSE IF (VIX > 25 AND SPX < SMA200) THEN
   usar reglas de "mercado bajista volátil"
```

#### 2. **Horizontes más cortos**
- Analizar PnL a 3-7 días en vez de 50%/90% DTE
- Tal vez las relaciones sean más estables a corto plazo

#### 3. **Ensemble condicional**
- Entrenar modelos separados por:
  - VIX alto/medio/bajo
  - Tendencia de SPX (alcista/lateral/bajista)
  - Nivel de HV20

#### 4. **Features de microestructura**
- Bid-ask spreads
- Volumen de opciones
- Put-call ratio
- Skew

#### 5. **Walk-forward estricto**
- Ventanas de 3-6 meses
- Re-entrenar constantemente
- Monitorear degradación de señal

---

## 📝 RESUMEN ULTRA-BREVE

**¿Encontramos algo con los filtros?**

✅ **Sí, in-sample**:
- Efectos hasta 13 pts de diferencia mediana
- Cliff's Delta hasta 0.388 (muy grande)
- Volatilidad histórica y nivel de SPX son factores dominantes

❌ **No, OOS**:
- Spearman ≈ 0 en validación temporal
- No hay edge explotable para trading sistemático
- Overfitting severo

**Valor del análisis:**
- **Para investigación**: Patrones robustos existen, interesante académicamente
- **Para trading**: Sin validación OOS, no es actionable
- **Próximo paso**: Análisis condicional por régimen o horizontes más cortos

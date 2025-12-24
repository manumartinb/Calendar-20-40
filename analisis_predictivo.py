#!/usr/bin/env python3
"""
Análisis predictivo robusto para PnL_fwd_pts_50_mediana y PnL_fwd_pts_90_mediana
Con control anti-leakage, validación estadística y validación OOS
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import spearmanr, pearsonr
from sklearn.model_selection import TimeSeriesSplit, KFold
from sklearn.linear_model import Ridge, Lasso
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

# Configuración de visualización
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class RobustAnalyzer:
    """Analizador robusto con control de leakage y validación OOS"""

    def __init__(self, csv_path, targets, min_bin_size=30):
        self.csv_path = csv_path
        self.targets = targets
        self.min_bin_size = min_bin_size
        self.df = None
        self.features = None
        self.results = {}
        self.report = []

    def load_data(self):
        """Carga datos y realiza validaciones iniciales"""
        self.report.append("# ANÁLISIS PREDICTIVO - CALENDAR SPREADS\n")
        self.report.append("## 1. VALIDACIÓN INICIAL DE DATOS\n")

        # Cargar CSV
        self.df = pd.read_csv(self.csv_path)

        # Extraer DTE1 y DTE2 de la columna 'DTE1/DTE2' y aplicar filtros
        if 'DTE1/DTE2' in self.df.columns:
            dte_split = self.df['DTE1/DTE2'].str.split('/', expand=True)
            self.df['DTE1'] = pd.to_numeric(dte_split[0])
            self.df['DTE2'] = pd.to_numeric(dte_split[1])
            self.df['DTE_diff'] = self.df['DTE2'] - self.df['DTE1']

            # FILTROS: DTE_diff > 10 AND FF_ATM > 0.7
            N_original = len(self.df)

            # Aplicar filtro DTE
            filter_dte = self.df['DTE_diff'] > 10
            N_after_dte = filter_dte.sum()

            # Aplicar filtro FF_ATM
            filter_ff = self.df['FF_ATM'] > 0.7
            N_after_ff = filter_ff.sum()

            # Filtros combinados
            combined_filter = filter_dte & filter_ff
            self.df = self.df[combined_filter].copy()
            N_filtered = len(self.df)

            self.report.append(f"**FILTROS APLICADOS:**\n")
            self.report.append(f"1. DTE2 - DTE1 > 10 días: {N_after_dte:,} registros ({100*N_after_dte/N_original:.1f}%)\n")
            self.report.append(f"2. FF_ATM > 0.7: {N_after_ff:,} registros ({100*N_after_ff/N_original:.1f}%)\n")
            self.report.append(f"3. **COMBINADOS (1 AND 2): {N_filtered:,} registros ({100*N_filtered/N_original:.1f}%)**\n")
            self.report.append(f"- Registros originales: {N_original:,}\n")
            self.report.append(f"- Registros eliminados: {N_original - N_filtered:,}\n\n")

        N = len(self.df)

        self.report.append(f"**Tamaño muestral:** N = {N:,} registros\n")

        if N < 100:
            self.report.append("⚠️ **ADVERTENCIA:** N < 100, solo análisis descriptivo\n")
            return False

        # Info básica
        self.report.append(f"**Columnas totales:** {len(self.df.columns)}\n")
        self.report.append(f"**Período:** {self.df['dia'].min()} a {self.df['dia'].max()}\n\n")

        # Verificar targets
        for target in self.targets:
            if target not in self.df.columns:
                self.report.append(f"❌ ERROR: Target '{target}' no encontrado en el dataset\n")
                return False

            n_valid = self.df[target].notna().sum()
            self.report.append(f"**Target {target}:**\n")
            self.report.append(f"  - Valores válidos: {n_valid:,} ({100*n_valid/N:.1f}%)\n")
            self.report.append(f"  - Media: {self.df[target].mean():.2f}\n")
            self.report.append(f"  - Mediana: {self.df[target].median():.2f}\n")
            self.report.append(f"  - Std: {self.df[target].std():.2f}\n\n")

        return True

    def detect_leakage(self):
        """Detecta y excluye columnas con data leakage"""
        self.report.append("## 2. CONTROL ANTI-LEAKAGE\n")

        # Columnas a excluir
        leakage_patterns = ['fwd', 'chg']
        excluded = []

        for col in self.df.columns:
            col_lower = col.lower()

            # Excluir si contiene patrones de leakage (excepto targets)
            if col not in self.targets:
                if any(pattern in col_lower for pattern in leakage_patterns):
                    excluded.append(col)

        # Excluir también columnas obvias de información futura
        future_cols = ['dia_fwd_25', 'hora_fwd_25', 'dia_fwd_50', 'hora_fwd_50',
                      'dia_fwd_90', 'hora_fwd_90', 'net_debit_fwd_25', 'net_debit_fwd_50',
                      'net_debit_fwd_90']

        for col in future_cols:
            if col in self.df.columns and col not in excluded and col not in self.targets:
                excluded.append(col)

        self.report.append(f"**Columnas excluidas por leakage:** {len(excluded)}\n")
        self.report.append("```\n")
        for col in sorted(excluded):
            self.report.append(f"  - {col}\n")
        self.report.append("```\n\n")

        # Definir features permitidas
        all_cols = set(self.df.columns)
        excluded_set = set(excluded + self.targets + ['dia', 'hora', 'hora_us', 'right',
                                                       'date_us', 'exp1', 'exp2'])
        self.features = sorted(list(all_cols - excluded_set))

        # Solo features numéricas
        self.features = [f for f in self.features if pd.api.types.is_numeric_dtype(self.df[f])]

        self.report.append(f"**Features permitidas (numéricas):** {len(self.features)}\n\n")

        return excluded

    def data_quality_checks(self):
        """Validación de calidad de datos"""
        self.report.append("## 3. CALIDAD DE DATOS\n")

        # NaNs
        nan_counts = self.df[self.features].isna().sum()
        features_with_nans = nan_counts[nan_counts > 0].sort_values(ascending=False)

        if len(features_with_nans) > 0:
            self.report.append(f"**Features con NaNs:** {len(features_with_nans)}\n")
            self.report.append("```\n")
            for feat, count in features_with_nans.head(10).items():
                pct = 100 * count / len(self.df)
                self.report.append(f"  {feat}: {count} ({pct:.1f}%)\n")
            self.report.append("```\n\n")

        # Infinitos
        inf_counts = {}
        for col in self.features:
            n_inf = np.isinf(self.df[col]).sum()
            if n_inf > 0:
                inf_counts[col] = n_inf

        if inf_counts:
            self.report.append(f"**Features con infinitos:** {len(inf_counts)}\n")
            self.report.append("```\n")
            for feat, count in sorted(inf_counts.items(), key=lambda x: -x[1])[:10]:
                self.report.append(f"  {feat}: {count}\n")
            self.report.append("```\n\n")

        # Duplicados
        n_dupes = self.df.duplicated().sum()
        self.report.append(f"**Filas duplicadas:** {n_dupes}\n\n")

        # Limpiar datos para análisis
        # Eliminar filas con NaN en targets
        for target in self.targets:
            self.df = self.df[self.df[target].notna()]

        self.report.append(f"**Registros válidos para análisis:** {len(self.df):,}\n\n")

    def compute_correlations(self, target):
        """Calcula correlaciones Pearson y Spearman con significancia"""
        self.report.append(f"## 4. CORRELACIONES BASELINE - {target}\n")

        results = []

        for feat in self.features:
            # Obtener datos válidos (sin NaN ni Inf)
            valid_mask = self.df[feat].notna() & np.isfinite(self.df[feat]) & \
                        self.df[target].notna() & np.isfinite(self.df[target])

            if valid_mask.sum() < 30:
                continue

            x = self.df.loc[valid_mask, feat].values
            y = self.df.loc[valid_mask, target].values

            # Pearson
            try:
                r_pearson, p_pearson = pearsonr(x, y)
            except:
                r_pearson, p_pearson = np.nan, np.nan

            # Spearman
            try:
                r_spearman, p_spearman = spearmanr(x, y)
            except:
                r_spearman, p_spearman = np.nan, np.nan

            results.append({
                'feature': feat,
                'r_pearson': r_pearson,
                'p_pearson': p_pearson,
                'r_spearman': r_spearman,
                'p_spearman': p_spearman,
                'n_valid': valid_mask.sum()
            })

        # Crear DataFrame de resultados
        corr_df = pd.DataFrame(results)

        # FDR correction (Benjamini-Hochberg)
        from statsmodels.stats.multitest import multipletests

        if len(corr_df) > 0:
            _, p_adj_pearson, _, _ = multipletests(corr_df['p_pearson'].fillna(1),
                                                   method='fdr_bh', alpha=0.05)
            _, p_adj_spearman, _, _ = multipletests(corr_df['p_spearman'].fillna(1),
                                                    method='fdr_bh', alpha=0.05)

            corr_df['p_adj_pearson'] = p_adj_pearson
            corr_df['p_adj_spearman'] = p_adj_spearman

            # Ordenar por correlación absoluta de Spearman
            corr_df['abs_r_spearman'] = corr_df['r_spearman'].abs()
            corr_df = corr_df.sort_values('abs_r_spearman', ascending=False)

            # Top correlaciones
            self.report.append("### Top 20 Features por Correlación de Spearman\n\n")
            self.report.append("| Feature | r_Spearman | p_adj | r_Pearson | N |\n")
            self.report.append("|---------|------------|-------|-----------|---|\n")

            for _, row in corr_df.head(20).iterrows():
                sig_mark = "***" if row['p_adj_spearman'] < 0.001 else \
                          "**" if row['p_adj_spearman'] < 0.01 else \
                          "*" if row['p_adj_spearman'] < 0.05 else ""

                self.report.append(
                    f"| {row['feature'][:40]} | {row['r_spearman']:.4f}{sig_mark} | "
                    f"{row['p_adj_spearman']:.4f} | {row['r_pearson']:.4f} | {row['n_valid']:,} |\n"
                )

            self.report.append("\n*Significancia: *** p<0.001, ** p<0.01, * p<0.05 (FDR ajustado)*\n\n")

            # Guardar resultados
            self.results[f'correlations_{target}'] = corr_df

        return corr_df

    def analyze_by_quantiles(self, feature, target, n_quantiles=5):
        """Analiza target por cuantiles de una feature"""
        valid_mask = self.df[feature].notna() & np.isfinite(self.df[feature]) & \
                     self.df[target].notna() & np.isfinite(self.df[target])

        # Ajustar n_quantiles si la muestra es pequeña
        total_valid = valid_mask.sum()
        if total_valid < 150:  # Si hay menos de 150 registros, usar tertiles
            n_quantiles = 3
            min_required = self.min_bin_size * n_quantiles
        else:
            min_required = self.min_bin_size * n_quantiles

        if total_valid < min_required:
            return None

        df_valid = self.df.loc[valid_mask, [feature, target]].copy()

        # Crear cuantiles
        df_valid['quantile'] = pd.qcut(df_valid[feature], q=n_quantiles,
                                       labels=False, duplicates='drop')

        # Estadísticas por cuantile
        stats_by_q = df_valid.groupby('quantile')[target].agg([
            'count', 'mean', 'median', 'std',
            ('q25', lambda x: x.quantile(0.25)),
            ('q75', lambda x: x.quantile(0.75))
        ])

        # Verificar tamaño mínimo
        if (stats_by_q['count'] < self.min_bin_size).any():
            return None

        # Test de diferencia entre extremos
        top_q = df_valid[df_valid['quantile'] == df_valid['quantile'].max()][target]
        bottom_q = df_valid[df_valid['quantile'] == df_valid['quantile'].min()][target]

        # Mann-Whitney U test
        statistic, p_value = stats.mannwhitneyu(top_q, bottom_q, alternative='two-sided')

        # Tamaño del efecto (Cliff's Delta)
        cliffs_delta = self._cliffs_delta(top_q.values, bottom_q.values)

        result = {
            'feature': feature,
            'target': target,
            'n_quantiles': n_quantiles,
            'stats_by_q': stats_by_q,
            'delta_median': top_q.median() - bottom_q.median(),
            'delta_mean': top_q.mean() - bottom_q.mean(),
            'p_value': p_value,
            'cliffs_delta': cliffs_delta,
            'top_q_median': top_q.median(),
            'bottom_q_median': bottom_q.median()
        }

        return result

    def _cliffs_delta(self, x, y):
        """Calcula Cliff's Delta (tamaño del efecto no paramétrico)"""
        n_x = len(x)
        n_y = len(y)

        if n_x == 0 or n_y == 0:
            return np.nan

        # Matriz de comparaciones
        greater = np.sum([np.sum(x_i > y) for x_i in x])
        less = np.sum([np.sum(x_i < y) for x_i in x])

        delta = (greater - less) / (n_x * n_y)
        return delta

    def find_threshold_rules(self, target, top_n=20):
        """Busca reglas simples de umbral para top features"""
        self.report.append(f"## 5. REGLAS POR UMBRALES Y CUANTILES - {target}\n")

        # Obtener top features por correlación
        if f'correlations_{target}' not in self.results:
            return

        corr_df = self.results[f'correlations_{target}']
        top_features = corr_df.head(top_n)['feature'].tolist()

        rules = []

        for feat in top_features:
            # Analizar por quintiles
            result = self.analyze_by_quantiles(feat, target, n_quantiles=5)

            if result is None:
                continue

            # Si hay diferencia significativa
            if result['p_value'] < 0.05 and abs(result['cliffs_delta']) > 0.1:
                rules.append(result)

        # Ordenar por tamaño del efecto
        rules.sort(key=lambda x: abs(x['cliffs_delta']), reverse=True)

        # Reportar top reglas
        self.report.append("### Top Reglas por Cuantiles (Quintiles)\n\n")
        self.report.append("| Feature | Top Q1 Median | Bottom Q5 Median | Δ Median | Cliff's δ | p-value |\n")
        self.report.append("|---------|---------------|------------------|----------|-----------|----------|\n")

        for rule in rules[:15]:
            self.report.append(
                f"| {rule['feature'][:35]} | {rule['top_q_median']:.2f} | "
                f"{rule['bottom_q_median']:.2f} | {rule['delta_median']:.2f} | "
                f"{rule['cliffs_delta']:.3f} | {rule['p_value']:.4f} |\n"
            )

        self.report.append("\n")

        self.results[f'rules_{target}'] = rules

        return rules

    def analyze_vix(self, target):
        """Análisis especial de VIX_close"""
        self.report.append(f"## 6. ANÁLISIS ESPECIAL VIX - {target}\n")

        if 'VIX_Close' not in self.df.columns and 'VIX_close' not in self.df.columns:
            self.report.append("⚠️ Columna VIX no encontrada en el dataset\n\n")
            return

        vix_col = 'VIX_Close' if 'VIX_Close' in self.df.columns else 'VIX_close'

        # Convertir a temporal si hay columna de fecha
        if 'dia' in self.df.columns:
            self.df['dia_dt'] = pd.to_datetime(self.df['dia'])
            self.df = self.df.sort_values('dia_dt')

        # Features VIX derivadas (solo hacia atrás, sin look-ahead)
        windows = [5, 10, 20]

        for w in windows:
            # ROC (Rate of Change)
            self.df[f'VIX_ROC_{w}'] = self.df[vix_col].pct_change(w) * 100

            # Slope (pendiente lineal últimas w sesiones)
            self.df[f'VIX_slope_{w}'] = self.df[vix_col].rolling(w).apply(
                lambda x: np.polyfit(np.arange(len(x)), x, 1)[0] if len(x) == w else np.nan
            )

            # Z-score robusto
            rolling_median = self.df[vix_col].rolling(w).median()
            rolling_mad = self.df[vix_col].rolling(w).apply(
                lambda x: np.median(np.abs(x - np.median(x)))
            )
            self.df[f'VIX_zscore_{w}'] = (self.df[vix_col] - rolling_median) / (rolling_mad * 1.4826)

            # SMA y distancia
            self.df[f'VIX_SMA_{w}'] = self.df[vix_col].rolling(w).mean()
            self.df[f'VIX_above_SMA_{w}'] = self.df[vix_col] - self.df[f'VIX_SMA_{w}']

        # Correlaciones de features VIX
        vix_features = [col for col in self.df.columns if 'VIX' in col and col != vix_col]

        self.report.append("### Correlaciones VIX Features\n\n")
        self.report.append("| Feature | r_Spearman | p-value | Interpretación |\n")
        self.report.append("|---------|------------|---------|----------------|\n")

        for feat in vix_features:
            valid_mask = self.df[feat].notna() & np.isfinite(self.df[feat]) & \
                        self.df[target].notna() & np.isfinite(self.df[target])

            if valid_mask.sum() < 30:
                continue

            x = self.df.loc[valid_mask, feat].values
            y = self.df.loc[valid_mask, target].values

            r, p = spearmanr(x, y)

            # Interpretación
            if abs(r) > 0.3 and p < 0.05:
                interp = "🔥 Fuerte"
            elif abs(r) > 0.15 and p < 0.05:
                interp = "✓ Moderada"
            elif p < 0.05:
                interp = "· Débil"
            else:
                interp = "- No sig."

            self.report.append(f"| {feat} | {r:.4f} | {p:.4f} | {interp} |\n")

        self.report.append("\n")

        # Análisis por cuantiles de VIX
        vix_result = self.analyze_by_quantiles(vix_col, target, n_quantiles=5)

        if vix_result:
            self.report.append("### VIX por Quintiles\n\n")
            self.report.append(f"- **Δ Mediana (Q5 vs Q1):** {vix_result['delta_median']:.2f}\n")
            self.report.append(f"- **Cliff's Delta:** {vix_result['cliffs_delta']:.3f}\n")
            self.report.append(f"- **p-value:** {vix_result['p_value']:.4f}\n\n")

            stats = vix_result['stats_by_q']
            self.report.append("| Quintil | N | Median | Mean | Std |\n")
            self.report.append("|---------|---|--------|------|-----|\n")
            for idx, row in stats.iterrows():
                self.report.append(
                    f"| Q{int(idx)+1} | {int(row['count'])} | {row['median']:.2f} | "
                    f"{row['mean']:.2f} | {row['std']:.2f} |\n"
                )
            self.report.append("\n")

    def feature_engineering(self, target, top_n=10):
        """Feature engineering parsimonioso"""
        self.report.append(f"## 7. FEATURE ENGINEERING - {target}\n")

        # Obtener top features
        if f'correlations_{target}' not in self.results:
            return

        corr_df = self.results[f'correlations_{target}']
        top_features = corr_df.head(top_n)['feature'].tolist()

        self.report.append(f"Trabajando con top {len(top_features)} features...\n\n")

        new_features = {}

        # Transformaciones simples
        for feat in top_features:
            if feat not in self.df.columns:
                continue

            # Rank normalizado
            new_features[f'{feat}_rank'] = self.df[feat].rank(pct=True)

            # Log absoluto
            new_features[f'{feat}_log'] = np.log1p(np.abs(self.df[feat]))

            # Z-score robusto
            median = self.df[feat].median()
            mad = np.median(np.abs(self.df[feat] - median))
            if mad > 0:
                new_features[f'{feat}_zscore'] = (self.df[feat] - median) / (mad * 1.4826)

        # Ratios seguros (top 5 features)
        epsilon = 1e-8
        for i, feat1 in enumerate(top_features[:5]):
            for feat2 in top_features[i+1:6]:
                if feat1 in self.df.columns and feat2 in self.df.columns:
                    new_features[f'{feat1}_div_{feat2}'] = \
                        self.df[feat1] / (np.abs(self.df[feat2]) + epsilon)

        # Agregar nuevas features al DataFrame (temporal)
        df_temp = self.df.copy()
        for name, values in new_features.items():
            df_temp[name] = values

        # Evaluar nuevas features
        self.report.append("### Top Features Derivadas\n\n")
        self.report.append("| Feature Derivada | r_Spearman | p-value |\n")
        self.report.append("|------------------|------------|----------|\n")

        derived_corrs = []

        for feat_name in new_features.keys():
            valid_mask = df_temp[feat_name].notna() & np.isfinite(df_temp[feat_name]) & \
                        df_temp[target].notna() & np.isfinite(df_temp[target])

            if valid_mask.sum() < 30:
                continue

            x = df_temp.loc[valid_mask, feat_name].values
            y = df_temp.loc[valid_mask, target].values

            try:
                r, p = spearmanr(x, y)
                derived_corrs.append((feat_name, r, p, valid_mask.sum()))
            except:
                continue

        # Ordenar por correlación absoluta
        derived_corrs.sort(key=lambda x: abs(x[1]), reverse=True)

        for feat_name, r, p, n in derived_corrs[:15]:
            sig_mark = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
            self.report.append(f"| {feat_name[:50]} | {r:.4f}{sig_mark} | {p:.4f} |\n")

        self.report.append("\n")

    def oos_validation(self, target, top_n=10):
        """Validación Out-of-Sample con TimeSeriesSplit"""
        self.report.append(f"## 8. VALIDACIÓN OUT-OF-SAMPLE - {target}\n")

        # Preparar datos
        if f'correlations_{target}' not in self.results:
            self.report.append("⚠️ No hay correlaciones calculadas\n\n")
            return

        corr_df = self.results[f'correlations_{target}']
        top_features = corr_df.head(top_n)['feature'].tolist()

        # Filtrar features disponibles
        top_features = [f for f in top_features if f in self.df.columns]

        if len(top_features) == 0:
            self.report.append("⚠️ No hay features válidas para OOS\n\n")
            return

        # Crear matriz de features
        X = self.df[top_features].copy()
        y = self.df[target].copy()

        # Eliminar filas con NaN
        valid_mask = X.notna().all(axis=1) & y.notna() & np.isfinite(y)
        X = X[valid_mask]
        y = y[valid_mask]

        if len(X) < 100:
            self.report.append(f"⚠️ Datos insuficientes para OOS (N={len(X)})\n\n")
            return

        # TimeSeriesSplit (si hay orden temporal) o KFold
        if 'dia_dt' in self.df.columns:
            cv = TimeSeriesSplit(n_splits=5)
            cv_type = "TimeSeriesSplit"
        else:
            cv = KFold(n_splits=5, shuffle=True, random_state=42)
            cv_type = "KFold"

        self.report.append(f"**Validación:** {cv_type} con 5 folds\n")
        self.report.append(f"**Features usadas:** {len(top_features)}\n")
        self.report.append(f"**Muestras:** {len(X):,}\n\n")

        # Modelos a probar
        models = {
            'Ridge': Ridge(alpha=1.0),
            'Lasso': Lasso(alpha=0.1, max_iter=5000)
        }

        results_oos = {}

        for model_name, model in models.items():
            mae_scores = []
            r2_scores = []
            spearman_scores = []

            for train_idx, test_idx in cv.split(X):
                X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
                y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]

                # Escalar
                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_test_scaled = scaler.transform(X_test)

                # Entrenar
                model.fit(X_train_scaled, y_train)

                # Predecir
                y_pred = model.predict(X_test_scaled)

                # Métricas
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)

                # Spearman (ranking)
                r_spear, _ = spearmanr(y_test, y_pred)

                mae_scores.append(mae)
                r2_scores.append(r2)
                spearman_scores.append(r_spear)

            results_oos[model_name] = {
                'MAE': np.mean(mae_scores),
                'MAE_std': np.std(mae_scores),
                'R2': np.mean(r2_scores),
                'R2_std': np.std(r2_scores),
                'Spearman': np.mean(spearman_scores),
                'Spearman_std': np.std(spearman_scores)
            }

        # Reportar resultados
        self.report.append("### Resultados OOS por Modelo\n\n")
        self.report.append("| Modelo | MAE | R² | Spearman |\n")
        self.report.append("|--------|-----|-----|----------|\n")

        for model_name, metrics in results_oos.items():
            self.report.append(
                f"| {model_name} | {metrics['MAE']:.3f} ± {metrics['MAE_std']:.3f} | "
                f"{metrics['R2']:.3f} ± {metrics['R2_std']:.3f} | "
                f"{metrics['Spearman']:.3f} ± {metrics['Spearman_std']:.3f} |\n"
            )

        self.report.append("\n")

        # Interpretación
        best_spearman = max(results_oos.values(), key=lambda x: x['Spearman'])['Spearman']

        if best_spearman > 0.3:
            self.report.append("✅ **Conclusión:** Señal predictiva FUERTE encontrada (Spearman OOS > 0.3)\n\n")
        elif best_spearman > 0.15:
            self.report.append("✓ **Conclusión:** Señal predictiva MODERADA encontrada (Spearman OOS > 0.15)\n\n")
        elif best_spearman > 0.05:
            self.report.append("⚠️ **Conclusión:** Señal predictiva DÉBIL (Spearman OOS > 0.05)\n\n")
        else:
            self.report.append("❌ **Conclusión:** NO hay señal predictiva consistente OOS\n\n")

        self.results[f'oos_{target}'] = results_oos

    def generate_plots(self, target):
        """Genera gráficos clave"""
        self.report.append(f"## 9. VISUALIZACIONES - {target}\n")

        if f'correlations_{target}' not in self.results:
            return

        corr_df = self.results[f'correlations_{target}']
        top_features = corr_df.head(6)['feature'].tolist()

        # Plot 1: Scatter plots de top features
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()

        for idx, feat in enumerate(top_features):
            if feat not in self.df.columns:
                continue

            valid_mask = self.df[feat].notna() & np.isfinite(self.df[feat]) & \
                         self.df[target].notna() & np.isfinite(self.df[target])

            if valid_mask.sum() < 10:
                continue

            x = self.df.loc[valid_mask, feat]
            y = self.df.loc[valid_mask, target]

            axes[idx].scatter(x, y, alpha=0.3, s=10)

            # Línea de tendencia
            z = np.polyfit(x, y, 1)
            p = np.poly1d(z)
            x_sorted = np.sort(x)
            axes[idx].plot(x_sorted, p(x_sorted), "r--", alpha=0.8, linewidth=2)

            # Correlación
            r = corr_df[corr_df['feature'] == feat]['r_spearman'].values[0]
            axes[idx].set_title(f'{feat}\n(ρ={r:.3f})', fontsize=10)
            axes[idx].set_xlabel(feat, fontsize=8)
            axes[idx].set_ylabel(target, fontsize=8)
            axes[idx].grid(True, alpha=0.3)

        plt.tight_layout()
        plot1_path = f'scatter_top_features_{target}_DTE10_FF07.png'
        plt.savefig(plot1_path, dpi=100, bbox_inches='tight')
        plt.close()

        self.report.append(f"![Top Features Scatter]({plot1_path})\n\n")

        # Plot 2: Boxplots por cuantiles
        if f'rules_{target}' in self.results and len(self.results[f'rules_{target}']) > 0:
            top_rules = self.results[f'rules_{target}'][:4]

            fig, axes = plt.subplots(2, 2, figsize=(12, 10))
            axes = axes.flatten()

            for idx, rule in enumerate(top_rules):
                feat = rule['feature']

                if feat not in self.df.columns:
                    continue

                valid_mask = self.df[feat].notna() & np.isfinite(self.df[feat]) & \
                             self.df[target].notna() & np.isfinite(self.df[target])

                df_valid = self.df.loc[valid_mask, [feat, target]].copy()

                # Usar tertiles para muestras pequeñas
                n_q = 3 if len(df_valid) < 150 else 5
                labels = ['T1', 'T2', 'T3'] if n_q == 3 else ['Q1', 'Q2', 'Q3', 'Q4', 'Q5']

                df_valid['quantile'] = pd.qcut(df_valid[feat], q=n_q, labels=labels,
                                              duplicates='drop')

                df_valid.boxplot(column=target, by='quantile', ax=axes[idx])
                axes[idx].set_title(f'{feat}\n(Cliff\'s δ={rule["cliffs_delta"]:.3f})', fontsize=10)
                axes[idx].set_xlabel('Cuantil', fontsize=8)
                axes[idx].set_ylabel(target, fontsize=8)
                axes[idx].get_figure().suptitle('')

            plt.tight_layout()
            plot2_path = f'boxplot_quantiles_{target}_DTE10_FF07.png'
            plt.savefig(plot2_path, dpi=100, bbox_inches='tight')
            plt.close()

            self.report.append(f"![Boxplots por Cuantiles]({plot2_path})\n\n")

    def generate_executive_summary(self):
        """Genera resumen ejecutivo con hallazgos accionables"""
        summary = []
        summary.append("# RESUMEN EJECUTIVO\n")
        summary.append("## Hallazgos Accionables (Top 10)\n\n")

        findings = []

        for target in self.targets:
            if f'correlations_{target}' in self.results:
                corr_df = self.results[f'correlations_{target}']

                # Top correlaciones significativas
                sig_corrs = corr_df[
                    (corr_df['p_adj_spearman'] < 0.05) &
                    (corr_df['abs_r_spearman'] > 0.1)
                ].head(3)

                for _, row in sig_corrs.iterrows():
                    findings.append(
                        f"- **{row['feature']}** correlaciona {row['r_spearman']:.3f} con {target} "
                        f"(p_adj={row['p_adj_spearman']:.4f}, N={row['n_valid']:,})"
                    )

            if f'rules_{target}' in self.results:
                rules = self.results[f'rules_{target}']

                for rule in rules[:2]:
                    if abs(rule['cliffs_delta']) > 0.2:
                        findings.append(
                            f"- **{rule['feature']}**: Quintil superior vs inferior → "
                            f"Δ mediana = {rule['delta_median']:.2f} puntos "
                            f"(Cliff's δ={rule['cliffs_delta']:.3f}, p={rule['p_value']:.4f})"
                        )

            if f'oos_{target}' in self.results:
                oos = self.results[f'oos_{target}']
                best_model = max(oos.items(), key=lambda x: x[1]['Spearman'])

                if best_model[1]['Spearman'] > 0.15:
                    findings.append(
                        f"- **Modelo {best_model[0]}** para {target}: "
                        f"Spearman OOS = {best_model[1]['Spearman']:.3f} ± {best_model[1]['Spearman_std']:.3f} "
                        f"(señal predictiva {'FUERTE' if best_model[1]['Spearman'] > 0.3 else 'MODERADA'})"
                    )

        # Limitar a top 10
        for finding in findings[:10]:
            summary.append(finding + "\n")

        summary.append("\n")

        # Insertar al inicio del reporte
        self.report = summary + self.report

    def run_full_analysis(self):
        """Ejecuta análisis completo"""
        print("Iniciando análisis...")

        # 1. Cargar datos
        if not self.load_data():
            return False

        # 2. Detectar leakage
        self.detect_leakage()

        # 3. Calidad de datos
        self.data_quality_checks()

        # Para cada target
        for target in self.targets:
            print(f"\nAnalizando target: {target}")

            # 4. Correlaciones
            self.compute_correlations(target)

            # 5. Reglas por cuantiles
            self.find_threshold_rules(target, top_n=20)

            # 6. Análisis VIX
            self.analyze_vix(target)

            # 7. Feature engineering
            self.feature_engineering(target, top_n=10)

            # 8. Validación OOS
            self.oos_validation(target, top_n=10)

            # 9. Gráficos
            self.generate_plots(target)

        # 10. Resumen ejecutivo
        self.generate_executive_summary()

        # Guardar reporte
        report_path = 'INFORME_ANALISIS_PREDICTIVO_DTE10_FF07.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.writelines(self.report)

        print(f"\n✅ Análisis completado. Informe guardado en: {report_path}")

        return True

# MAIN
if __name__ == "__main__":
    # Configuración
    CSV_PATH = "combined_CALENDAR_mediana_w_stats_w_vix.csv"
    TARGETS = ["PnL_fwd_pts_50_mediana", "PnL_fwd_pts_90_mediana"]

    # Ejecutar análisis (min_bin_size reducido para muestra pequeña)
    analyzer = RobustAnalyzer(CSV_PATH, TARGETS, min_bin_size=20)
    success = analyzer.run_full_analysis()

    if success:
        print("\n" + "="*60)
        print("ANÁLISIS COMPLETADO EXITOSAMENTE")
        print("="*60)
    else:
        print("\n⚠️ El análisis no pudo completarse")

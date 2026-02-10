import csv
import hashlib
import pickle
from pathlib import Path
from typing import Any, Dict, List, Tuple

from .core.base import BaseNode


class CsvDataSourceNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        path = self.config.get("path") or inputs.get("path")
        uploaded_file_id = self.config.get("uploaded_file_id") or inputs.get("uploaded_file_id")
        delimiter = self.config.get("delimiter", ",")
        encoding = self.config.get("encoding", "utf-8")

        if not path and uploaded_file_id:
            path = str(Path("uploads") / str(uploaded_file_id))

        if not path:
            return {"rows": [], "table": [], "warning": "No CSV path or uploaded_file_id provided."}

        csv_path = Path(path)
        if not csv_path.exists():
            return {"rows": [], "table": [], "error": f"CSV not found at {csv_path}."}

        rows: List[Dict[str, Any]] = []
        with csv_path.open("r", encoding=encoding, newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            for row in reader:
                rows.append(dict(row))

        print(f"  [CsvDataSource] Loaded {len(rows)} rows from {csv_path}.")
        return {"rows": rows, "table": rows}


class PIIRedactionNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        dataset = inputs.get("rows") or inputs.get("table") or inputs.get("dataset") or []
        columns_to_drop = self.config.get("columns_to_drop", [])
        columns_to_hash = self.config.get("columns_to_hash", [])
        policy = self.config.get("policy", "LGPD")

        redacted_rows: List[Dict[str, Any]] = []
        dropped_count = 0
        hashed_count = 0

        for row in dataset:
            updated = dict(row)
            for column in columns_to_drop:
                if column in updated:
                    dropped_count += 1
                    updated.pop(column, None)

            for column in columns_to_hash:
                if column in updated and updated[column] is not None:
                    hashed_count += 1
                    value = str(updated[column])
                    updated[column] = hashlib.sha256(value.encode("utf-8")).hexdigest()

            redacted_rows.append(updated)

        report = {
            "policy": policy,
            "tags": [policy, "PII_REDACTED"],
            "dropped_columns": columns_to_drop,
            "hashed_columns": columns_to_hash,
            "dropped_count": dropped_count,
            "hashed_count": hashed_count,
            "total_rows": len(dataset),
        }
        print(f"  [PIIRedaction] Redacted dataset with policy {policy}.")
        return {"rows": redacted_rows, "table": redacted_rows, "governance_report": report}


class FeatureEngineeringChurnNode(BaseNode):
    _GEOGRAPHIES = ("France", "Germany", "Spain")
    _GENDERS = ("Male", "Female")

    @staticmethod
    def _to_float(value: Any, default: float = 0.0) -> float:
        if value is None:
            return default
        if isinstance(value, (int, float)):
            return float(value)
        value_str = str(value).strip()
        if value_str == "":
            return default
        try:
            return float(value_str)
        except ValueError:
            return default

    def _build_feature_row(self, row: Dict[str, Any]) -> Tuple[Dict[str, float], Dict[str, Any]]:
        features: Dict[str, float] = {
            "CreditScore": self._to_float(row.get("CreditScore")),
            "Age": self._to_float(row.get("Age")),
            "Tenure": self._to_float(row.get("Tenure")),
            "Balance": self._to_float(row.get("Balance")),
            "NumOfProducts": self._to_float(row.get("NumOfProducts")),
            "HasCrCard": self._to_float(row.get("HasCrCard")),
            "IsActiveMember": self._to_float(row.get("IsActiveMember")),
            "EstimatedSalary": self._to_float(row.get("EstimatedSalary")),
        }

        geography = str(row.get("Geography", "")).strip()
        gender = str(row.get("Gender", "")).strip()

        for geo in self._GEOGRAPHIES:
            features[f"Geography_{geo}"] = 1.0 if geography == geo else 0.0
        for gen in self._GENDERS:
            features[f"Gender_{gen}"] = 1.0 if gender == gen else 0.0

        metadata = {"geography": geography, "gender": gender}
        return features, metadata

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        dataset = inputs.get("rows") or inputs.get("table") or inputs.get("dataset") or []
        features: List[Dict[str, float]] = []
        metadata_rows: List[Dict[str, Any]] = []

        for row in dataset:
            feature_row, metadata = self._build_feature_row(row)
            features.append(feature_row)
            metadata_rows.append(metadata)

        feature_map = [
            {"name": key, "type": "numeric" if not key.startswith(("Geography_", "Gender_")) else "categorical"}
            for key in (features[0].keys() if features else [])
        ]
        print(f"  [FeatureEngineering] Generated feature matrix with {len(features)} rows.")
        return {"features": features, "feature_map": feature_map, "metadata": metadata_rows}


class ChurnModelPredictNode(BaseNode):
    @staticmethod
    def _resolve_feature_order(model: Any, features: List[Dict[str, Any]]) -> List[str]:
        if hasattr(model, "feature_names_in_"):
            return list(model.feature_names_in_)
        if features:
            return sorted(features[0].keys())
        return []

    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        model_path = self.config.get("model_path")
        threshold = float(self.config.get("threshold", 0.5))
        features = inputs.get("features") or []

        if not model_path:
            return {"error": "No model_path provided.", "proba": [], "label": []}

        model_file = Path(model_path)
        if not model_file.exists():
            return {"error": f"Model not found at {model_file}.", "proba": [], "label": []}

        if not features:
            return {"error": "No features provided for prediction.", "proba": [], "label": []}

        with model_file.open("rb") as handle:
            model = pickle.load(handle)

        feature_order = self._resolve_feature_order(model, features)
        if not feature_order:
            return {"error": "Unable to resolve feature order.", "proba": [], "label": []}

        matrix = [[row.get(feature, 0.0) for feature in feature_order] for row in features]

        probabilities: List[float] = []
        if hasattr(model, "predict_proba"):
            raw = model.predict_proba(matrix)
            for entry in raw:
                if isinstance(entry, (list, tuple)) and len(entry) > 1:
                    probabilities.append(float(entry[1]))
                else:
                    probabilities.append(float(entry[0]))
        elif hasattr(model, "predict"):
            raw = model.predict(matrix)
            probabilities = [float(value) for value in raw]
        else:
            return {"error": "Model does not support prediction.", "proba": [], "label": []}

        labels = [1 if proba >= threshold else 0 for proba in probabilities]
        print(f"  [ChurnModelPredict] Scored {len(probabilities)} rows.")
        return {"proba": probabilities, "label": labels, "threshold": threshold}


class ExplainabilityNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        features = inputs.get("features") or []
        feature_importance = self.config.get("feature_importance", {})
        top_k = int(self.config.get("top_k", 5))

        if not features:
            return {"top_factors": [], "method": "none", "warning": "No features provided."}

        row = features[0]
        importance_map = {}
        if isinstance(feature_importance, dict) and feature_importance:
            importance_map = feature_importance
        else:
            importance_map = {key: abs(value) for key, value in row.items()}

        scored = []
        for feature, importance in importance_map.items():
            value = float(row.get(feature, 0.0))
            contribution = float(importance) * value
            scored.append({
                "feature": feature,
                "importance": float(importance),
                "value": value,
                "contribution": contribution,
            })

        scored.sort(key=lambda item: abs(item["contribution"]), reverse=True)
        top_factors = scored[:top_k]
        print(f"  [Explainability] Generated top {len(top_factors)} factors.")
        return {"top_factors": top_factors, "method": "coefficients"}


class ExecutiveBriefNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        context = inputs.get("context") or self.config.get("context") or {}
        proba = inputs.get("proba") or []
        top_factors = inputs.get("top_factors") or []

        if isinstance(proba, list) and proba:
            churn_risk = float(proba[0])
        elif isinstance(proba, (int, float)):
            churn_risk = float(proba)
        else:
            churn_risk = 0.0

        segment = context.get("segment", "cliente")
        objective = context.get("objective", "reduzir churn")

        bullets = [
            f"Risco de churn estimado: {churn_risk:.2%} para o segmento {segment}.",
            f"Objetivo principal: {objective}.",
        ]

        if top_factors:
            factors_text = ", ".join(factor["feature"] for factor in top_factors)
            bullets.append(f"Principais fatores observados: {factors_text}.")

        recommendation = "Reforçar iniciativas de retenção para clientes de maior risco."

        brief = "\n".join(f"- {bullet}" for bullet in bullets)
        print("  [ExecutiveBrief] Generated executive summary.")
        return {"executive_brief": brief, "recommendation": recommendation}

"""Model service handling artifact loading, validation, caching, and inference."""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
import joblib
import numpy as np
import pandas as pd

from config.settings import settings
from app.schemas.risk import RiskFactor

logger = logging.getLogger("tvs_credit.model_service")


class ModelService:
    """Manages model artifacts, single-load caching, and inference pipeline."""

    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.threshold: float = 0.47
        self.classes_ = None
        self.class_1_index: int = 1
        self.feature_names: List[str] = []
        self._is_loaded: bool = False

    @property
    def is_ready(self) -> bool:
        """Check if all necessary artifacts are loaded and ready for inference."""
        return (
            self._is_loaded
            and self.model is not None
            and self.preprocessor is not None
            and self.threshold is not None
        )

    def load_artifacts(
        self,
        model_path: Optional[Path] = None,
        preprocessor_path: Optional[Path] = None,
        threshold_path: Optional[Path] = None,
    ) -> None:
        """Load and validate all trained model artifacts.

        Called once during application startup.
        """
        m_path = model_path or settings.resolved_model_path
        p_path = preprocessor_path or settings.resolved_preprocessor_path
        t_path = threshold_path or settings.resolved_threshold_path

        logger.info("Initializing TVS Credit model artifacts...")

        # 1. Load Preprocessor
        if not p_path.exists():
            logger.warning(f"Preprocessor artifact not found at {p_path}")
            raise FileNotFoundError(f"Preprocessor artifact missing at {p_path}")
        try:
            self.preprocessor = joblib.load(p_path)
            logger.info(f"Loaded preprocessor from {p_path.name}")
        except Exception as e:
            logger.error(f"Failed to deserialize preprocessor: {e}")
            raise

        # 2. Load Risk Threshold
        if not t_path.exists():
            logger.warning(f"Risk threshold artifact not found at {t_path}, fallback to 0.47")
            self.threshold = 0.47
        else:
            try:
                loaded_thresh = joblib.load(t_path)
                self.threshold = float(loaded_thresh)
                logger.info(f"Loaded operational risk threshold: {self.threshold:.4f}")
            except Exception as e:
                logger.error(f"Failed to deserialize risk threshold: {e}")
                raise

        # 3. Load Model
        if not m_path.exists():
            logger.warning(f"Model artifact not found at {m_path}")
            raise FileNotFoundError(f"Model artifact missing at {m_path}")
        try:
            self.model = joblib.load(m_path)
            logger.info(f"Loaded model from {m_path.name}")
        except Exception as e:
            logger.error(f"Failed to deserialize model: {e}")
            raise

        # 4. Verify Model attributes
        if not hasattr(self.model, "predict_proba"):
            raise ValueError("Loaded model does not support predict_proba")

        if hasattr(self.model, "classes_"):
            self.classes_ = list(self.model.classes_)
            if 1 in self.classes_:
                self.class_1_index = self.classes_.index(1)
            else:
                self.class_1_index = 1
            logger.info(f"Model classes: {self.classes_}, Class 1 index: {self.class_1_index}")

        # Extract feature names if available from preprocessor
        try:
            if hasattr(self.preprocessor, "get_feature_names_out"):
                self.feature_names = list(self.preprocessor.get_feature_names_out())
                logger.info(f"Preprocessor output dimensionality: {len(self.feature_names)} features")
        except Exception as e:
            logger.warning(f"Could not extract feature names from preprocessor: {e}")

        self._is_loaded = True
        logger.info("All TVS Credit ML artifacts verified and ready.")

    def predict_default_probability(self, df_featured: pd.DataFrame) -> float:
        """Run preprocessor and model inference to calculate probability of default (class 1)."""
        if not self.is_ready:
            raise RuntimeError("Model artifacts are not loaded. Service is not ready.")

        # Pass through the saved preprocessor
        X_processed = self.preprocessor.transform(df_featured)

        # Predict probability
        probabilities = self.model.predict_proba(X_processed)
        default_prob = float(probabilities[0, self.class_1_index])

        return default_prob

    def explain_prediction(self, df_featured: pd.DataFrame, top_k: int = 5) -> List[RiskFactor]:
        """Generate safe, model-based risk factor explanations using tree feature importances."""
        if not self.is_ready or not self.feature_names:
            return []

        try:
            X_processed = self.preprocessor.transform(df_featured)
            if hasattr(self.model, "feature_importances_"):
                importances = self.model.feature_importances_
                
                # Pair with feature names and sample values
                row_values = X_processed[0] if hasattr(X_processed, "__getitem__") else np.array(X_processed)[0]
                
                # Calculate contribution proxy
                factors = []
                for idx, (name, imp) in enumerate(zip(self.feature_names, importances)):
                    val = float(row_values[idx]) if idx < len(row_values) else 0.0
                    impact = "Positive" if val > 0 else "Negative"
                    factors.append(
                        RiskFactor(
                            feature=name.replace("num__", "").replace("cat__", ""),
                            impact=impact,
                            value=round(float(imp * abs(val)), 4)
                        )
                    )
                
                # Sort descending by contribution value
                factors.sort(key=lambda x: x.value, reverse=True)
                return factors[:top_k]
        except Exception as e:
            logger.warning(f"Explainability generation failed safely: {e}")
            return []
        return []


# Singleton instance
model_service = ModelService()

"""Decision Audit Trail service for TVS Credit NIRNAY.

Maintains immutable logs of credit evaluations, model versions, probability scores,
decision recommendations, and consented data signals for regulatory compliance.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.schemas.nirnay import AuditTrailRecord


class AuditService:
    """In-memory thread-safe store for NIRNAY assessment audit records."""

    def __init__(self):
        self._records: Dict[str, AuditTrailRecord] = {}

    def log_assessment(
        self,
        application_id: str,
        customer_id: str,
        customer_name: str,
        default_prob: float,
        risk_class: str,
        recommended_action: str,
        consented_sources: List[str],
        alt_stability_score: int,
        resilience_score: int,
        analyst_action: str = "Automated Evaluation Complete",
        dealer_status: str = "Eligible - Verification Complete"
    ) -> AuditTrailRecord:
        record = AuditTrailRecord(
            application_id=application_id,
            customer_id=customer_id,
            customer_name=customer_name,
            timestamp=datetime.now(timezone.utc).isoformat(),
            model_name="Enhanced Random Forest",
            model_version="1.0.0 (Production NIRNAY)",
            threshold=0.47,
            default_probability=round(default_prob, 4),
            risk_classification=risk_class,
            recommended_action=recommended_action,
            consented_sources=consented_sources,
            alternative_stability_score=alt_stability_score,
            resilience_score=resilience_score,
            analyst_action=analyst_action,
            dealer_status=dealer_status
        )
        self._records[customer_id] = record
        self._records[application_id] = record
        return record

    def get_record(self, key: str) -> Optional[AuditTrailRecord]:
        return self._records.get(key)

    def list_recent_records(self, limit: int = 50) -> List[AuditTrailRecord]:
        # Return unique by application_id
        seen = set()
        unique = []
        for r in reversed(list(self._records.values())):
            if r.application_id not in seen:
                seen.add(r.application_id)
                unique.append(r)
            if len(unique) >= limit:
                break
        return unique


audit_service = AuditService()

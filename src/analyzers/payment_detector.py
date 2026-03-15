"""Payment destination detection from transaction descriptions."""
import re
import yaml
from pathlib import Path
from typing import Optional, Dict, Tuple
from sqlalchemy.orm import Session
from src.database.models import PaymentDestination


class PaymentDetector:
    """Detects payment destinations from transaction descriptions."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize payment detector with pattern configuration.

        Args:
            config_path: Path to payment_patterns.yaml (default: config/payment_patterns.yaml)
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "payment_patterns.yaml"

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Compile regex patterns for efficiency
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile all regex patterns from config."""
        self.patterns = []

        for category, patterns in self.config.get('payment_destinations', {}).items():
            for item in patterns:
                compiled_pattern = re.compile(item['pattern'])
                self.patterns.append({
                    'pattern': compiled_pattern,
                    'name': item['name'],
                    'institution': item.get('institution'),
                    'type': item['type'],
                    'category': category
                })

    def detect(self, description: str) -> Optional[Dict]:
        """
        Detect payment destination from transaction description.

        Args:
            description: Transaction description text

        Returns:
            Dict with payment destination info if matched, None otherwise
            Keys: name, institution, type, category
        """
        for pattern_info in self.patterns:
            if pattern_info['pattern'].search(description):
                return {
                    'name': pattern_info['name'],
                    'institution': pattern_info['institution'],
                    'type': pattern_info['type'],
                    'category': pattern_info['category']
                }

        return None

    def get_or_create_destination(
        self,
        session: Session,
        description: str
    ) -> Optional[PaymentDestination]:
        """
        Detect and get/create payment destination in database.

        Args:
            session: Database session
            description: Transaction description

        Returns:
            PaymentDestination instance if detected, None otherwise
        """
        detected = self.detect(description)

        if not detected:
            return None

        # Check if destination already exists
        destination = session.query(PaymentDestination).filter(
            PaymentDestination.name == detected['name']
        ).first()

        if destination:
            return destination

        # Create new destination
        destination = PaymentDestination(
            name=detected['name'],
            destination_type=detected['type'],
            institution=detected['institution']
        )
        session.add(destination)
        session.commit()

        return destination

    def analyze_transactions(
        self,
        session: Session,
        account_id: Optional[int] = None
    ) -> Dict:
        """
        Analyze all transactions and detect payment destinations.

        Args:
            session: Database session
            account_id: Optional account ID to filter transactions

        Returns:
            Dict with analysis results
        """
        from src.database.models import Transaction

        query = session.query(Transaction)
        if account_id:
            query = query.filter(Transaction.account_id == account_id)

        transactions = query.all()

        detected_count = 0
        undetected_count = 0
        destination_breakdown = {}

        for transaction in transactions:
            if transaction.payment_destination_id:
                # Already has destination
                detected_count += 1
                dest_name = transaction.payment_destination.name
                destination_breakdown[dest_name] = destination_breakdown.get(dest_name, 0) + 1
            else:
                # Try to detect
                destination = self.get_or_create_destination(session, transaction.description)
                if destination:
                    transaction.payment_destination_id = destination.id
                    detected_count += 1
                    destination_breakdown[destination.name] = destination_breakdown.get(destination.name, 0) + 1
                else:
                    undetected_count += 1

        session.commit()

        return {
            'total_transactions': len(transactions),
            'detected_count': detected_count,
            'undetected_count': undetected_count,
            'detection_rate': detected_count / len(transactions) if transactions else 0,
            'destination_breakdown': destination_breakdown
        }

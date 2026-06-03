"""
Service de génération de rapports
Export PDF, CSV et JSON des résultats d'analyse
"""


def generate_report(campaign_id: str, fmt: str = "json") -> str:
    """Génère un rapport d'analyse au format demandé."""
    # TODO: implémenter la génération de rapports
    return f"Report for campaign {campaign_id} in {fmt} format"

"""Seed the database with a demo tenant and sample enterprise documents.

Usage:
    python scripts/seed_demo_data.py
"""
import asyncio
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert

from app.db.models import Base, Tenant
from app.db.session import async_session, engine
from app.rag.retriever import index_document

DEMO_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")

DEMO_DOCUMENTS: list[dict[str, object]] = [
    {
        "content": (
            "Politique de remboursement : tout produit peut être retourné dans les "
            "30 jours suivant l'achat avec preuve d'achat. Les produits numériques "
            "ne sont pas remboursables après téléchargement."
        ),
        "metadata": {"source": "faq", "category": "remboursements"},
    },
    {
        "content": (
            "Procédure d'escalade IT : les incidents P1 (interruption totale de service) "
            "doivent être signalés immédiatement à l'astreinte via #incidents-p1 Slack. "
            "SLA de résolution : 4 heures maximum. Les incidents P2 : SLA de 8 heures."
        ),
        "metadata": {"source": "runbook", "category": "incidents"},
    },
    {
        "content": (
            "Avantages employés : 25 jours de congés payés par an, télétravail jusqu'à "
            "3 jours par semaine, mutuelle d'entreprise prise en charge à 80%, "
            "tickets restaurant de 10 €/jour, prime de cooptation de 2 000 €."
        ),
        "metadata": {"source": "rh", "category": "avantages"},
    },
    {
        "content": (
            "Politique de sécurité informatique : les mots de passe doivent contenir "
            "au minimum 12 caractères dont une majuscule, un chiffre et un caractère spécial. "
            "Rotation obligatoire tous les 90 jours. MFA requis pour tous les accès VPN."
        ),
        "metadata": {"source": "policy", "category": "securite"},
    },
    {
        "content": (
            "Onboarding nouveaux employés : la première semaine est dédiée à la formation "
            "et aux présentations d'équipe. Les accès systèmes sont provisionnés J-1 avant "
            "l'arrivée. Le buddy program associe chaque nouvelle recrue à un mentor pendant 3 mois."
        ),
        "metadata": {"source": "rh", "category": "onboarding"},
    },
    {
        "content": (
            "Processus d'achat : tout achat supérieur à 1 000 € nécessite l'approbation "
            "du manager direct. Au-delà de 10 000 €, une validation du CFO est requise. "
            "Utiliser le portail Coupa pour toutes les demandes d'achat."
        ),
        "metadata": {"source": "finance", "category": "achats"},
    },
]


async def main() -> None:
    async with engine.begin() as conn:
        await conn.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        stmt = insert(Tenant).values(id=DEMO_TENANT_ID, name="demo-tenant")
        stmt = stmt.on_conflict_do_nothing(index_elements=["name"])
        await db.execute(stmt)
        await db.commit()

    for doc in DEMO_DOCUMENTS:
        await index_document(
            str(doc["content"]),
            dict(doc["metadata"]),  # type: ignore[arg-type]
            DEMO_TENANT_ID,
        )

    await engine.dispose()
    print(f"Seeded {len(DEMO_DOCUMENTS)} documents for tenant {DEMO_TENANT_ID}.")
    print()
    print("Generate an API token:")
    print(f"  python scripts/generate_token.py --tenant-id {DEMO_TENANT_ID}")


if __name__ == "__main__":
    asyncio.run(main())

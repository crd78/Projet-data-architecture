from dagster import op, job


@op
def run_gold_tasks(context):
    """Wrapper op that calls existing procedural functions in `gold.without_dagster`.

    Adjust which functions are invoked below depending on the desired gold steps.
    """
    from gold import without_dagster

    # Exemple : exécuter le calcul de prix par arrondissement
    without_dagster.prix_arrondissement()
    context.log.info("prix_arrondissement exécuté")

    # Décommentez et ajustez si vous voulez exécuter d'autres étapes
    # without_dagster.disponibilite_stationnement()
    # without_dagster.activite_quartier()

    return "done"


@job
def gold_job():
    run_gold_tasks()


# Liste d'assets (vide pour l'instant). Si vous souhaitez exposer
# des assets Dagster pour le gold, transformez les fonctions en `@asset`.
all_gold_assets = []

from celery import shared_task
from wbfdm.models import Controversy, Instrument

from wbportfolio.models import AssetPosition, Portfolio


@shared_task(queue="portfolio")
def synchronize_portfolio_controversies():
    active_portfolios = Portfolio.objects.filter_active_and_tracked()
    qs = (
        AssetPosition.objects.filter(portfolio__in=active_portfolios)
        .values("underlying_instrument")
        .distinct("underlying_instrument")
    )
    objs = {}
    securities = Instrument.objects.filter(id__in=qs.values("underlying_instrument"))
    securities_mapping = {security.id: security.get_root() for security in securities}
    for controversy in securities.dl.esg_controversies():
        instrument = securities_mapping[controversy["instrument_id"]]
        obj = Controversy.dict_to_model(controversy, instrument)
        objs[obj.external_id] = obj

    Controversy.objects.bulk_create(
        objs.values(),
        update_fields=[
            "instrument",
            "headline",
            "description",
            "source",
            "direct_involvement",
            "company_response",
            "review",
            "initiated",
            "flag",
            "status",
            "type",
            "severity",
        ],
        unique_fields=["external_id"],
        update_conflicts=True,
        batch_size=10000,
    )

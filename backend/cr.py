from models import Asset, DownloadsData, SiteContent
from sqlmodel import Session


def try_create_asset(*, session: Session, asset_create: Asset) -> Asset:

    try:
        db_obj = create_asset(session=session, asset_create=asset_create)
        return db_obj
    except:
        session.rollback()

    return asset_create


def create_asset(*, session: Session, asset_create: Asset) -> Asset:

    db_obj = asset_create

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


def create_downloads_data(
    *, session: Session, downloads_data_create: DownloadsData
) -> DownloadsData:

    db_obj = downloads_data_create

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj


def create_site_content(
    *, session: Session, site_content_create: SiteContent
) -> SiteContent:

    db_obj = site_content_create

    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)

    return db_obj

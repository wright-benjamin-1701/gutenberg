from models import Asset, DownloadsData, SiteContent

from sqlalchemy import select


from cr import try_create_asset, create_downloads_data


def get_most_recent_download_timestamp(session):

    data = (
        session.query(SiteContent).order_by(SiteContent.retrieved.desc()).limit(1).one()
    )

    return data.retrieved


def translate_fetched_data_to_database(session, retrieved: float, dfs):

    for bucket in dfs.keys():
        for ind, row in dfs[bucket].iterrows():
            dd = DownloadsData(
                retrieved=retrieved,
                count=row["count"],
                bucket=bucket,
                asset=row["asset"],
            )

            dd = create_downloads_data(session=session, downloads_data_create=dd)
            asset = Asset(url=row["asset"], name=row["name"])
            asset = try_create_asset(session=session, asset_create=asset)

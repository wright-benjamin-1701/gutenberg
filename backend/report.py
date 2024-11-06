import models
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import plotly.express as px
import chart_studio.plotly as py
import utils

def get_key_timestamps(site_content_list):
    keyframe_map = {}

    for site in site_content_list:
        soup = BeautifulSoup(site.content,'html.parser')
        key = soup.find('caption').next_sibling.next_element.find('th').text
        if key in keyframe_map.keys():
            pass
        else:
            keyframe_map[key] = site.retrieved

    keyframes = list(set(keyframe_map.values()))
    return keyframes

def retrieved_for_display(row):
    retrieved = row['retrieved']
    return str(datetime.datetime.fromtimestamp(retrieved - utils.SECONDS_PER_DAY).date())

def report():

    session = models.Session()

    K = 20

    keyframes = get_key_timestamps(session.query(models.SiteContent).order_by(models.SiteContent.retrieved.desc()).limit(K).all())

    df = pd.read_sql(sql='SELECT * FROM downloadsdata',con=models.database_url, index_col=None)
    df = df[df['retrieved'].isin(keyframes)]
    df['retrieved_label'] = df.apply(retrieved_for_display,axis=1)
    df = df.drop_duplicates(subset=['retrieved_label','asset','bucket'])

    for bucket,type in [('Top 100 EBooks yesterday','E-Book'),('Top 100 Authors yesterday','Author')]:
        report_df = df[df['bucket'] == bucket].reset_index()

        T = 10
        top_arr = report_df.groupby('asset')[['count']].sum().reset_index().sort_values('count',ascending=False).head(T)['asset'].values
        plot_df = report_df[report_df['asset'].isin(top_arr)].drop(columns=['index','bucket'])
        asset_df = pd.read_sql('SELECT * FROM assets',models.database_url,index_col=None)
        plot_df = plot_df.merge(asset_df,left_on='asset',right_on='url')
        title = f'Top {T} {type}s Downloaded from Project Gutenberg over Past {len(keyframes)} Days'
        fig = px.line(plot_df,x='retrieved_label',y='count',line_group='name',color='name', labels=
                    {
                        'name': 'Legend' ,
                        'count': 'Number of Downloads',
                        'retrieved_label': 'Date'
                    },
                    title=title
                    )
        fig.update_xaxes(showticklabels=True, dtick='D1')
        #fig.show()
        py.plot(fig, filename=f'project-gutenberg-most-recent-{type}', auto_open=False)

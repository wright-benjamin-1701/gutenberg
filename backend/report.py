import models
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import plotly.express as px
import chart_studio.plotly as py
import utils
from fuzzywuzzy import fuzz

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

    K = 28

    keyframes = get_key_timestamps(session.query(models.SiteContent).order_by(models.SiteContent.retrieved.desc()).limit(K).all())

    df = pd.read_sql(sql='SELECT * FROM downloadsdata',con=models.database_url, index_col=None)
    df = df[df['retrieved'].isin(keyframes)]
    df['retrieved_label'] = df.apply(retrieved_for_display,axis=1)
    df = df.drop_duplicates(subset=['retrieved_label','asset','bucket'])

    for bucket,type in [('Top 100 EBooks yesterday','E-Book'),('Top 100 Authors yesterday','Author')]:
        report_df = df[df['bucket'] == bucket].reset_index()
        asset_df = pd.read_sql('SELECT * FROM assets',models.database_url,index_col=None)
        report_df = report_df.merge(asset_df,left_on='asset',right_on='url')

        T = 10
        S = 80
        def get_similarity_group(row):
            name = row['name']
            similarity_threshold = S  
            for group, _ in report_df.groupby('name').groups.items():
                if fuzz.ratio(name, group) > similarity_threshold:
                    return group
            return name
        report_df['fuzzy_name'] = report_df.apply(get_similarity_group,axis=1)
        
        top_arr = report_df.groupby('fuzzy_name')[['count']].sum().reset_index().sort_values('count',ascending=False).head(T)['fuzzy_name'].values
        plot_df = report_df[report_df['fuzzy_name'].isin(top_arr)].drop(columns=['index','bucket'])
        plot_df = plot_df.groupby(['fuzzy_name','retrieved']).agg({'count':'sum'}).reset_index()
        plot_df['retrieved_label'] = plot_df.apply(retrieved_for_display,axis=1)
        
        title = f'Top {T} {type}s Downloaded from Project Gutenberg over Past {len(keyframes)} Days'
        fig = px.line(plot_df,x='retrieved_label',y='count',line_group='fuzzy_name',color='fuzzy_name', labels=
                    {
                        'name': 'Legend' ,
                        'count': 'Number of Downloads',
                        'retrieved_label': 'Date'
                    },
                    title=title
                    )
        fig.update_xaxes(showticklabels=True, dtick='D1')
        fig.update_layout(legend=dict(
        orientation="v",
        yanchor="top",
        y=1,
        xanchor="left",
        x=1
        ))
        #fig.show()

        py.plot(fig, filename=f'project-gutenberg-most-recent-{type}', auto_open=False)

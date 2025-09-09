"""
Facebook Ads utility functions.
Copyright (C) 2022 Humankind Investments
"""

import re
import requests


def get_access_token(app_id, app_secret):
    """
    Get an access token that is valid for up to 2 hours

    Parameters
    ----------
    app_id : str
        Credential for the facebook API.
    app_secret : str
        Credential for the facebook API.

    Returns
    -------
    str
        Access token for facebook API

    """
    url= f"""https://graph.facebook.com/oauth/access_token?client_id={app_id}&client_secret={app_secret}&grant_type=client_credentials"""
    response = requests.get(url, timeout=30).json()
    return response["access_token"]


def get_columns(df_columns):
    """
    Get lists of columns by type for aggregating statistics.

    Parameters
    ----------
    df_columns : list of str
        List of column names in dataframe.

    Returns
    -------
    list of str
        List of column names representing metadata.
    list of str
        List of column names representing additive values.
    list of str
        List of column names representing scores.
    list of str
        List of column names representing ranks.
    list of str
        List of column names representing fractional values.
    """

    meta_cols = [col for col in ['account_id',
                                 'campaign_id',
                                 'campaign_name',
                                 'adset_id',
                                 'adset_name',
                                 'ad_id',
                                 'ad_name',
                                 'objective',
                                 'optimization_goal',
                                 ] if col in df_columns]

    sum_cols = [col for col in ['spend',
                                'impressions',
                                'reach',
                                'clicks',
                                'unique_clicks',
                                'link_clicks',
                                'landing_page_views',
                                'post_engagements',
                                'page_engagements',
                                'unique_link_clicks',
                                'unique_post_engagements',
                                'unique_page_engagements',
                                'outbound_clicks',
                                'unique_outbound_clicks',
                                'video_30_sec_watched_actions',
                                'video_avg_time_watched_actions',
                                'video_p100_watched_actions',
                                'video_p75_watched_actions',
                                'video_p50_watched_actions',
                                'video_p25_watched_actions',
                                'video_play_actions',
                                'visits',
                                'not_bounced',
                                'etf_clicks',
                                ] if col in df_columns]

    score_cols = [col for col in df_columns if re.search("^quality_score.*$", col)]

    rank_cols = [col for col in df_columns if re.search("^.*ranking$", col)]

    div_cols = [col for col in ['frequency',
                                'ctr',
                                'unique_ctr',
                                'cpc',
                                'cost_per_unique_click',
                                'cpm',
                                'cpp',
                                'cost_per_link_click',
                                'cost_per_landing_page_view',
                                'cost_per_post_engagement',
                                'cost_per_page_engagement',
                                'cost_per_unique_link_click',
                                'cost_per_unique_post_engagement',
                                'cost_per_unique_page_engagement',
                                'outbound_clicks_ctr',
                                'unique_outbound_clicks_ctr',
                                'cost_per_outbound_click',
                                'cost_per_unique_outbound_click',
                                ] if col in df_columns]

    return meta_cols, sum_cols, score_cols, rank_cols, div_cols


def calculate_fractions(df, columns):
    """
    Return fractional values for given columns of dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        Facebook Ads dataframe.
    columns : list of str
        List of columns to calculate and return.

    Returns
    -------
    pd.DataFrame
        Dataframe containing columns with recalculated values.
    """
    
    ctr_cols = [col for col in columns if re.search(r"^.*ctr.*$", col)]
    cost_cols = [col for col in columns if re.search(r"^(cost.*|cp.)$", col)]

    try:
        df['frequency'] = df['impressions'] / df['reach']
    except:
        pass

    for icol in ctr_cols:
        numer = icol.split('ctr')[0]
        if 'click' not in numer: numer += 'clicks'
        numer = numer.strip('_')
        denom = 'reach' if numer.startswith('unique') else 'impressions'
        try:
            df[icol] = df[numer] / df[denom] * 100
        except:
            pass
        
    for icol in cost_cols:
        mult = 1
        numer = 'spend'
        col_split = icol.split('cost_per_')
        try:
            denom = col_split[1] + 's'
        except IndexError:
            denom = col_split[0]
            if denom == 'cpm' or denom == 'cpp':
                denom = 'impressions' if denom == 'cpm' else 'reach'
                mult = 1000
            else:
                denom = 'clicks'
        try:
            df[icol] = df[numer] / df[denom] * mult
        except:
            pass

    return df[columns]



"""
Analysis utility functions.
Copyright (C) 2022 Humankind Investments.
"""

import os
from joblib import load
import pathlib
import re

from datetime import datetime
import calendar
import pytz
eastern = pytz.timezone('US/Eastern')

import requests
from bs4 import BeautifulSoup
import json

import pandas as pd
import numpy as np

from .db_utils import database_connect


# CLEANING DUPLICATE AND SPLIT VISITS +++++++++++++++++++++++++++++++++++++++++++++++++++++++
def drop_false_splits(df):
    """
    Drop false splits.
    
    Drop extraneous false splits, i.e. visits with duplicate visit counts per visitor
    occurring more than thirty minutes from each other. For each set of false splits, 
    the visit with the most activity is kept.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of false splits.
        
    Returns
    -------
    pd.DataFrame
        Dataframe of remaining splits after drops.
    """
    
    # keep visit among false splits with longest visit duration or most actions
    cdf = df.sort_values(by=['visit_duration', 'actions'],
                         ascending=[False, False]).drop_duplicates(
                             subset=['visitor_id', 'visit_count']).reset_index(drop=True)
    
    return cdf


def combine_true_splits(df, dt0=True):
    """
    Combine true splits.
    
    Combine and return true split visits, i.e. visits with duplicate visit counts 
    per visitor occurring within thirty minutes of one another.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of true splits.
    dt0 : bool
        Whether delta-dt between visits is 0, indicating split visits occur at same time.
        
    Returns
    -------
    pd.DataFrame
        Dataframe of combined splits.
    """
    
    # separate columns by how data to be aggregated
    mean_cols = [col for col in df.columns if col.split('_')[0] == 'avg']
    sum_cols = [col for col in df.columns if col.split('_')[-1] in [
        'actions', 'pages', 'downloads', 'outlinks', 'buyetfs', 'brokerlinks', 
        'plays', 'pauses', 'resumes', 'seeks', 'finishes', 
        'time', 'submissions', 'duration'] and col != 'time' and col not in mean_cols]
    first_cols = [col for col in df.columns if col not in
                  mean_cols + sum_cols and col.split('_')[0] not in [
                      'first', 'last', 'entry', 'exit'] and col.split('_')[-1] not in [
                          'flow', 'ts', 'list'] and not col.endswith('video_resolution')]
    manual_cols = [col for col in df.columns if col not in sum_cols + mean_cols + first_cols]

    # convert numeric columns to proper type
    df[mean_cols] = df[mean_cols].astype(float)
    
    # combine split visits with same visitor id and visit count
    # --> sort by visit id for split visits occurring at same time; split by datetime otherwise
    sort_col = 'visit_id' if dt0 else 'datetime'
    grp_cols = ['visitor_id', 'visit_count']
    # --> also group by datetime for split visits occurring at same time
    if dt0: grp_cols.append('datetime')
    grp = df.sort_values(by=sort_col).groupby(grp_cols)
    
    # apply basic aggregates for appropriate columns (first/last, sum, mean)
    first_grp = grp[[col for col in first_cols if col not in grp.keys]]
    # --> pull basic visit info from last visit info in half hour window if delta-t != 0
    first_df = first_grp.first() if dt0 else first_grp.last()
    sum_df = grp[[col for col in sum_cols if col not in grp.keys]].sum()
    mean_df = grp[[col for col in mean_cols if col not in grp.keys]].mean()
    cdf = pd.concat([first_df, sum_df, mean_df], axis=1)

    # combine remaining columns manually ...
    
    # select first and last non-empty action, and combine non-empty action flows in order
    actgrp = df[df['first_action'] != 'None'].sort_values(by=sort_col).groupby(
        grp_cols, group_keys=False)
    acts_df = pd.concat([actgrp['first_action'].first(), 
                         actgrp['last_action'].last(),
                         actgrp['action_flow'].apply(lambda x: ','.join(x)),
                         actgrp['action_ts'].apply(lambda x: ','.join(x)),
                         actgrp['action_site_flow'].apply(lambda x: ','.join(x)), 
                         actgrp['action_path_flow'].apply(lambda x: ','.join(x))], axis=1)
    
    # select first/last entry/exit pages, and fill in missing values based on first/last actions
    pgs_df = pd.concat([actgrp['entry_page'].first(), actgrp['exit_page'].last()], axis=1)
    pgs_df.loc[(pgs_df['entry_page'] == 'None') &
               (acts_df['first_action'].str.rsplit('_', n=1).str[0].isin(
                   ['humankind_video', 'humankind-short_video', 'getstarted_form'])),
               'entry_page'] = 'humankind'
    pgs_df.loc[(pgs_df['entry_page'] == 'None') &
               ((acts_df['first_action'].str.rsplit('_', n=1).str[0].isin(
                   ['wtf_video', 'wtf-short_video', 'buyetf'])) |
                (acts_df['first_action'].str.split('_', n=1).str[-1].isin(
                    ['brokerlink_click', 'download']))), 'entry_page'] = 'humankindfunds'
    pgs_df.loc[(pgs_df['exit_page'] == 'None') &
               (acts_df['last_action'].str.rsplit('_', n=1).str[0].isin(
                   ['humankind_video', 'humankind-short_video', 'getstarted_form'])),
               'exit_page'] = 'humankind'
    pgs_df.loc[(pgs_df['exit_page'] == 'None') &
               ((acts_df['last_action'].str.rsplit('_', n=1).str[0].isin(
                   ['wtf_video', 'wtf-short_video', 'buyetf'])) |
                (acts_df['last_action'].str.split('_', n=1).str[-1].isin(
                    ['brokerlink_click', 'download']))), 'exit_page'] = 'humankindfunds'

    # combine non-empty page flows
    pggrp = df[df['page_flow'] != 'None'].sort_values(by=sort_col).groupby(
        grp_cols, group_keys=False)
    pgs_df = pd.concat([
        pgs_df, pggrp['page_flow'].apply(lambda x: ','.join(x)), 
        pggrp['page_ts'].apply(lambda x: ','.join(x))], axis=1).fillna('None')
    
    # combine non-empty article post and ranked company page lists
    for pg in ['article-post', 'ranked-company']:
        pg += '_page_list'
        pgs_df = pd.concat([pgs_df, df[df[pg].fillna('None').replace(
            'NaN', 'None') != 'None'].sort_values(by=sort_col).groupby(
                grp_cols, group_keys=False)[pg].apply(
                    lambda x: ','.join(x))], axis=1).fillna('None')
        
    # combine non-empty download flows
    dlgrp = df[df['download_flow'] != 'None'].sort_values(by=sort_col).groupby(
        grp_cols, group_keys=False)
    dls_df = pd.concat([
        dlgrp['download_flow'].apply(lambda x: ','.join(x)), 
        dlgrp['download_ts'].apply(lambda x: ','.join(x))], axis=1).fillna('None')
    
    # combine non-empty outlink flows
    olgrp = df[df['outlink_flow'] != 'None'].sort_values(by=sort_col).groupby(
        grp_cols, group_keys=False)
    ols_df = pd.concat([
        olgrp['outlink_flow'].apply(lambda x: ','.join(x)), 
        olgrp['outlink_ts'].apply(lambda x: ','.join(x))], axis=1).fillna('None')

    # combine non-empty outlink lists
    for ol in ['social', 'crs', 'disclosures', 'articles']:
        ol += '_outlink_list'
        ols_df = pd.concat([ols_df, df[df[ol].fillna('None').replace(
            'NaN', 'None') != 'None'].sort_values(by=sort_col).groupby(
                grp_cols, group_keys=False)[ol].apply(
                    lambda x: ','.join(x))], axis=1).fillna('None')
           
    # combine non-empty buy-etf timestamps
    etfs_df = df[df['buyetf_ts'].fillna('None').replace(
        'NaN', 'None') != 'None'].sort_values(by=sort_col).groupby(
            grp_cols, group_keys=False)['buyetf_ts'].apply(lambda x: ','.join(x))
    
    # combine non-empty broker link flows
    brkgrp = df[df['brokerlink_flow'] != 'None'].sort_values(by=sort_col).groupby(
        grp_cols, group_keys=False)
    brks_df = pd.concat([
        brkgrp['brokerlink_flow'].apply(lambda x: ','.join(x)), 
        brkgrp['brokerlink_ts'].apply(lambda x: ','.join(x))], axis=1).fillna('None')
    
    # combine non-empty video flows and non-empty video resolutions
    vidgrp = df[df['video_action_flow'] != 'None'].sort_values(by=sort_col).groupby(
        grp_cols, group_keys=False)
    vids_df = pd.concat([
        vidgrp['video_action_flow'].apply(lambda x: ','.join(x)), 
        vidgrp['video_action_ts'].apply(lambda x: ','.join(x))], axis=1).fillna('None')

    # combine non-empty form flows
    frmgrp = df[df['form_action_flow'] != 'None'].sort_values(by=sort_col).groupby(
        grp_cols, group_keys=False)
    frms_df = pd.concat([
        frmgrp['form_action_flow'].apply(lambda x: ','.join(x)), 
        frmgrp['form_action_ts'].apply(lambda x: ','.join(x))], axis=1).fillna('None')
    
    # combine all split visit columns
    cdf = pd.concat([cdf, acts_df, pgs_df, dls_df, ols_df, etfs_df,
                     brks_df, vids_df, frms_df], axis=1).fillna('None')
    
    # reset missing values in appropriate columns
    cdt = cdf.index.get_level_values(2) if dt0 else cdf['datetime']
    for pg in [col[:-1] for col in df.isnull().sum()[df.isnull().sum() > 0].index
               if col.endswith('_pages')]:
        cdf.loc[cdt <= df[df[pg + 's'].isnull()].sort_values(
            by='datetime', ascending=False)['datetime'].iloc[0],
                [col for col in cdf.columns if pg in col]] = np.nan
    for dl in [col[:-1] for col in df.isnull().sum()[df.isnull().sum() > 0].index
               if col.endswith('_downloads')]:
        cdf.loc[cdt <= df[df[dl + 's'].isnull()].sort_values(
            by='datetime', ascending=False)['datetime'].iloc[0],
                [col for col in cdf.columns if col == dl + 's'
                 or col == dl + '_duration']] = np.nan
    for ol in [col[:-1] for col in df.isnull().sum()[df.isnull().sum() > 0].index
               if col.endswith('_outlinks')]:
        cdf.loc[cdt <= df[df[ol + 's'].isnull()].sort_values(
            by='datetime', ascending=False)['datetime'].iloc[0],
                [col for col in cdf.columns if ol in col]] = np.nan
    if any(df['buyetfs'].isnull()):
        cdf.loc[cdt <= df[df['buyetfs'].isnull()].sort_values(
            by='datetime', ascending=False)['datetime'].iloc[0],
                [col for col in cdf.columns if 'buyetf' in col]] = np.nan
    for vid in [col.rsplit('_', 1)[0] for col in df.isnull().sum()[df.isnull().sum() > 0].index
                if col.endswith('_video_plays')]:
        cdf.loc[cdt <= df[df[vid + '_plays'].isnull()].sort_values(
            by='datetime', ascending=False)['datetime'].iloc[0],
                [col for col in cdf.columns if vid in col]] = np.nan
    for frm in [col.rsplit('_', 1)[0] for col in df.isnull().sum()[df.isnull().sum() > 0].index
                if col.endswith('_form_actions')]:
        cdf.loc[cdt <= df[df[frm + '_actions'].isnull()].sort_values(
            by='datetime', ascending=False)['datetime'].iloc[0],
                [col for col in cdf.columns if frm in col]] = np.nan
    
    return cdf
    
    
def clean_split_visits(df, true_split=True, same_time=True):
    """
    Clean split visits, combining true splits and dropping false splits.
    
    Combine true split visits, i.e. visits with duplicate visit counts per visitor 
    occurring within thirty minutes of one another, and drop extraneous false splits,
    i.e. visits with duplicate visit counts per visitor occurring more than thirty 
    minutes from each other.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of split visits.
    true_split : bool
        Whether split visits are true splits or false splits.
    same_time : bool
        Whether true splits occur at same time or different times.
        
    Returns
    -------
    pd.DataFrame
        Cleaned dataframe of split visits.
    """

    # calculate differences in time between split visits
    grp = df.sort_values(by='datetime').groupby(['visitor_id', 'visit_count'])
    # --> deltadt = time between each split visit for given visitor ID and visit count
    deltadt = grp['datetime'].apply(list).apply(
        lambda x: [(x[i+1] - x[i]).total_seconds() for i in range(len(x)-1)]).rename('deltadt')
    # --> visit_id_pairs = split visit pairs for which delta-dt calculated
    visit_id_pairs = grp['visit_id'].unique().apply(
        lambda x: [(x[i], x[i+1]) for i in range(len(x)-1)] if len(x) > 1 else
        [(x[0], x[0])]).rename('visit_id_pairs')
    split_dt = pd.concat([deltadt, visit_id_pairs], axis=1)
    
    # filter out split visits already cleaned (no duplicates)
    split_mask = split_dt['deltadt'].str.len() > 0
    split_dt = pd.concat([split_dt[split_mask]['deltadt'].explode(),
                          split_dt[split_mask]['visit_id_pairs'].explode()], axis=1)
    
    # sum up total delta-dt for true splits occurring at different times or false splits
    if not true_split or not same_time:
        split_dt = pd.concat([
            split_dt.reset_index().groupby(['visitor_id', 'visit_count'])['deltadt'].sum(),
            split_dt['visit_id_pairs'].apply(
                lambda x: list(x)).explode().drop_duplicates().reset_index().groupby([
                    'visitor_id', 'visit_count'])['visit_id_pairs'].unique()], axis=1)
    # set delta-dt thresholds for selecting split visits of given type
    if true_split:
        deltadt_mask = split_dt['deltadt'] == 0 if same_time else split_dt['deltadt'] < 1800
    else:
        deltadt_mask = split_dt['deltadt'] >= 1800
    # isolate split visits of given type
    split_ids = split_dt[deltadt_mask]['visit_id_pairs'].apply(
        lambda x: list(x)).explode().drop_duplicates()
    split_visits = df[df['visit_id'].isin(split_ids)].reset_index(drop=True)
    
    # combine true splits or drop false splits
    if true_split: clean_splits = combine_true_splits(split_visits, same_time).reset_index()
    else: clean_splits = drop_false_splits(split_visits)

    # drop split visits of given type, and add newly cleaned split visits
    df = df.drop(df.loc[df['visit_id'].isin(split_visits['visit_id'])].index)
    df = pd.concat([df, clean_splits]).sort_values(by='visit_id').reset_index(drop=True)
    
    return df


def get_split_visits(df):
    """
    Get split visits from visit-level data.
    
    Identify and return all split visits from visit-level data set, where split visits
    are those with duplicate visit counts per visitor.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of visits.
    
    Returns
    -------
    pd.DataFrame
        Dataframe of split visits.
    """

    # count number of visit IDs associated with each visitor ID - visit count pair
    visit_count = df.groupby(['visitor_id', 'visit_count'])['visit_id'].count()
    
    # isolate visitor ID - visit count pairs with multiple visit IDs
    dupl_visit_count = visit_count[visit_count > 1]
    
    # pull out split visits from visit-level data set
    split_visits = df.loc[df[['visitor_id', 'visit_count']].apply(
        tuple, axis=1).isin(dupl_visit_count.index)].reset_index(drop=True)
    
    return split_visits


def clean_duplicate_visits(df):
    """
    Clean duplicate visits from visit-level data.
    
    The real-time visits logged in the visit-level data set are sometimes prone to 
    tracking errors by Matomo that result in duplicate visits. Such duplicate visits 
    can take the form of true duplicates, where multiple rows contain identical entries 
    but for the visit IDs attached to them. Alternatively, duplicate visits can appear 
    in the form of split visits, where a single visit is split into multiple entries with 
    different visit IDs and visit metrics for the same visit count and visitor ID. 
    When such split visits occur within a small window of time, i.e. within thirty minutes 
    of one another, such split visits represent true splits that should be recombined into 
    the original visits from which they were split. On the other hand, when split visits 
    are spread across large amounts of time, i.e. hours or days, they represent false splits, 
    or truly unique visits that Matomo erroneously attributed the same visit count to, which 
    are cleaned by dropping all but those with the longest visit durations or most activity.
    
    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of visits.
    
    Returns
    -------
    pd.DataFrame
        Dataframe of visits with cleaned duplicates.
    """

    # clean action ts columns: replace '0.0' with 'None'
    for col in [col for col in df.columns if col.endswith('_ts')]:
        df[col] = df[col].astype(str).replace('0.0', 'None')

    # DROP DUPLICATE VISITS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # duplicate visits = entries with identical metrics except for visit IDs
    df = df.drop_duplicates(subset=[col for col in df.columns if
                                    col != 'visit_id']).reset_index(drop=True)

    
    # IDENTIFY SPLIT VISITS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # split visits = visits with duplicate visit counts per visitor
    
    # isolate split visits to be combined or cleaned
    split_df = get_split_visits(df)

    # keep track of initial split visit IDs (for dropping later)
    split_visit_ids = split_df['visit_id']

    # drop split visits with no actions (no use in combining these if nothing to combine)
    split_df = split_df.drop(split_df[split_df['actions'] == 0].index).reset_index(drop=True)

    # add datetime column
    split_df['datetime'] = pd.to_datetime(split_df['date'].astype(str) + ' ' + split_df['time'])
    
    # COMBINE SAME-TIME TRUE SPLITS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # same-time true splits = split visits occurring at exact same time
    if not split_df.empty:
        split_df = clean_split_visits(split_df, true_split=True, same_time=True)
    
    # COMBINE DIFFERENT-TIME TRUE SPLITS ++++++++++++++++++++++++++++++++++++++++++++++++++++
    # different-time true splits = split visits occurring within 30 minutes of one another
    if not split_df.empty:
        split_df = clean_split_visits(split_df, true_split=True, same_time=False)
    
    # CLEAN FALSE SPLITS ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # false splits = split visits occurring more than 30 minutes from each other
    if not split_df.empty:
        split_df = clean_split_visits(split_df, true_split=False)
    
    # DROP SPLIT VISITS AND REPLACE WITH CLEANED SPLITS +++++++++++++++++++++++++++++++++++++
    df = df.drop(df[df['visit_id'].isin(split_visit_ids)].index)
    df = pd.concat([df, split_df.drop(columns='datetime')],
                   ignore_index=True).sort_values(by='visit_id').reset_index(drop=True)

    # drop remaining duplicate visits, if any
    df = df.drop(df[df.duplicated(subset='visit_id')].index).reset_index(drop=True)
    
    return df


# CLEANING ATYPICAL VISITS ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def drop_hki(df, db_cred):
    """
    Drop visits from Humankind employees and third-party vendors.

    Parameters
    ----------
    df : pd.DataFrame
        Visit-level data.
    db_cred : dict
        Dictionary of database credentials.
    """

    # DROP HUMANKIND EMPLOYEE VISITS ++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # read in ip addresses and locations of humankind employees
    cursor, conn = database_connect('hkiproc', db_cred)
    query = """SELECT * FROM ips ORDER BY name, description, start_date"""
    ips = pd.read_sql(query, conn)
    ips.ip = ips.ip.str.rsplit('.', n=2).str[0] + '.0.0'  # anonymize ips
    cursor.close()
    conn.close()

    # merge with visits of same ips and locations
    ip_grp = ips.groupby(['name', 'description', 'ip', 'city', 'region', 'country'])
    vis_grp = df.groupby(['ip', 'city', 'region', 'country', 'date'])
    ipvis = pd.merge(pd.concat([ip_grp.start_date.first(),
                                ip_grp.end_date.last().fillna('9999-99-99')],
                               axis=1).droplevel(['name', 'description']).reset_index(),
                     vis_grp.visit_id.unique().reset_index(), how='left',
                     on=['ip', 'city', 'region', 'country'])

    # isolate visits with select ip-locations within relevant date ranges
    ipvis = ipvis.drop(ipvis[(ipvis.date.astype(str) < ipvis.start_date) |
                             (ipvis.date.astype(str) > ipvis.end_date)].index)
    hki_visits = ipvis.visit_id.explode().tolist()

    # isolate visitors with offending visits
    hki_visitors = df[(df.referrer_type != 'campaign') &  # exclude campaign referrals
                      (df.visit_id.isin(hki_visits))].visitor_id.tolist()

    # drop non-campaign referral entries from humankind employees
    df.drop(df[(df.visitor_id.isin(hki_visitors))].index, inplace=True)

    # DROP VENDORS ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # drop yellow.system visitors
    ys_visits = df[df.country.isin(['Belarus', 'Armenia', 'Georgia'])].visit_id.tolist()
    ys_visitors = df[df.visit_id.isin(ys_visits)].visitor_id.tolist()
    df.drop(df[(df.visitor_id.isin(ys_visitors))].index, inplace=True)
    df.reset_index(drop=True, inplace=True)


def drop_dev(df, db_cred):
    """
    Drop visitors with any visits to the dev sites.

    Parameters
    ----------
    df : pd.DataFrame
        Visit-level data.
    db_cred : dict
        Dictionary of database credentials.
    """

    # get list of unique visitors to dev sites from action log
    cursor, conn = database_connect('hkiweb', db_cred)
    query = """select distinct visitor_id
    from action_log 
    where 
        (url not like '%humankind.co%'
        and url not like '%humankindfunds.com%')
        -- subdomain begins with dev
        or regexp_replace(url, '(https?://)?(www.)?', '') like 'dev%'
    """
    dev = pd.read_sql(query, conn)
    cursor.close()
    conn.close()

    # drop dev-site visitors
    df.drop(df[df.visitor_id.isin(dev.visitor_id)].index, inplace=True)
    df.reset_index(drop=True, inplace=True)


def drop_foreign(df):
    """
    Drop foreign visitors.

    Parameters
    ----------
    df : pd.DataFrame
        Visit-level data.
    """

    # count number of domestic and foreign visits per visitor
    domestic = df.groupby('visitor_id').country.apply(
        lambda x: [i for i in x if i == 'United States']).rename('domestic')
    foreign = df.groupby('visitor_id').country.apply(
        lambda x: [i for i in x if i != 'United States']).rename('foreign')

    # count visitors with more foreign than domestic visits as foreign
    foreign_visitors = foreign[foreign.str.len() > domestic.str.len()].index

    # drop foreign visitors
    df.drop(df[df.visitor_id.isin(foreign_visitors)].index, inplace=True)
    df.reset_index(drop=True, inplace=True)


# CLEANING ACTION FLOWS +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def clean_flow(df, action_type, actions, deltat=0):
    """
    Clean action flows for individual action type.

    Remove duplicate actions, i.e. consecutive actions of same type occurring
    within given time range, from action flows. Update action flow, timestamp, 
    count, and average duration columns with duplicate actions removed.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of website visits.
    action_type : str
        Type of action for which to clean flows. Valid options are 'pageview',
        'download', 'outlink_click', 'buyetf_click', 'brokerlink_click', 'video_action',
        and 'form_action'. An invalid action flow will cause the
        function to return without making any modifications to the dataframe.
    actions : pd.DataFrame
        Dataframe of individual actions of all type over all visits.
    deltat : int
        Maximum time difference, in seconds, between consecutive actions for which to 
        apply cleaning. Consecutive actions occurring within delta-t seconds of one 
        another will be cleaned, with the latter of the two being removed from the action flow. 
        Default of 0 cleans consecutive actions occurring at exactly the same time only.
    """

    # exit if action type not valid option
    if action_type not in ['pageview',
                           'download',
                           'outlink_click',
                           'buyetf_click',
                           'brokerlink_click',
                           'video_action',
                           'form_action',
                          ]: return df

    # get action string
    action_str = action_type
    if action_type == 'pageview': action_str = 'page'
    elif action_type.split('_')[-1] == 'click': action_str = action_type.split('_')[0]

    # get individual actions and timestamps of given type per visit
    acts_mask = (actions.action_flow.str.endswith('_' + action_type))
    if action_type == 'buyetf_click':
        acts_mask = (actions.action_flow == 'buyetf_click')
    elif action_type.split('_')[-1] == 'action':
        acts_mask = (actions.action_flow.str.split('_', n=1).str[-1].str.split('_').str[0] ==
                     action_type.split('_')[0])  # *_video/form_*
    acts = actions[acts_mask].rename(
        columns={col : col.replace('action', action_str) for col in actions.columns})
    acts[action_str + '_flow'] = acts[action_str + '_flow'].replace(
        '_' + action_type, '', regex=True)

    # find duplicate actions of given type and update action type flow/ts columns
    dupl_mask = ((actions.visit_id == actions.visit_id.shift()) &  # same visit id
                 (actions.action_flow == actions.action_flow.shift()) &  # same action 
                 (actions.action_ts_int - actions.action_ts_int.shift() <= deltat)  # time in range
                )        
    dupl_acts = actions.loc[dupl_mask & acts_mask]
    act_grp = acts.drop(dupl_acts.index).groupby('visit_id', group_keys=False)
    flow_cols = [action_str + '_ts']
    if action_type != 'buyetf_click': flow_cols = [action_str + '_flow'] + flow_cols
    for col in flow_cols:
        df[col] = act_grp[col].apply(lambda x: ','.join(x))
        df[col] = df[col].fillna('None')

    # update action type counts and average durations
    df[action_str + 's'] = df[action_str + '_ts'].apply(
        lambda x: 0 if x == 'None' else len(x.split(',')))
    if action_type != 'form_action':
        if action_type != 'pageview':  # modify page action duration instead
            df[action_str + '_duration'] = act_grp[action_str + '_duration'].sum()
            df[action_str + '_duration'] = df[action_str + '_duration'].fillna(0).astype(int)
        df['avg_' + action_str + '_duration'] = (df[action_str + '_duration'] /
                                                 df[action_str + 's']).fillna(0)
    if action_type == 'pageview':
        df.page_action_duration = act_grp[action_str + '_duration'].sum()
        df.page_action_duration = df.page_action_duration.fillna(0).astype(int)
        df.avg_page_action_duration = (df.page_action_duration / df.pages).fillna(0)
    elif action_type == 'form_action':
        df.avg_form_interaction_time = (df.form_interaction_time / df.form_actions).fillna(0)

    # update individual action type counts: subtract duplicate actions from corresponding columns
    dupl_acts = dupl_acts.drop(columns=['action_path_flow', 'action_ts'])
    if action_type == 'buyetf_click': return  # no further columns to update
    elif action_type.split('_')[-1] != 'action':
        dupl_acts.action_flow = dupl_acts.action_flow.str.replace(action_type, action_str + 's')
        if action_type == 'pageview':  # combine individual article post / company ranking pages
            dupl_acts.action_flow = dupl_acts.action_flow.apply(
                lambda x: re.sub('articles-.*_pages', 'article-post_pages', x)).apply(
                lambda x: re.sub('rankings-.*_pages', 'ranked-company_pages', x))
            dupl_acts.action_flow = np.select(  # map socially responsible pages to site homepages
                [(dupl_acts.action_flow == 'socially_responsible_pages') &
                 (dupl_acts.action_site_flow == 'humankind.co'),
                 (dupl_acts.action_flow == 'socially_responsible_pages') &
                 (dupl_acts.action_site_flow == 'humankindfunds.com')],
                ['humankind_pages', 'humankindfunds_pages'], default=dupl_acts.action_flow)
            dupl_acts = dupl_acts.loc[dupl_acts.action_flow != 'page-not-found_pages']
        elif action_type == 'outlink_click':  # combine categories of outlinks
            dupl_acts.action_flow = dupl_acts.action_flow.apply(
                lambda x: re.sub('(linkedin|instagram|youtube|facebook|twitter)_outlinks',
                                 'social_outlinks', x)).apply(
                lambda x: re.sub('(investor|adviserinfo.sec)_outlinks', 'crs_outlinks', x)).apply(
                lambda x: re.sub('(finra|sipc)_outlinks', 'disclosures_outlinks', x))
            # drop article outlinks: no good way to track this category
            df.drop(columns = [col for col in df.columns if
                               col.startswith('articles_outlink')], inplace=True)
        actcols = [col for col in df.columns if col.endswith('_' + action_str + 's')]
        dupl_actcts = dupl_acts.groupby('visit_id').action_flow.apply(lambda x: [i for i in x])
        dupl_actcts = pd.concat([dupl_actcts, pd.DataFrame(columns=actcols)], axis=1).fillna(0)
        for col in actcols:
            dupl_actcts[col] = dupl_actcts.action_flow.apply(
                lambda x: len([i for i in x if i == col]))
            df.loc[df.index.isin(dupl_actcts.index), col] = df[col] - dupl_actcts[col]
            df[col] = df[col].astype(float)
    else:  # handle video and form actions separately
        actpre = action_type.split('_')[0]
        if actpre == 'video': subs = ['play', 'pause', 'resume', 'seek', 'finish']
        elif actpre == 'form': subs = ['submission']
        subs = [actpre + '_' + i for i in subs]
        subcols = [col for col in df.columns for i in subs if
                   col == (i + 'es' if i.endswith('sh') else i + 's')]
        actcols = [col for col in df.columns for i in subcols if col.endswith('_' + i)]
        for icol, col in enumerate(subcols):
            dupl_acts.action_flow = dupl_acts.action_flow.str.replace(subs[icol], col)
        dupl_actcts = dupl_acts.groupby(
            'visit_id', group_keys=False).action_flow.apply(lambda x: [i for i in x])
        dupl_actcts = pd.concat(
            [dupl_actcts, pd.DataFrame(columns=subcols+actcols)], axis=1).fillna(0)
        for col in subcols:  # duplicate total subactions
            dupl_actcts[col] = dupl_actcts.action_flow.apply(
                lambda x: len([i for i in x if i.endswith('_' + col)]))
        for col in actcols:  # duplicate subactions by video/form
            dupl_actcts[col] = dupl_actcts.action_flow.apply(
                lambda x: len([i for i in x if i == col]))
        for col in subcols + actcols:
            df.loc[df.index.isin(dupl_actcts.index), col] = df[col] - dupl_actcts[col]
            df[col] = df[col].astype(float)
        if actpre == 'video':  # update average video columns
            df.avg_video_watch_time = (df.video_watch_time / df.video_plays).replace(
                np.inf, 0).fillna(0)

        
def clean_action_flows(df, deltat=0):
    """
    Clean action flows.

    Remove duplicate actions, i.e. consecutive actions of same type occurring at
    once, from action flows. Update action flow, timestamp, count, and average
    duration columns for total and individual action types with duplicate actions removed.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of website visits.

    Returns
    -------
    pd.DataFrame
        Dataframe of website visits with cleaned action flows.
    deltat : int
        Maximum time difference, in seconds, between consecutive actions for which to 
        apply cleaning. Consecutive actions occurring within delta-t seconds of one 
        another will be cleaned, with the latter of the two being removed from the action flow. 
        Default of 0 cleans consecutive actions occurring at exactly the same time only.
    """

    # set visit id as index
    df.set_index('visit_id', inplace=True)

    # clean action ts columns: replace '0.0' with 'None'
    for col in [col for col in df.columns if col.endswith('_ts')]:
        df[col] = df[col].replace('0.0', 'None')

    # clean up action path flow --> remove split entries for page-not-found pageviews
    bad_flows = df[df.action_flow.str.split(',').str.len() !=
                   df.action_path_flow.str.split(',').str.len()].action_path_flow
    df.loc[df.index.isin(bad_flows.index),
           'action_path_flow'] = bad_flows.str.rstrip(',').apply(
        lambda x: ','.join([i for i in x.split(',') if not
                            i.startswith('<svg') and i not in ['/)', "'"]]))

    # get individual actions and timestamps per visit
    actions = pd.concat([df.action_flow.apply(lambda x: x.split(',')).explode(),
                         df.action_site_flow.apply(lambda x: x.split(',')).explode(),
                         df.action_path_flow.apply(lambda x: x.split(',')).explode(),
                         df.action_ts.apply(lambda x: x.split(',')).explode(),
                         ], axis=1).sort_values(by=['visit_id', 'action_ts']).reset_index()
    actions['action_ts_int'] = actions.action_ts.fillna('None').replace('None', '0').astype(int)

    # find duplicate actions (consecutive same actions within time range) and update flow/ts columns
    dupl_mask = (
        (actions.visit_id == actions.visit_id.shift()) &  # same visit id
        (actions.action_flow == actions.action_flow.shift()) &  # same action
        (actions.action_ts_int - actions.action_ts_int.shift() <= deltat)  # timestamps in range
        )
    act_clean = actions.drop(actions.loc[dupl_mask].index)
    act_clean['action_duration'] = act_clean.groupby(
        'visit_id').action_ts_int.diff(1).shift(-1).abs()
    actions['action_duration'] = act_clean['action_duration']
    act_grp = act_clean.groupby('visit_id')
    for col in ['action_flow', 'action_site_flow', 'action_path_flow', 'action_ts']:
        df[col] = act_grp[col].apply(lambda x: ','.join(x))

    # update action count, action duration, and average duration columns
    df.actions = df.action_flow.apply(lambda x: 0 if x == 'None' else len(x.split(',')))
    df.action_duration = act_grp.action_duration.sum()
    df.action_duration = df.action_duration.fillna(0).astype(int)
    df.avg_action_duration = (df.action_duration / df.actions).fillna(0)

    # clean individual action type flows
    for action_type in ['pageview',
                        'download',
                        'outlink_click',
                        'buyetf_click',
                        'brokerlink_click',
                        'video_action',
                        'form_action',
                        ]: clean_flow(df, action_type, actions, deltat)

    # reset index
    df.reset_index(inplace=True)


def clean_standalone_action(df, action_type, deltat=0):
    """
    Clean individual action type flow and update overall action flow.

    Remove duplicate actions of given type, i.e. consecutive actions occurring 
    within given time range, from overall and specific action flows. 
    Update action flow, timestamp, count, and average duration columns with 
    duplicate actions removed.

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe of website visits.
    action_type : str
        Type of action for which to clean flows. Valid options are 'pageview',
        'download', 'outlink_click', 'buyetf_click', 'brokerlink_click', 
        'video_action', and 'form_action'. An invalid action flow will cause the
        function to return without making any modifications to the dataframe.
    deltat : int
        Maximum time difference, in seconds, between consecutive actions for which to 
        apply cleaning. Consecutive actions occurring within delta-t seconds of one 
        another will be cleaned, with the latter of the two being removed from the action flow. 
        Default of 0 cleans consecutive actions occurring at exactly the same time only.
    """

    # set visit id as index
    df.set_index('visit_id', inplace=True)
    
    # get individual actions and timestamps per visit
    actions = pd.concat([df.action_flow.apply(lambda x: x.split(',')).explode(),
                         df.action_site_flow.apply(lambda x: x.split(',')).explode(),
                         df.action_path_flow.apply(lambda x: x.split(',')).explode(),
                         df.action_ts.apply(lambda x: x.split(',')).explode(),
                         ], axis=1).sort_values(by=['visit_id', 'action_ts']).reset_index()
    actions['action_ts_int'] = actions.action_ts.fillna('None').replace('None', '0').astype(int)
    
    # get individual actions and timestamps of given type per visit
    acts_mask = (actions.action_flow.str.endswith('_' + action_type))
    if action_type == 'buyetf_click':
        acts_mask = (actions.action_flow == 'buyetf_click')
    elif action_type.split('_')[-1] == 'action':
        acts_mask = (actions.action_flow.str.split('_', n=1).str[-1].str.split('_').str[0] ==
                     action_type.split('_')[0])  # *_video/form_*
    
    # find duplicate actions (consecutive same actions within time range) and update flow/ts columns
    dupl_mask = (
        (actions.visit_id == actions.visit_id.shift()) &  # same visit id
        (actions.action_flow == actions.action_flow.shift()) &  # same action
        (actions.action_ts_int - actions.action_ts_int.shift() <= deltat)  # timestamps in range
        )
    # drop duplicate actions of given type
    act_clean = actions.drop(actions.loc[dupl_mask & acts_mask].index)
    act_clean['action_duration'] = act_clean.groupby(
        'visit_id').action_ts_int.diff(1).shift(-1).abs()
    actions['action_duration'] = act_clean['action_duration']
    act_grp = act_clean.groupby('visit_id')
    for col in ['action_flow', 'action_site_flow', 'action_path_flow', 'action_ts']:
        df[col] = act_grp[col].apply(lambda x: ','.join(x))

    # update action count, action duration, and average duration columns
    df.actions = df.action_flow.apply(lambda x: 0 if x == 'None' else len(x.split(',')))
    df.action_duration = act_grp.action_duration.sum()
    df.action_duration = df.action_duration.fillna(0).astype(int)
    df.avg_action_duration = (df.action_duration / df.actions).fillna(0)
    
    # clean individual action type flow
    clean_flow(df, action_type, actions, deltat)
    
    # reset index
    df.reset_index(inplace=True)
    


# VISITOR-LEVEL DATA ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def categorize_visitor_action_flow(df):
    """
    Categorize visitor-level action flows - map specific actions to categories.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw visitor-level data.
    """
    
    # separate actions
    adf = df.action_flow.str.split(',').explode()
    
    # map actions to categories
    subs = {r'^(.*)_socially_responsible_pageview$' :
            r'\1_pageview',
            r'^articles-.*_pageview$' :
            'articles-post_pageview',
            r'^rankings_.*_pageview$' :
            'rankings_pageview',
            r'^rankings-.*_pageview$' :
            'rankings-company_pageview',
            r'^.*\.(jpg|png|eps)_download$' :
            'logo_download',
            r'^(linkedin|youtube|twitter|instagram|facebook)_outlink_click$' :
            'social_outlink_click',
            r'^(adviserinfo\.sec|sipc|finra|investor)_outlink_click$' :
            'compliance_outlink_click',
            r'^(theconversation|benefitcorporationreduced|onlinelibrary\.wiley)_outlink_click$' :
            'articles_outlink_click',
            r'^(.*)_video_.*$' :
            r'\1_video_action',
            r'^(.*)_form_.*$' :
            r'\1_form_action',
           }
    for sub in subs.items():
        adf = adf.apply(lambda x: re.sub(r'^{}$'.format(sub[0]), sub[1], x))
        
    # regroup actions and insert new categorical column into dataframe
    adf = adf.groupby('visitor_id').apply(lambda x: ','.join(x))
    df.insert(df.columns.get_loc('action_flow')+1, 'action_category_flow', adf)


def clean_visitor_action_flow(df):
    """
    Clean raw visitor-level action flows - map extraneous actions.
    
    Parameters
    ----------
    df : pd.DataFrame
        Raw visitor-level data.
    """
    
    # build dataframe of individual actions
    adf = pd.concat([df.action_flow.str.split(',').explode(), 
                     df.action_site_flow.str.split(',').explode(),
                     df.action_ts.str.split(',').explode(),
                    ], axis=1)

    # map socially responsible pages to proper homepages
    srpg = 'socially_responsible_pageview'
    for site in ['humankind.co', 'humankindfunds.com']:
        adf.loc[(adf.action_flow == srpg) & (adf.action_site_flow == site),
                'action_flow'] = site.split('.')[0] + '_' + srpg

    # map original rankings company pages to corresponding year
    adf.action_flow = np.where((adf.action_flow.str.startswith('rankings-')) &
                               (adf.action_flow.str.endswith('_pageview')),
                               adf.action_flow.str.replace('_pageview', '-2022_pageview'),
                               adf.action_flow)
        
    # map article post and rankings company pageviews with bad urls to page-not-found
    fpats = ['^articles-', '^rankings-']
    bpat = '_pageview$'
    for fpat in fpats:
        pgmask = (adf.action_flow.apply(lambda x: bool(re.match(r'{}.*{}'.format(fpat, bpat), x))))
        if fpat[1:-1] == 'articles':
            patmask = (~(adf.action_flow.apply(lambda x: bool(
                re.match(r'({}(?=.*?\-)[a-z0-9\-]*{})'.format(fpat, bpat), x)))) |
                       (adf.action_flow.apply(lambda x: bool(
                           re.match(r'({}frame-[a-z0-9]*{})'.format(fpat, bpat), x)))))
        elif fpat[1:-1] == 'rankings':
            patmask = ~(adf.action_flow.apply(
                lambda x: '-' in re.sub(r'-[\d]{4}', '', x.replace('rankings-', ''))))
        adf.loc[pgmask & patmask, 'action_flow'] = 'page-not-found_pageview'
        
    # map article link downloads to outlink clicks
    link_dls = ['benefitcorporationreduced']
    for link_dl in link_dls:
        adf.loc[adf.action_flow == '{}_download'.format(link_dl),
                'action_flow'] = '{}_outlink_click'.format(link_dl)
        
    df.action_flow = adf.groupby('visitor_id').action_flow.apply(lambda x: ','.join(x))
    
    
def build_raw_visitor_data(vdf):
    """
    Build raw visitor-level data set.

    Raw visitor data = time-ordered list of visits and activities across customer lifetime.
    
    Parameters
    ----------
    vdf : pd.DataFrame
        Raw visit-level data.

    Returns
    -------
    pd.DataFrame
        Raw visitor-level data.
    """

    # initialize dataframe
    df = pd.DataFrame()

    # copy input dataframe (avoid modifying original)
    vdf = vdf.copy()

    # add necessary columns to input dataframe
    vdf['datetime'] = vdf.date.astype(str) + ' ' + vdf.time
    vdf['timestamp'] = vdf.datetime.apply(lambda x: eastern.localize(
        datetime.strptime(x, '%Y-%m-%d %H:%M:%S')).timestamp()).astype(int)
    vdf['bounce'] = (vdf.visit_duration == 0).astype(int)
    vdf['true_bounce'] = ((vdf.visit_duration == 0) &
                          (vdf.actions - vdf.pages == 0) & (vdf.pages < 2)).astype(int)
    vdf['mobile'] = (vdf.device_category == 'mobile').astype(int)
    vdf['desktop'] = (vdf.device_category == 'desktop').astype(int)
    dict_cols = {'location' : ['city', 'region', 'country', 'continent'],
                 'campaign' : [col for col in vdf.columns if col.startswith('campaign')]}
    for out_col, in_cols in dict_cols.items():
        vdf[out_col] = vdf[in_cols].apply(lambda x: ','.join(x), axis=1)
        vdf[out_col] = vdf[out_col].apply(
            lambda x: {in_cols[i] : x.split(',')[i] for i in range(len(in_cols))})
    
    # add engagement types
    if 'engagement_type' not in vdf.columns:
        visit_engagement = assign_cluster(vdf).reset_index()
        vdf = vdf.merge(visit_engagement, how='left', on='visit_id')
    vdf['engagement_type'] = vdf.engagement_type.str.replace(',', '').str.replace(' ', '_')
    
    # modify flow columns in input dataframe to include session starts/ends
    flows = ['action', 'action_site', 'page']
    for flow in flows:
        vdf[flow + '_flow'] = 'session-start,' + vdf[flow + '_flow'] + ',session-end'
    for flow in [flow for flow in flows if flow != 'action_site']:
        vdf[flow + '_ts'] = '0,' + vdf[flow + '_ts'] + ',1'
    
    # group by visitor id in order of visit
    grp = vdf.sort_values(by='visit_id').groupby('visitor_id')

    # visitor lifetime
    df['datetime'] = grp.datetime.agg(list)
    df['timestamp'] = grp.timestamp.agg(list)
    df['day'] = grp.day.agg(list)
    df['visit_trade_hours'] = grp.visit_trade_hours.agg(list)
    
    # visits
    df['visits'] = grp.visit_count.max()
    df['visit_count'] = grp.visit_count.agg(list)
    df['visit_id'] = grp.visit_id.agg(list)
    df['visit_duration'] = grp.visit_duration.agg(list)
    
    # bounce rates
    df['bounce'] = grp.bounce.agg(list)
    df['bounce_rate'] = grp.bounce.sum().div(df.visits)
    df['true_bounce'] = grp.true_bounce.agg(list)
    df['true_bounce_rate'] = grp.true_bounce.sum().div(df.visits)

    # devices
    df['device_category'] = grp.device_category.agg(list)
    df['mobile_desktop_ratio'] = grp.mobile.sum().div(grp.desktop.sum()).replace(np.inf, 0)
    
    # locations
    df['location'] = grp.location.agg(list)
    
    # referrals
    df['referrer_type'] = grp.referrer_subtype.agg(list)
    df['referrer_website'] = grp.referrer_website_url.agg(list)
    df['referrer_social_network'] = grp.referrer_social_network_name.agg(list)
    df['referrer_search_engine'] = grp.referrer_search_engine_name.agg(list)
    df['referrer_search_engine_keyword'] = grp.referrer_search_engine_keyword.agg(list)
    df['campaign'] = grp.campaign.agg(list)

    # actions
    df['actions'] = grp.actions.agg(list)
    df['action_duration'] = grp.action_duration.agg(list)
    df['page_duration'] = grp.page_duration.agg(list)
    df['page_action_duration'] = grp.page_action_duration.agg(list)
    df['action_flow'] = grp.action_flow.apply(lambda x: ','.join(x))
    df['action_site_flow'] = grp.action_site_flow.apply(lambda x: ','.join(x))
    df['action_ts'] = grp.action_ts.apply(lambda x: ','.join(x))
        
    # engagement types
    df['engagement_flow'] = grp.engagement_type.apply(lambda x: ','.join(x))

    # clean and categorize action flows
    clean_visitor_action_flow(df)
    categorize_visitor_action_flow(df)
    
    return df


def get_asset_urls(url, urls):
    """
    Get URLs of all assets on advisor site.
    
    Parameters
    ----------
    url : str
        Main assets page URL.
    urls : list of str
        List of assets urls. This list is changed in place.
    """
    
    # recursively loop through assets folders to get urls
    response = requests.request('GET', url)
    content = response.content
    soup = BeautifulSoup(content, 'html.parser')
    divs = soup.find_all('div', class_=re.compile('assets_folder__[a-zA-Z0-9]*'))
    for div in divs:
        links = div.find_all('a')
        for link in links:
            new_url = os.path.join(url, link.string)
            urls.append(new_url)
            get_asset_urls(new_url, urls)


def get_action_category_map():
    """
    Build numerical mapping for categorical action flows.
    
    Returns
    -------
    dict of {str : int}
        Dictionary mapping categorical actions to integers.
    """
    
    # replace hardcoding for some actions, i.e. downloads, brokerlinks, with site scraping (?)
    action_dict = {
        'pageview' : ['humankind', 'mission', 'research', 'team', 'articles',
                      'articles-post', 'rankings', 'rankings-company', 'humankindfunds',
                      'etf-explanation', 'topcompanies', 'shareholders', 'tax-information',
                      'investors', 'contact', 'relationship', 'terms', 'page-not-found'],
        'download' : ['summaryprospectus', 'prospectus', 'prospectussupplement',
                      'sai', 'methodology', 'factsheet', 'premiumdiscountchart',
                      'quarterlyreport', 'semiannualreport', 'annualreport', 'benefitreport',
                      '8937', 'holdings', 'crs', 'logo'],
        'outlink_click' : ['social', 'compliance', 'articles'],
        'click' : ['buyetf'],
        'brokerlink_click' : ['robinhood', 'fidelity', 'vanguard', 'schwab',
                              'tdameritrade', 'etrade', 'interactivebrokers'],
        'video_action' : ['humankind-short', 'humankind', 'wtf-short', 'wtf'],
        'form_action' : ['getstarted', 'newsletter', 'contactus', 'institutionalcontact'],
    }
    
    action_list = []
    for action_type, actions in action_dict.items(): 
        actions = [action + '_' + action_type for action in actions]
        for action in actions: action_list.append(action)
    action_list += ['session-start', 'session-end', 'None']
    
    return {action : i for i, action in enumerate(action_list)}


def get_action_map():
    """
    Build numerical mapping for full action flows.
    
    Returns
    -------
    dict of {str : int}
        Dictionary mapping granular actions to integers.
    """

    # grab individual article posts in order of appearance on site
    url = 'https://www.humankind.co/articles'
    response = requests.request('GET', url)
    content = response.content
    soup = BeautifulSoup(content, 'html.parser')
    article_list = []
    for link in soup.find_all('a'):
        href = link.get('href').strip('/')
        if href.startswith('articles/') and not link.get('class'):
            article_list.append(href.replace('/', '-') + '_pageview')
    
    # grab individual company rankings in order of rank and year on site
    url = 'https://rankings.humankind.co/{}'
    year_list = [str(i) for i in range(2022, int(datetime.now().astimezone(eastern).year)+1)]
    ranking_list = []
    for year in year_list:
        year_url = url.format(year)
        response = requests.request('GET', year_url)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        data = soup.find_all('script', id='__NEXT_DATA__')[0].contents[0]
        data = json.loads(data)
        if 'companies' in data['props']['pageProps']:
            for company in data['props']['pageProps']['companies']['items']:
                ranking_list.append('rankings-' + company['slug'] + '_pageview')

    # grab individual logo downloads in order of appearance on site
    url = 'https://www.humankind.co/assets'
    asset_urls = []
    get_asset_urls(url, asset_urls)
    logo_list = []
    for url in asset_urls:
        response = requests.request('GET', url)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        for link in soup.find_all('a'): 
            href = link.get('href')
            if not href: continue
            href = href.strip('/')
            if href.startswith('assets'): logo_list.append(re.sub(
                    r'(hknd|humankind|[\d_%]+)', '', href.split('/')[-1].lower()) + '_download')

    # expand individual social and compliance outlinks
    outlink_list = ['facebook', 'twitter', 'instagram', 'linkedin', 'youtube',
                    'investor', 'adviserinfo.sec', 'finra', 'sipc',
                    'theconversation', 'benefitcorporationreduced', 'onlinelibrary.wiley']
    outlink_list = [outlink + '_outlink_click' for outlink in outlink_list]
    # --> scrape rest of outlinks from site (?)

    # expand video actions to individual plays, pauses, resumes, seeks, and finishes
    video_list = []
    for video in ['humankind-short', 'humankind', 'wtf-short', 'wtf']:
        for video_act in ['video_play', 'video_pause', 'video_resume', 'video_seek',
                          'video_finish']: video_list.append(video + '_' + video_act)

    # expand form actions to individual interactions and submissions
    form_list = []
    for form in ['getstarted', 'newsletter', 'contactus', 'institutionalcontact']:
        for form_act in ['form_interaction', 'form_submission']:
            form_list.append(form + '_' + form_act)

    # build full action list
    action_list = [i for i in get_action_category_map()]
    article_index = action_list.index('articles-post_pageview')
    action_list[article_index:article_index] = article_list
    action_list.remove('articles-post_pageview')
    ranking_index = action_list.index('rankings-company_pageview')
    action_list[ranking_index:ranking_index] = ranking_list
    action_list.remove('rankings-company_pageview')
    logo_index = action_list.index('logo_download')
    action_list[logo_index:logo_index] = logo_list
    action_list.remove('logo_download')
    outlink_index = action_list.index('social_outlink_click')
    action_list[outlink_index:outlink_index] = outlink_list
    for ol in ['social_outlink_click', 'articles_outlink_click', 'compliance_outlink_click']:
        action_list.remove(ol)
    video_index = action_list.index('humankind-short_video_action')
    action_list[video_index:video_index] = video_list
    for vid in ['humankind-short_video_action', 'humankind_video_action',
                'wtf-short_video_action', 'wtf_video_action']:
        action_list.remove(vid)
    form_index = action_list.index('getstarted_form_action')
    action_list[form_index:form_index] = form_list
    for frm in ['getstarted_form_action', 'newsletter_form_action',
                'contactus_form_action', 'institutionalcontact_form_action']:
        action_list.remove(frm)
    for hmpg in ['humankind', 'humankindfunds']: action_list.insert(
            action_list.index(hmpg + '_pageview')+1, hmpg + '_socially_responsible_pageview')

    # map actions to numbers
    return {action : i for i, action in enumerate(action_list)}


def get_site_map():
    """
    Build numerical mapping for site flows.
    
    Returns
    -------
    dict of {str : int}
        Dictionary mapping sites to integers.
    """
    
    site_list = ['humankind.co', 'rankings.humankind.co', 'humankindfunds.com',
                 'session-start', 'session-end', 'None']
    return {site : i for i, site in enumerate(site_list)}


def get_engage_map():
    """
    Build numerical mapping for engagement flows.
    
    Returns
    -------
    dict of {str : int}
        Dictionary mapping engagement types to integers.
    """
    
    return {val.replace(',', '').replace(' ', '_') : key for
            key, val in get_cluster_grades().engagement_type.to_dict().items()}


def map_action_flow(df, colstr='', action_types=[], drop_sessions=False, drop_none=False):
    """
    Map action flows to numerical sequences.

    Parameters
    ----------
    df : pd.DataFrame
        Raw visitor-level data.
    colstr : str
        String to replace 'action' in action flow column names.
    action_types : list of str
        Action types to include in flows.
    drop_sessions : bool
        Whether to drop 'session-start' and 'session-end' from action flows.
    drop_none : bool
        Whether to drop 'None' from action flows.

    Returns
    -------
    pd.DataFrame
        Dataframe of numerical sequences of given action type flows.
    """
    
    action_flow = []
    actflow_cols = ['action_flow', 'action_category_flow', 'action_site_flow', 'action_ts']
    for col in actflow_cols: action_flow.append(df[col].str.split(',').explode())
    action_flow = pd.concat(action_flow, axis=1).reset_index()
    
    # filter action flow based on action types
    pat_ix = pd.Index([])  # select actions of given types 
    pat = r'.*_({})'.format('|'.join(action_types))
    pat_ix = action_flow.loc[action_flow.action_flow.apply(
        lambda x: bool(re.match(pat, x)))].index
    sess_ix = pd.Index([])  # select session-starts/ends
    if not drop_sessions: sess_ix = action_flow.loc[
            action_flow.action_flow.isin(['session-start', 'session-end'])].index
    none_ix = pd.Index([])  # select None's
    if not drop_none: none_ix = action_flow.loc[
            action_flow.action_flow == 'None'].index
    drop_ix = action_flow.index.difference(pat_ix.union(sess_ix).union(none_ix))  # drop other ix
    action_flow = action_flow.drop(drop_ix)
    
    # map actions to numbers
    action_flow.action_flow = action_flow.action_flow.map(get_action_map())
    action_flow.action_category_flow = action_flow.action_category_flow.map(
        get_action_category_map())
    action_flow.action_site_flow = action_flow.action_site_flow.map(get_site_map())
    
    # drop rows with missing values
    action_flow = action_flow.drop(action_flow[action_flow.isnull().any(axis=1)].index)
    action_flow[actflow_cols[:-1]] = action_flow[actflow_cols[:-1]].astype(int).astype(str)
    
    # group actions by visitor id to build numerical sequence columns
    vdf = pd.DataFrame()
    for col in actflow_cols:
        outcol = col.replace('action', colstr) if colstr else col
        vdf[outcol] = action_flow.groupby('visitor_id')[col].apply(lambda x: ','.join(x))
    
    return vdf


def map_engage_flow(df):
    """
    Map engagement flows to numerical sequences.

    Parameters
    ----------
    df : pd.DataFrame
        Raw visitor-level data.

    Returns
    -------
    pd.DataFrame
       Numerical sequences of engagement types across visits.
    """
    
    engage_flow = df.engagement_flow.str.split(',').explode()
    engage_flow = engage_flow.map(get_engage_map()).astype(str)
    engage_flow = pd.DataFrame(engage_flow.groupby('visitor_id').apply(lambda x: ','.join(x)))
    
    return engage_flow


def build_processed_visitor_data(visits=None, visitors=None, drop_sessions=False, drop_none=False):
    """
    Build processed visitor-level data set.

    Processed visitor data = summary data and numerical sequences representing customer journeys.
    
    Parameters
    ----------
    visits : pd.DataFrame
        Raw visit-level data. If none passed in, must pass in raw visitor-level data instead.
    visitors : pd.DataFrame
        Raw visitor-level data. If none passed in, will build on the fly.
    drop_sessions : bool
        Whether to drop 'session-start' and 'session-end' from action flows.
    drop_none : bool
        Whether to drop 'None' from action flows.

    Returns
    -------
    pd.DataFrame
        Processed visitor-level data.
    """

    # get raw visitor-level data
    if visitors is None:
        if visits is None: raise Exception('Must pass in either raw visit- or visitor-level data.')
        visitors = build_raw_visitor_data(visits)

    df = visitors.copy()

    # get summary data
    df.actions = df.action_category_flow.apply(
        lambda x: len([i for i in x.split(',') if not i.startswith('session-') and i != 'None']))
    for action in ['pageview', 'download', 'outlink_click', 'buyetf_click',
                   'brokerlink_click', 'video_action', 'form_action']:
        df[action + 's'] = df.action_category_flow.apply(
            lambda x: len([i for i in x.split(',') if i.endswith('_' + action)]))
    for duration in ['visit_duration', 'action_duration',
                     'page_duration', 'page_action_duration']:
        df[duration] = df[duration].apply(lambda x: sum(x))

    df.timestamp = df.timestamp.explode().astype(str).groupby('visitor_id').apply(
        lambda x: ','.join(x))  # transform from list to comma separated string

    # map visit flows to numerical sequences
    maps = [
        dict(zip(calendar.day_name, [str(i) for i in range(7)])),
        {hr : str(i) for i, hr in enumerate(['preopening', 'early', 'core', 'late', 'None'])},
        {dc : str(i) for i, dc in enumerate(np.sort(df.device_category.explode().unique()))},
        {rt : str(i) for i, rt in enumerate(sorted(
            sorted(df.referrer_type.explode().unique()), key=lambda s: s.split('_')[-1]))},
        ]
    cols = ['day', 'visit_trade_hours', 'device_category', 'referrer_type']
    for i, col in enumerate(cols):
        df[col] = df[col].apply(lambda x: ','.join(list(map(maps[i].get, x))))
        
    # map action and engagement flows to numerical sequences
    action_flow = map_action_flow(df, drop_sessions=drop_sessions, drop_none=drop_none)
    page_flow = map_action_flow(df, colstr='page', action_types=['pageview'],
                                drop_sessions=drop_sessions, drop_none=drop_none)
    engage_flow = map_engage_flow(df)

    # drop original columns and replace with transformations
    df = df.drop(columns=[col for col in df.columns if col in
                          list(action_flow.columns) +
                          list(page_flow.columns) +
                          list(engage_flow.columns)])
    df = pd.concat([df, action_flow, page_flow, engage_flow], axis=1)    

    return df

    
# MODEL FOR ENGAGEMENT TYPES ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def load_default_model():
    """
    Load visit-level engagement types model and corresponding scaler.

    Returns
    -------
    sklearn.estimator
        Fitted Gaussian mixture model.
    sklearn.preprocessor
        Fitted StandardScaler that includes feature names.
    """
    
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    d = '2023-04-02'
    scaler = load(os.path.join(data_path,'gmm_scaler_{}.joblib'.format(d)))
    clf = load(os.path.join(data_path,'gmm_{}.joblib'.format(d)))

    return clf, scaler


def get_engagement_features(scaler=None):
    """
    Get feature names of required for classifying visit engagement types.

    Parameters
    ----------
    scaler : sklearn.preprocessor
        Fitted StandardScaler with feature names.
    
    Returns
    -------
    list of str
        List of feature names.
    """

    if scaler is None: _, scaler = load_default_model()

    scaler_features = scaler.feature_names_in_.tolist()
    bounce_features = ['visit_count',
                       'visit_duration',
                       'action_duration',
                       'pages',
                       'downloads',
                       'brokerlinks',
                       'video_pauses',
                       'video_resumes',
                       ]
    visit_features = ['visit_id', 'date']
    calc_features = ['articles_page_action_duration',
                     'article-post_page_action_duration',
                     'seconds_since_first_visit',
                     'seconds_since_last_visit',
                     'page_action_duration',
                     'humankind_page_action_duration',
                     'humankindfunds_page_action_duration',
                     ]

    return list(set(scaler_features + bounce_features + visit_features + calc_features))

    
def get_bounce_mask(df):
    """
    Create mask for 'new, bounce' cluster

    Parameters
    ----------
    df : pd.DataFrame
        Visit-level data.

    Returns
    -------
    bounce_mask : pd.Series
        Mask for selecting the bounce visits out of the df.
    """
    
    # check that the required columns are present in the dataframe
    col = ['visit_duration',
           'action_duration',
           'downloads',
           'video_resumes',
           'brokerlinks',
           'visit_count',
           'pages',
           ]
    assert all(c in list(df) for c in col), "One or more columns are missing from df"
    bounce_mask= (((df['visit_duration']==0) | (df['action_duration']==0)) &
                  (df['downloads']==0) & (df['brokerlinks']==0) &
                  (df['visit_count']==1) & (df['pages']<=1) & (df['video_resumes']==0))
    return bounce_mask


def get_cluster_names(date=''):
    """
    Provide a map between cluster ids and the names assigned to those clusters.

    Parameters
    ----------
    date : str
        The final date for the data set used to derive the names.
    
    Returns
    -------
    names : pd.Series
        Series mapping engagement type numbers to names. Internal name allows
        use as column upon merging with dataframe.
    """
    
    if date== '2022-10-23':
        names = pd.Series({
            0: 'new, low engagement', 
            5: 'return, 1pg, no action',
            12: 'scrolling pgs with vids',
            7: 'browsing home pgs',
            19: 'ETF, brokerlinks',  # small chance brokerlink?
            11: 'ETF, just looking',  # no vids, brokerlinks, downloads. Similar chance of seeing either home pg. 
            17: 'return, low engagement', 
            9: 'article reading', 
            3: 'new, downloads',
            8: 'browsing home pgs',
            16: 'brokerlinks, articles',
            1: 'video watching',
            6: 'downloads, brokerlink',
            13: 'new, visiting many pgs',
            18: 'broad engagement except downloads',
            2: 'get started form',
            10: 'downloads, brokerlink', 
            14: 'research and articles',
            15: 'downloads, videos, team pg, get started',
            4: 'downloads, videos, team pg, get started'
            },name='engagement_type')
    else:
        names= pd.Series({
            1: 'new, auto video', 
            9: 'return, 1pg, no action',
            0: 'browsing home pgs',
            4: 'new, low chance of download',
            6: 'return to advisor home and explore pages', 
            5: 'scrolling advisor home',
            8: 'brief return, low chance of download',
            7: 'new, exploratory',
            3: 'likely to click brokerlink',
            11: 'article reading, other exploration',
            2: 'exploratory, high chance of download',
            10: 'broad, long engagement', 
            },name='engagement_type')
        
    return names
    
    
def assign_cluster(visit, scaler=None, clf=None, cluster_names=None):
    """
    Assign each visit to a cluster based on the trained clustering model.

    Parameters
    ----------
    visit : pd.DataFrame
        Visit-level data. Some features will be normalized to be used as inputs
        for the classifier. If the dataset is too different from the original 
        data set (from 2021-04-01 to 2022-09-20) the scaling may lead to 
        inconsistent results from the classifier
    scaler : sklearn.preprocessor, optional
        Fitted StandardScaler that includes feature names. The default is the
        most recent fitted StandardScaler.
    clf : sklearn.estimator, optional
        Fitted Gaussian mixture model. The default is the most recent fitted 
        model.
    cluster_names : pd.Series, optional.
        A map from cluster id to name. The default is the most recent map.

    Returns
    -------
    engagement : pd.DataFrame
        The index is visit_id and the only column is engagement_type.
    
    Example
    -------
    assign engagement type and merge with the rest of the data:
        engagement= analy_utils.assign_cluster(visit)
        visit.set_index('visit_id', inplace=True)
        visit= visit.join(engagement, how='inner')
    """

    if clf is None or scaler is None: clf, scaler = load_default_model()
    if cluster_names is None: cluster_names = get_cluster_names('')
        
    #check for required features
    if 'articles_duration' not in visit.columns:
        #combine all article time
        visit['articles_duration']= visit.loc[:, [
            'articles_page_action_duration', 'article-post_page_action_duration']].sum(axis=1)
    if 'minutes_since_last_visit' not in visit.columns:
        #convert seconds to minutes
        for col in ['seconds_since_first_visit', 'seconds_since_last_visit']:
            visit['minutes_'+ col.split('_', 1)[1]]= visit[col]/60
            
    visit['other_page_duration']= visit['page_action_duration']- visit[
        ['humankind_page_action_duration',
         'humankindfunds_page_action_duration',
         'articles_duration']].sum(axis=1)
    #change negative values to 0
    visit['other_page_duration']= np.where(visit['other_page_duration']<0, 0, visit['other_page_duration'])
    
    #check that all features are present in the input data
    missing_features= [c for c in scaler.feature_names_in_ if c not in visit.columns]
    assert len(missing_features)==0, f"The following features are missing from visit: {missing_features}"
    
    #fill null values if they exist in these columns
    visit[scaler.feature_names_in_] = visit[scaler.feature_names_in_].fillna(0)
    
    #let the first cluster be the bounce cluster for non-returning visits
    bounce_mask= get_bounce_mask(visit)
    df_bounce= visit.loc[bounce_mask, ['visit_id','date']]
    df_bounce['engagement_type']= "new, bounce"
    df= visit.loc[~bounce_mask, ['visit_id'] + list(scaler.feature_names_in_)]
    
    #apply the preprocessor and the model
    X= scaler.transform(df[scaler.feature_names_in_])
    df['cluster_id']= clf.predict(X)
    
    #assign the names based on cluster id to the corresponding visits
    df= df.merge(cluster_names, how='left', 
                 left_on='cluster_id', right_index=True)
    
    engagement= pd.concat([df[['visit_id','engagement_type']], 
                    df_bounce[['visit_id','engagement_type']]], 
                   ignore_index=True, axis=0)
    engagement.set_index('visit_id', inplace=True)
    return engagement


def get_cluster_grades():
    """
    Get the look up table for the grade and engagement score of each engagement
    type

    Returns
    -------
    grade : pd.DataFrame
        1 row for each engagement type, 3 columns.

    """
    grade= pd.DataFrame([
        ['new, low chance of download', 'A'],
        ['likely to click brokerlink', 'A'],
        ['return, 1pg, no action','A'],
        ['new, exploratory', 'A'],
        
        ['exploratory, high chance of download', 'B+'],
        
        ['article reading, other exploration', 'B'], 
        ['browsing home pgs', 'B'],
        ['new, auto video', 'B'],
        
        ['brief return, low chance of download', 'C'],
        
        ['scrolling advisor home', 'D'],
        ['return to advisor home and explore pages','D'], 
        ['broad, long engagement', 'D'],
        
        ['new, bounce', 'F']], 
        columns=['engagement_type','grade'])
    
    value= pd.DataFrame([
        [4, 'A'],
        [3, 'B'],
        [3.2, 'B+'],
        [2, 'C'],
        [1, 'D'],
        [0, 'F']], 
        columns=['engagement_score','grade'])
    grade= grade.merge(value, how='left', on='grade')
    
    return grade

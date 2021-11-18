# USGS_USGS_MYB_SandGravelInd.py (flowsa)
# !/usr/bin/env python3
# coding=utf-8

"""
Projects
/
FLOWSA
/

FLOWSA-314

Import USGS Mineral Yearbook data

Description

Table T1

SourceName: USGS_MYB_SandGravelInd
https://www.usgs.gov/centers/nmic/silica-statistics-and-information

Minerals Yearbook, xls file, tab T1:
Data for:
Sand and Gravel; sand and gravel (industrial)

Years = 2014+
"""
import io
import pandas as pd
from flowsa.flowbyfunctions import assign_fips_location_system
from flowsa.data_source_scripts.USGS_MYB_Common import *

SPAN_YEARS = "2014-2018"


def usgs_sgi_url_helper(build_url, config, args):
    """
    This helper function uses the "build_url" input from flowbyactivity.py,
    which is a base url for data imports that requires parts of the url text
    string to be replaced with info specific to the data year. This function
    does not parse the data, only modifies the urls from which data is
    obtained.
    :param build_url: string, base url
    :param config: dictionary, items in FBA method yaml
    :param args: dictionary, arguments specified when running flowbyactivity.py
        flowbyactivity.py ('year' and 'source')
    :return: list, urls to call, concat, parse, format into Flow-By-Activity
        format
    """
    url = build_url
    return [url]


def usgs_sgi_call(url, r, args):
    """
    Convert response for calling url to pandas dataframe, begin parsing df into FBA format
    :param url: string, url
    :param r: df, response from url call
    :param args: dictionary, arguments specified when running
        flowbyactivity.py ('year' and 'source')
    :return: pandas dataframe of original source data
    """

    df_raw_data_two = pd.io.excel.read_excel(io.BytesIO(r.content), sheet_name='T1')

    df_data_1 = pd.DataFrame(df_raw_data_two.loc[6:10]).reindex()
    df_data_1 = df_data_1.reset_index()
    del df_data_1["index"]

    df_data_2 = pd.DataFrame(df_raw_data_two.loc[15:19]).reindex()
    df_data_2 = df_data_2.reset_index()
    del df_data_2["index"]

    if len(df_data_1.columns) > 12:
        for x in range(12, len(df_data_1.columns)):
            col_name = "Unnamed: " + str(x)
            del df_data_1[col_name]
            del df_data_2[col_name]

    if len(df_data_1. columns) == 12:
        df_data_1.columns = ["Production", "space_7", "space_1", "year_1", "space_2", "year_2", "space_3",
                             "year_3", "space_4", "year_4", "space_5", "year_5"]
        df_data_2.columns = ["Production", "space_7", "space_1", "year_1", "space_2", "year_2", "space_3",
                             "year_3", "space_4", "year_4", "space_5", "year_5"]

    col_to_use = ["Production"]
    col_to_use.append(usgs_myb_year(SPAN_YEARS, args["year"]))
    for col in df_data_1.columns:
        if col not in col_to_use:
            del df_data_1[col]
            del df_data_2[col]

    frames = [df_data_1, df_data_2]
    df_data = pd.concat(frames)
    df_data = df_data.reset_index()
    del df_data["index"]

    return df_data


def usgs_sgi_parse(dataframe_list, args):
    """
    Combine, parse, and format the provided dataframes
    :param dataframe_list: list of dataframes to concat and format
    :param args: dictionary, used to run flowbyactivity.py
        ('year' and 'source')
    :return: df, parsed and partially formatted to flowbyactivity
        specifications
    """
    data = {}
    row_to_use = ["Quantity", "Total"]
    dataframe = pd.DataFrame()
    for df in dataframe_list:

        for index, row in df.iterrows():
            if df.iloc[index]["Production"].strip() == "Sold or used:":
                prod = "production"
            elif df.iloc[index]["Production"].strip() == "Imports for consumption:":
                prod = "imports"
            elif df.iloc[index]["Production"].strip() == "Exports:":
                prod = "exports"
            if df.iloc[index]["Production"].strip() in row_to_use:
                remove_digits = str.maketrans('', '', digits)
                product = df.iloc[index]["Production"].strip().translate(remove_digits)
                data = usgs_myb_static_varaibles()
                data["SourceName"] = args["source"]
                data["Year"] = str(args["year"])
                data["Unit"] = "Thousand Metric Tons"
                col_name = usgs_myb_year(SPAN_YEARS, args["year"])
                data["Description"] = "Sand Gravel Industrial"
                data["ActivityProducedBy"] = "Sand Gravel Industrial"
                data['FlowName'] = "Sand Gravel Industrial " + prod
                data["FlowAmount"] = str(df.iloc[index][col_name])
                dataframe = dataframe.append(data, ignore_index=True)
                dataframe = assign_fips_location_system(dataframe, str(args["year"]))
    return dataframe

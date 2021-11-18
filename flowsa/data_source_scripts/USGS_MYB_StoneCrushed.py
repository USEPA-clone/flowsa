# USGS_MYB_Stone_Crushed.py (flowsa)
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

SourceName: USGS_MYB_Stone_Crushed
https://www.usgs.gov/centers/nmic/dimension-stone-statistics-and-information

Minerals Yearbook, xls file, tab T10:

Data for:
Stone; Stone (crushed)

Years = 2013+
"""
import io
import pandas as pd
from flowsa.flowbyfunctions import assign_fips_location_system
from flowsa.data_source_scripts.USGS_MYB_Common import *

SPAN_YEARS = "2013-2017"


def usgs_stonecr_url_helper(build_url, config, args):
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


def usgs_stonecr_call(url, r, args):
    """
    Convert response for calling url to pandas dataframe, begin parsing df into FBA format
    :param url: string, url
    :param r: df, response from url call
    :param args: dictionary, arguments specified when running
        flowbyactivity.py ('year' and 'source')
    :return: pandas dataframe of original source data
    """
    df_raw_data_two = pd.io.excel.read_excel(io.BytesIO(r.content), sheet_name='T1')

    df_data_1 = pd.DataFrame(df_raw_data_two.loc[5:15]).reindex()
    df_data_1 = df_data_1.reset_index()
    del df_data_1["index"]

    if len(df_data_1.columns) > 11:
        for x in range(11, len(df_data_1.columns)):
            col_name = "Unnamed: " + str(x)
            del df_data_1[col_name]

    if len(df_data_1. columns) == 11:
        df_data_1.columns = ["Production", "space_1", "year_1", "space_2", "year_2", "space_3",
                             "year_3", "space_4", "year_4", "space_5", "year_5"]

    col_to_use = ["Production"]
    col_to_use.append(usgs_myb_year(SPAN_YEARS, args["year"]))
    for col in df_data_1.columns:
        if col not in col_to_use:
            del df_data_1[col]

    return df_data_1


def usgs_stonecr_parse(dataframe_list, args):
    """
    Combine, parse, and format the provided dataframes
    :param dataframe_list: list of dataframes to concat and format
    :param args: dictionary, used to run flowbyactivity.py
        ('year' and 'source')
    :return: df, parsed and partially formatted to flowbyactivity
        specifications
    """
    data = {}
    row_to_use = ["Quantity"]
    dataframe = pd.DataFrame()
    for df in dataframe_list:
        for index, row in df.iterrows():
            if df.iloc[index]["Production"].strip() == "Sold or used by producers:2":
                prod = "production"
            elif df.iloc[index]["Production"].strip() == "Imports for consumption:3":
                prod = "imports"
            elif df.iloc[index]["Production"].strip() == "Exports:":
                prod = "exports"
            elif df.iloc[index]["Production"].strip() == "Recycle:":
                prod = "recycle"
            if df.iloc[index]["Production"].strip() in row_to_use:
                remove_digits = str.maketrans('', '', digits)
                product = df.iloc[index]["Production"].strip().translate(remove_digits)
                data = usgs_myb_static_varaibles()
                data["SourceName"] = args["source"]
                data["Year"] = str(args["year"])
                data["Unit"] = "Thousand Metric Tons"
                col_name = usgs_myb_year(SPAN_YEARS, args["year"])
                data["Description"] = "Stone Crushed"
                data["ActivityProducedBy"] = "Stone Crushed"
                data['FlowName'] = "Stone Crushed " + prod
                data["FlowAmount"] = str(df.iloc[index][col_name])
                if prod != "recycle":
                    dataframe = dataframe.append(data, ignore_index=True)
                    dataframe = assign_fips_location_system(dataframe, str(args["year"]))
    return dataframe

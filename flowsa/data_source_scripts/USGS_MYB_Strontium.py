# USGS_MYB_Strontium.py (flowsa)
# !/usr/bin/env python3
# coding=utf-8

import io
from flowsa.flowbyfunctions import assign_fips_location_system
from flowsa.data_source_scripts.USGS_MYB_Common import *


"""
Projects
/
FLOWSA
/

FLOWSA-314

Import USGS Mineral Yearbook data

Description

Table T1

SourceName: USGS_MYB_Strontium
https://www.usgs.gov/centers/nmic/strontium-statistics-and-information

Minerals Yearbook, xls file, tab T1

Data for: Strontium; Celestite Strontium; Strontium compounds

Years = 2014+
"""
SPAN_YEARS = "2014-2018"


def usgs_strontium_url_helper(build_url, config, args):
    """Used to substitute in components of usgs urls"""
    url = build_url
    return [url]


def usgs_strontium_call(url, usgs_response, args):
    """TODO."""
    df_raw_data = pd.io.excel.read_excel(io.BytesIO(usgs_response.content), sheet_name='T1')# .dropna()
    df_data = pd.DataFrame(df_raw_data.loc[6:13]).reindex()
    df_data = df_data.reset_index()
    del df_data["index"]

    if len(df_data.columns) > 11:
        for x in range(11, len(df_data.columns)):
            col_name = "Unnamed: " + str(x)
            del df_data[col_name]


    if len(df_data. columns) == 11:
        df_data.columns = ["Production", "space_1", "year_1", "space_2", "year_2", "space_3",
                           "year_3", "space_4", "year_4", "space_5", "year_5"]

    col_to_use = ["Production"]
    col_to_use.append(usgs_myb_year(SPAN_YEARS, args["year"]))
    for col in df_data.columns:
        if col not in col_to_use:
            del df_data[col]

    return df_data


def usgs_strontium_parse(dataframe_list, args):
    """Parsing the USGS data into flowbyactivity format."""
    data = {}
    row_to_use = ["Production, strontium minerals", "Strontium compounds3", "Celestite4", "Strontium carbonate"]
    prod = ""
    name = usgs_myb_name(args["source"])
    des = name
    dataframe = pd.DataFrame()
    col_name = usgs_myb_year(SPAN_YEARS, args["year"])
    for df in dataframe_list:
        for index, row in df.iterrows():
            if df.iloc[index]["Production"].strip() == "Imports for consumption:2":
                product = "imports"
            elif df.iloc[index]["Production"].strip() == "Production, strontium minerals":
                product = "production"
            elif df.iloc[index]["Production"].strip() == "Exports:2":
                product = "exports"



            if df.iloc[index]["Production"].strip() in row_to_use:
                data = usgs_myb_static_varaibles()
                data["SourceName"] = args["source"]
                data["Year"] = str(args["year"])
                data["Unit"] = "Metric Tons"
                if usgs_myb_remove_digits(df.iloc[index]["Production"].strip()) == "Celestite":
                    data['FlowName'] = name + " " + product + " " + usgs_myb_remove_digits(df.iloc[index]["Production"].strip())
                else:
                    data['FlowName'] = name + " " + product
                data["Description"] = usgs_myb_remove_digits(df.iloc[index]["Production"].strip())
                data["ActivityProducedBy"] = name
                col_name = usgs_myb_year(SPAN_YEARS, args["year"])
                if str(df.iloc[index][col_name]) == "--" or str(df.iloc[index][col_name]) == "(3)":
                    data["FlowAmount"] = str(0)
                else:
                    data["FlowAmount"] = str(df.iloc[index][col_name])
                dataframe = dataframe.append(data, ignore_index=True)
                dataframe = assign_fips_location_system(dataframe, str(args["year"]))
    return dataframe


import pandas as pd
import tablemaster as tm
import re
import time
import numpy as np
from datetime import datetime 
import datarecipe as dr

def sku_get_brand(sku):
    try:
        return sku[:2]
    except:
        return 'unknown'

def sku_get_model(sku):
    try:
        return sku.split("-")[1]
    except:
        return 'unknown'

def sku_get_sku_code(sku):
    try:
        return sku.split("-")[1][:2]
    except:
        return 'unknown'

def sku_get_product_line(sku, map_sku_code):
    miss_info = ''
    sku_code = sku_get_sku_code(sku)
    try:
        product_line = map_sku_code.loc[map_sku_code['code']==sku_code, 'product_line'].iloc[0]
    except:
        product_line = ""
        miss_info = f'product line of {sku} not found, please update!'
    return product_line, miss_info

def sku_get_product_type(sku, map_sku_code):
    miss_info = ''
    sku_code = sku_get_sku_code(sku)
    try:
        product_type = map_sku_code.loc[map_sku_code['code']==sku_code, 'product_type'].iloc[0]
    except:
        product_type = ""
        miss_info = f'product type of {sku} not found, please update!'
    return product_type, miss_info

def sku_get_scu(sku, map_scu):
    try:
        if(sku in map_scu['SKU'].astype(str).to_list()):
            scu = map_scu.loc[map_scu['SKU']==sku, 'SCU'].iloc[0]
        else:
            scu = sku_get_model(sku)
        return scu
    except:
        return 'unknown'

def sku_get_app_product(sku, map_app_product):
    try:
        if(sku in map_app_product['Smart Products List'].astype(str).to_list()):
            return "Y"
        else:
            return "N"
    except:
        return 'unknown'
    
def sku_get_series(sku, map_series):
    miss_info = ''
    model = sku_get_model(sku)
    try:
        series = map_series.loc[map_series['Model']==model, 'Series'].iloc[0]
    except:
        series = ""
        miss_info = f'series of {sku} not found, please update!'
    return series, miss_info

def get_sku_extra(df_ori, fields, return_miss=False,service_account_path=None):
    if fields == 'all':
        print('total fields...')
        fields_list = ['brand','product_line','product_type','sku_code','model', 'scu', 'connected', 'series']
    else:
        fields_list = fields
    df = df_ori.copy()
    print('loading mapping info...')
    if "product_line" in fields_list or "product_type" in fields_list :
        if service_account_path:
            df_map_sku_code = tm.gs_read_df(('Datalibro Mapping Master', 'sku_code'),service_account_path)
        else:
            df_map_sku_code = tm.gs_read_df(('Datalibro Mapping Master', 'sku_code'))
        if "product_line" in fields_list:
            df["product_line"], list_miss_product_line = zip(*df['sku'].apply(sku_get_product_line, map_sku_code = df_map_sku_code))
        if "product_type" in fields_list:
            df["product_type"], list_miss_product_type = zip(*df['sku'].apply(sku_get_product_type, map_sku_code = df_map_sku_code))
    if "scu" in fields_list:
        if service_account_path:
            df_map_scu = tm.gs_read_df(('Datalibro Mapping Master', 'scu'),service_account_path)
        else:
            df_map_scu = tm.gs_read_df(('Datalibro Mapping Master', 'scu'))
        df['scu'] = df['sku'].apply(sku_get_scu, map_scu=df_map_scu)
    if "series" in fields_list:
        if service_account_path:
            df_map_series = tm.gs_read_df(('Datalibro Mapping Master', 'series'),service_account_path)
        else:
            df_map_series = tm.gs_read_df(('Datalibro Mapping Master', 'series'))
        df['series'], list_miss_series = zip(*df['sku'].apply(sku_get_series, map_series=df_map_series))
        df['series'] = df['series'].apply(lambda x: 'Infinity' if x == np.inf or x == -np.inf else x)
    if "brand" in fields_list:
        df['brand'] = df['sku'].apply(sku_get_brand)
    if ("model" in fields_list) | ("connected" in fields_list):
        df['model'] = df['sku'].apply(sku_get_model)

        # 检验是否有新增支持APP的model
        sql = 'select distinct model from bi_app_dev_stats_di'
        try:
            app_data = dr.sql_query('cfg.yaml', 'saas_internal', sql)
        except Exception as e:
            print(f'Error: {e}')
            print('Try to use saas_external')
            app_data = dr.sql_query('cfg.yaml', 'saas_external', sql)
        model_list = app_data['model'].str[2:]

        try: 
            app_supported_models = dr.fetch_table_data('cfg.yaml', 'common_internal', 'map_all_app_supported_model')
        except Exception as e:
            print(f'Error: {e}')
            print('Try to use common_external')
            app_supported_models = dr.fetch_table_data('cfg.yaml', 'common_external', 'map_all_app_supported_model')
        add_model = model_list[~model_list.isin(app_supported_models['model'])].reset_index(drop=True)
        add_model = pd.DataFrame(add_model, columns=['model'])
        if add_model.empty:
            pass
        else:
            print(f'检测到新增 connected model:\n{add_model}')
            try:
                dr.update_data(add_model, 'cfg.yaml', 'common_internal', 'map_all_app_supported_model', add_data=True)
            except Exception as e:
                print(f'Error: {e}')
                print('Try to use common_external')
                dr.update_data(add_model, 'cfg.yaml', 'common_external', 'map_all_app_supported_model', add_data=True)
        # 映射 connected 字段
        try:
            app_supported_models = dr.fetch_table_data('cfg.yaml', 'common_internal', 'map_all_app_supported_model')
        except Exception as e:
            print(f'Error: {e}')
            print('Try to use common_external')
            app_supported_models = dr.fetch_table_data('cfg.yaml', 'common_external', 'map_all_app_supported_model')
        if app_supported_models.empty: # type: ignore
            raise ValueError("No data found in bi_app_dev")
        else:
            df['connected'] = df['model'].apply(lambda x: 'Y' if x in app_supported_models['model'].values else 'N')  # type: ignore
    if "sku_code" in fields_list:
        df['sku_code'] = df['sku'].apply(sku_get_sku_code)

    if return_miss:
        list_miss = pd.concat([pd.Series(list_miss_product_line), pd.Series(list_miss_product_type), pd.Series(list_miss_series)]).unique()
        return df, list_miss
    else:
        return df

def amz_merge(raw_df, merge_col=['all'], need_missing_info = False, date_col=None, country_col=None, store_id_col=None, asin_col=None, msku_col=None, sku_col=None, scu_col=None, end_date=None):
    df = raw_df.copy()
    # 修改列名
    if date_col:
        df.rename(columns={date_col:'date_col'}, inplace=True)
        date_col = 'date_col'
    if country_col:
        df.rename(columns={country_col:'country_col'}, inplace=True)
        country_col = 'country_col'
    if store_id_col:
        df.rename(columns={store_id_col:'store_id_col'}, inplace=True)
        store_id_col = 'store_id_col'
    if asin_col:
        df.rename(columns={asin_col:'asin_col'}, inplace=True)
        asin_col = 'asin_col'
    if msku_col:
        df.rename(columns={msku_col:'msku_col'}, inplace=True)
        msku_col = 'msku_col'
    if sku_col:
        df.rename(columns={sku_col:'sku_col'}, inplace=True)
        sku_col = 'sku_col'
    if scu_col:
        df.rename(columns={scu_col:'scu_col'}, inplace=True)
        scu_col = 'scu_col'

    # 读取飞书映射表
    feishu_sheet = ('NPeWsHetvhIV7ft6QfBcEEq5nqb', 'WCwfoy!A:S')
    max_retries = 5
    delay = 3
    datalibro_amazon_mapping=pd.DataFrame()
    for _ in range(max_retries):
        try:
            datalibro_amazon_mapping = tm.fs_read_df(feishu_sheet, tm.cfg.lark_awd)
            break
        except:
            if _ < max_retries - 1:  # Don't sleep after the last try
                time.sleep(delay)
        
    # Data cleaning——删除空白行
    datalibro_amazon_mapping.dropna(how='all', inplace=True)
    # Data cleaning——去除单元格多余空格
    for col in datalibro_amazon_mapping.columns:
        if datalibro_amazon_mapping[col].dtype == "object":
            datalibro_amazon_mapping[col] = datalibro_amazon_mapping[col].str.strip()
    if len(datalibro_amazon_mapping) == 0:
            raise KeyError('No mapping table is requested, please check your cfg file')
    # Data cleaning——转换数据类型
    datalibro_amazon_mapping['change_date'] = pd.to_datetime(datalibro_amazon_mapping['change_date'])
    # Data cleaning——若为中文国家字段修改为数据库中标准格式
    if country_col:
        def is_contains_chinese(str):
            if str is not None:
                for ch in str:
                    if u'\u4e00' <= ch <= u'\u9fff':
                        return True
            return False

        if datalibro_amazon_mapping['country'].apply(is_contains_chinese).any():
            sql_query = 'SELECT * FROM map_all_country_list'
            try:
                map_all_country_list = tm.query(sql_query, tm.cfg.common_internal)
            except Exception as e:
                print(f'Error: {e}')
                print('Try to use common_external')
                map_all_country_list = tm.query(sql_query, tm.cfg.common_external)
            datalibro_amazon_mapping = datalibro_amazon_mapping.rename(columns = {country_col:'country_chinese'})
            datalibro_amazon_mapping = datalibro_amazon_mapping.merge(map_all_country_list, on='country_chinese', how='left')
            datalibro_amazon_mapping = datalibro_amazon_mapping.drop(['country_chinese'], axis=1)
            datalibro_amazon_mapping = datalibro_amazon_mapping.rename(columns = {'country_capital':'country'})

    # Data cleaning——重复映射的数据删除
    key_columns = ['change_date', 'country', 'store_id', 'asin', 'msku', 'sku', 'scu']
    key = [col for col, flag in zip(key_columns, [date_col, country_col, store_id_col, asin_col, msku_col, sku_col, scu_col]) if flag]
    datalibro_amazon_mapping = datalibro_amazon_mapping.drop_duplicates(subset=key, keep='last')
    if date_col:
        key.remove('change_date')

    if merge_col[0] == 'all':
        merge_col = list(set(datalibro_amazon_mapping.columns) - set(key)- {'备注', '数据是否重复', '辅助列'})
    # 删除已有映射列
    for res_col in merge_col:
        if res_col in df.columns:
            df.drop(columns=res_col, inplace=True)

    # 缺失键则不进行映射
    if len(key) == 0:
        raise ValueError('The data frame must has at least on key')
    # 创建信息映射键
    keys = ['date', 'country', 'store_id', 'asin', 'msku', 'sku', 'scu']
    if not date_col:
        keys.remove('date')
    args =[country_col, store_id_col, asin_col, msku_col, sku_col, scu_col]
    args_names =["country", "store_id", "asin", "msku", 'sku', 'scu']
    df['left_key'] = ''
    datalibro_amazon_mapping['right_key'] = ''
    for i, arg in enumerate(args):
        if arg is None:
            keys.remove(args_names[i])
        else:
            df['left_key'] += df[arg]
            df.rename(columns={str(arg):args_names[i]}, inplace=True)
            datalibro_amazon_mapping['right_key'] += datalibro_amazon_mapping[args_names[i]]
    
    print(f"\n{datetime.now()}——Metrics used to mapping:{keys}")

    # 如有最晚日期参数则剔除范围外数据
    if end_date:
        datalibro_amazon_mapping = datalibro_amazon_mapping[datalibro_amazon_mapping['change_date'] <= end_date]

    # 检验空缺键
    def check_empty(df, map_col):
        tmp_df = df[map_col].copy()
        # 替换任意数量的空格为 np.nan
        tmp_df = tmp_df.replace(r'^\s*$', np.nan, regex=True)
        # 替换None为 np.nan
        tmp_df = tmp_df.fillna(value=np.nan)
        # 筛选含空值数据
        null_data = df[tmp_df.isnull().any(axis=1)]
        df = df[~tmp_df.isnull().any(axis=1)]
        if len(null_data) != 0:
            # 输出包含空值的行数
            print(f'存在映射键缺失的数据行数: {len(null_data)}')
        return df, null_data

    df, dirty_df = check_empty(df, key)

    # 连表映射
    if date_col:
        # 筛选出有更改记录的数据和没有更改记录的数据
        datalibro_amazon_mapping_unchanged = datalibro_amazon_mapping[pd.isnull(datalibro_amazon_mapping['change_date'])].reset_index(drop=True).copy()
        datalibro_amazon_mapping_changed = datalibro_amazon_mapping[~pd.isnull(datalibro_amazon_mapping['change_date'])].copy()

        df = df.merge(datalibro_amazon_mapping_unchanged[merge_col + key], on=key, how='left')
        if len(datalibro_amazon_mapping_changed) > 0:
            datalibro_amazon_mapping_changed.sort_values(by='change_date', inplace=True, ascending=True)
            datalibro_amazon_mapping_changed.reset_index(drop=True, inplace=True)
            for row1 in range(len(datalibro_amazon_mapping_changed)):
                for row2 in range(len(df)):
                    if (datalibro_amazon_mapping_changed.loc[row1, 'right_key'] == df.loc[row2, 'left_key']) & (df.loc[row2, date_col] > datalibro_amazon_mapping_changed.loc[row1,"change_date"]):
                        for col in merge_col:
                            df.loc[row2, col] = datalibro_amazon_mapping_changed.loc[row1, col]
    else:
        df = df.merge(datalibro_amazon_mapping[merge_col + key], on=key, how='left')

    df = pd.concat([df, dirty_df], axis=0, ignore_index=True)

    # 删除不需要的列
    df.drop(columns='left_key', inplace=True)
    df.reset_index(drop=True, inplace=True)

    # 检验空缺映射列
    def check_empty_res(df, map_col, key_col):
        tmp_df = df[map_col].copy()
        # 替换任意数量的空格为 np.nan
        tmp_df = tmp_df.replace(r'^\s*$', np.nan, regex=True)
        # 替换None为 np.nan
        tmp_df = tmp_df.fillna(value=np.nan)
        # 筛选含空值数据
        null_data = df[tmp_df.isnull().any(axis=1)]
        if len(null_data) != 0:
            # 输出包含空值的行数
            print(f'映射列存在空值行数: {len(null_data)}')
            if key_col:
                null_data = null_data[key_col+map_col].drop_duplicates()
            # 输出具有空值的行和其他列的内容
            return null_data
        else:
            print("Complete mapping, no missing mapping value")

    null_data = check_empty_res(df, merge_col, key_col = key)  
    if need_missing_info:
        return df, null_data
    else:
       return df
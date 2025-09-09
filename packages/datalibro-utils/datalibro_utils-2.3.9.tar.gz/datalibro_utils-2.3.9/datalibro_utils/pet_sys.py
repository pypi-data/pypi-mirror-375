import yaml
from yaml.loader import SafeLoader
import random
import pandas as pd

def read_yaml(yaml_name):
    with open(yaml_name) as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def store_yaml(dict_name, yaml_name):
    with open(yaml_name, 'w') as file:
            yaml.dump(dict_name, file, default_flow_style=False, allow_unicode=True)

def get_random_pet(config_path, n=2):
    config_pet = read_yaml(config_path)
    dict_pet = config_pet['pet_probability']
    prob_pets = [key for key, value_list in dict_pet.items() for _ in value_list]
    emoji_pets = [value for value_list in dict_pet.values() for value in value_list]
    chosen_pets = ''.join(random.choices(emoji_pets, weights=prob_pets, k=n))
    return chosen_pets

def get_user_daily_pets(config_path, username, day):
    config_pet = read_yaml(config_path)
    if username in config_pet['user_daily_pet']:
        if day in config_pet['user_daily_pet'][username]:
            return config_pet['user_daily_pet'][username][day]
        else:
            config_pet['user_daily_pet'][username][day] = get_random_pet(config_path)
    else:
        config_pet['user_daily_pet'][username] = {day: get_random_pet(config_path)}
    
    store_yaml(config_pet, config_path)
    return config_pet['user_daily_pet'][username][day]
            

def get_user_pets(config_path, username):
    config_pet = read_yaml(config_path)
    try:
        return config_pet['user_pets'][username]
    except:
        return ''

def add_user_pets(config_path, username, pet):
    config_pet = read_yaml(config_path)
    try:
        if pet not in config_pet['user_pets'][username]:
            config_pet['user_pets'][username] += pet
    except:
        config_pet['user_pets'][username] = pet
    store_yaml(config_pet, config_path)

def get_pets_rank(config_path):
    all_pets = read_yaml(config_path)['user_pets']
    df_rank = pd.DataFrame(pd.Series(all_pets))
    df_rank['Qty'] = df_rank[0].apply(len)
    df_rank = df_rank.sort_values('Qty', ascending=False)
    df_rank = df_rank.rename(columns={0:'Pets'})
    df_rank['Rank'] = df_rank['Qty'].rank(method='min',ascending=False).astype(int)
    df_rank['Name'] = df_rank.index
    df_rank = df_rank.set_index('Rank')
    df_rank = df_rank[['Name', 'Pets']]
    return df_rank
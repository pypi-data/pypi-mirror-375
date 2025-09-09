import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import pandas as pd
import re
import os
import shutil
from datetime import datetime
import random
from .pet_sys import get_user_daily_pets, get_user_pets, add_user_pets, get_pets_rank

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_pet_button(config_path, username, pet, key):
    try:
        user_pets = read_yaml(config_path)['user_pets'][username]
    except:
        user_pets = ''
    if st.button(pet, key=key):
        if pet in user_pets:
            st.warning(f'You already have {pet}')
        else:
            st.success(f'A new pet {pet} was caught!')
            st.snow()
            add_user_pets(config_path=config_path, username=username, pet=pet)

def refresh_file(new_file, old_file):
    if os.path.isfile(old_file):
        os.remove(old_file)
    shutil.copy(new_file, old_file)

def tablemaster_init(tmcfg_source_config, tmcfg_source_config2):
    tmcfg_local_config = './cfg.yaml'
    try:
        refresh_file(tmcfg_source_config, tmcfg_local_config)
    except:
        refresh_file(tmcfg_source_config2, tmcfg_local_config)

def read_yaml(yaml_name):
    with open(yaml_name) as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def store_yaml(dict_name, yaml_name):
    with open(yaml_name, 'w') as file:
            yaml.dump(dict_name, file, default_flow_style=False)

def make_clickable(link):
    # target _blank to open new window
    # extract clickable text to display for your link
    text = re.findall(r'db\d{3}', link)[0]
    return f'<a target="_blank" href="{link}">{text}</a>'

def print_about_datalibro(view_times, doc=None):
    print_doc = False
    with st.sidebar.expander("🦒 About Datalibro"):
        st.markdown(f'<p style="color:#6f6e6e;font-size:15px;"> Datalibro is a business intelligence tool created\
                     by the Designlibro data team that allows people to easily interact with data through the web.\
                     \n\nToday Datalibro View Times: {view_times}</p>', unsafe_allow_html=True)
        if doc != None:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Doc for this DB"):
                    print_doc = True
            with col2:
                if st.button("Hide Doc"):
                    print_doc = False
    if print_doc:
        st.markdown(doc)


def auth_init(dbcode, dbtitle, user_auth_config, db_config, pet_config, skip_auth=False, print_doc=False, layout='centered', initial_sidebar_state="auto", menu_items=None):
    # Set page config
    st.set_page_config(page_title=dbtitle, page_icon=':giraffe_face:', layout=layout, initial_sidebar_state=initial_sidebar_state, menu_items=menu_items)

    # Hide the streamlit footer
    hide_st_style = """
                    <style>
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    header {visibility: hidden;}
                    </style>
                    """
    st.markdown(hide_st_style, unsafe_allow_html=True)

    # Add Petlibro Logo
    st.image(os.path.join(BASE_DIR, 'PETLIBRO_LOGO_16-9.png'), width=160)

    # Get Docs if need to print it
    if print_doc:
        doc = read_yaml(db_config)['dashboards'][dbcode]['docs']
    else:
        doc = None

    # Read Configs
    config = read_yaml(user_auth_config)
    config_current_db = config['credentials'].copy()
    df_config_current_db = pd.DataFrame(config_current_db['usernames']).transpose()
    config_current_db['usernames'] = df_config_current_db[df_config_current_db['dbcode'].apply(lambda x: dbcode in x)].transpose().to_dict()

    # Auth
    authenticator = stauth.Authenticate(
    config_current_db,
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
    )
    today = datetime.now().strftime('%Y-%m-%d')
    if skip_auth:
        print_about_datalibro(config["view_times"][today], doc=doc)
        try:
            config['view_times'][today] += 1
        except:
            config['view_times'][today] = 0
        store_yaml(config, user_auth_config)
        return (True, 'None')
    else:


        name, authentication_status, username = authenticator.login('Sign in to Datalibro', 'main')
        if authentication_status:

            # Load pet system info
            daily_pets = get_user_daily_pets(config_path=pet_config, username=username, day=today)
            user_pets = get_user_pets(config_path=pet_config, username=username)
            st.sidebar.text('🦒' + user_pets)

            # Refresh daily views
            if dbcode in config['detail_view_times']:
                if username in config['detail_view_times'][dbcode]:
                    if today in config['detail_view_times'][dbcode][username]:
                        config['detail_view_times'][dbcode][username][today] += 1
                    else:
                        config['detail_view_times'][dbcode][username][today] = 1
                else:
                    config['detail_view_times'][dbcode][username] = {today:1}
            else:
                config['detail_view_times'][dbcode] = {username:{today:1}}

            try:
                config['view_times'][today] += 1
            except:
                config['view_times'][today] = 0

            with st.sidebar.expander("🦧 User Center"):
                st.caption(f'Welcome, **{name}**!')
                get_pet_button(config_path=pet_config, username=username, pet=daily_pets[0], key='key1')
                try:
                    if authenticator.reset_password(username, 'Reset password'):
                        st.success('Password modified successfully')
                except Exception as e:
                    st.error(e)
                authenticator.logout('Log out', key='unique_key')
                st.divider()
                st.markdown("Pets Rank!")
                st.dataframe(get_pets_rank(pet_config))

            list_user_db = list(df_config_current_db.loc[username,'dbcode'])
            df_db_info = pd.DataFrame(read_yaml(db_config)['dashboards']).transpose()
            # drop docs if there is docs
            try:
                df_db_info = df_db_info.drop('docs', axis=1)
            except:
                print('no docs for this db')
            df_db_info = df_db_info[df_db_info['dbcode'].isin(list_user_db)]
            df_db_info['link'] = df_db_info['link'].apply(make_clickable)
            df_db_info = df_db_info.drop('dbcode', axis=1).set_index('link')
            df_db_info.index.name = None
            df_db_info = df_db_info.rename(columns={'description':'Description'})
            df_db_info = df_db_info.to_html(escape=False)
        

            with st.sidebar.expander("🦋 My Dashboards"):
                get_pet_button(config_path=pet_config, username=username, pet=daily_pets[1], key='key2')
                st.write(df_db_info, unsafe_allow_html=True)

            print_about_datalibro(config["view_times"][today], doc=doc)

            config['credentials']['usernames'][username] = config_current_db['usernames'][username]
            config['credentials']['usernames'][username]['last_active_time'] = datetime.now().strftime('%Y-%m-%d %H:%M')

            store_yaml(config, user_auth_config)

            return(True, username)
        
        elif authentication_status is False:
            st.error('Username/password is incorrect')
            return (False, 'Unknown')
        elif authentication_status is None:
            st.warning('Please enter your username and password')
            return (False, 'Unknown')

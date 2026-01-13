# Import python packages
import streamlit as st
import requests
# Write directly to the app
st.title("🥤 Customize Your Smoothie!🥤")

st.write(
  """Choose the fruit you want in your custom Smoothie!
  """
)

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on the Smoothie will be:", name_on_order)

from snowflake.snowpark.functions import col


cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"), col("SEARCH_ON"))
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe.select(col("FRUIT_NAME")).to_pandas()["FRUIT_NAME"].tolist(),
    my_dataframe, max_selections=5
)
if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
      ingredients_string += fruit_chosen+' '
      st.subheader(fruit_chosen+' Nutrition Information')
      search_on_value = session.table("smoothies.public.fruit_options") \
        .filter(col("FRUIT_NAME") == fruit_chosen) \
        .select(col("SEARCH_ON")) \
        .collect()[0][0]
      smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+search_on_value)
      sf_df=st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    st.write (ingredients_string)
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """', '""" + name_on_order + """')"""

    time_to_insert=st.button('Submit Order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")

og_dataset = session.table("smoothies.public.orders")



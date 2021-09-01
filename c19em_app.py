"""Streamlit app for FOIA Explorer COVID-19 Emails"""
import streamlit as st
import pandas as pd
import altair as alt
import psycopg2
from st_aggrid import AgGrid


st.set_page_config(page_title="FOIA Explorer: COVID-19 Emails", layout="wide")
st.title("FOIA Explorer: COVID-19 Emails")


# initialize database connection - uses st.cache to only run once
@st.cache(allow_output_mutation=True,
          hash_funcs={"_thread.RLock": lambda _: None})
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

# perform query - ses st.cache to only rerun once
@st.cache
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()


conn = init_connection()
# foias = run_query("SELECT file_id, title from covid19.files order by title")


st.selectbox('FOIA', ["Fauci Emails"])
"""
The COVID-19 releated emails of Dr. Anthony Fauci, director of the National
Institute of Allergy and Infectious Diseases.
- Source: MuckRock/DocumentCloud | Contributor: Jason Leopold
- https://www.documentcloud.org/documents/20793561-leopold-nih-foia-anthony-fauci-emails
"""

""" ## Emails by Month"""
emcnts = """
select coalesce(to_char(sent,'YYYY-MM'), 'Unknown') year_month,
       count(*) emails
   from covid19.emails
   group by year_month
   order by year_month"""
cntsdf = pd.read_sql_query(emcnts, conn)
c = alt.Chart(cntsdf).mark_bar().encode(
    x='year_month',
    y='emails'
)
st.altair_chart(c, use_container_width=True)

""" ## Individual Emails """
emqry = """
select sent, subject, topic, from_email "from",
       to_emails "to", cc_emails cc, e.email_id, file_pg_start pg_number
    from covid19.emails e
       left join top_topic_emails t on (e.email_id = t.email_id)
    order by sent nulls last
"""
emdf = pd.read_sql_query(emqry, conn)
emdf['sent'] = pd.to_datetime(emdf['sent'], utc=True)
AgGrid(emdf)

"""
## About
The FOIA Explorer and associated tools were created by Columbia
Univesity's [History Lab](http://history-lab.org) under a grant from the Mellon
Foundation's [Email Archives: Building Capacity and Community]
(https://emailarchivesgrant.library.illinois.edu/blog/) program.
"""

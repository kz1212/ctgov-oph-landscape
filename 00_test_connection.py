import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
engine = create_engine(
    f"postgresql+psycopg2://{os.environ.get('AACT_USER')}:{os.environ.get('AACT_PASSWORD')}@"
    f"{os.environ.get('AACT_HOST')}:{os.environ.get('AACT_PORT', '5432')}/"
    f"{os.environ.get('AACT_DB', 'aact')}?sslmode=require"
)

pd.read_sql("SELECT COUNT(*) FROM studies;", engine)